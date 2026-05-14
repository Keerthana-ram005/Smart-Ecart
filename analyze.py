from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import logging
import os

from services.video_processor import download_video, extract_audio, extract_frames
from services.whisper_service import transcribe_audio, extract_ingredients_from_text
from services.yolo_detector import detect_ingredients_from_frames
from services.ocr_service import extract_text_from_frames, extract_ingredients_from_ocr
from services.ingredient_fusion import fuse_ingredients
from services.summarizer import generate_summary
from services.nlp_ner_service import extract_exact_ingredients

logger = logging.getLogger(__name__)
router = APIRouter()

class AnalyzeRequest(BaseModel):
    url: str

@router.post("/analyze")
async def analyze_video(request: AnalyzeRequest):
    try:
        # Initial validation
        if not request.url or ("youtube.com" not in request.url and "youtu.be" not in request.url):
            raise HTTPException(status_code=400, detail="Invalid YouTube URL provided")
            
        # 1. Download Video
        try:
            video_path, description = download_video(request.url)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Download failure: {str(e)}")
            
        # 2. Extract Audio
        try:
            audio_path = extract_audio(video_path)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Audio extraction failure: {str(e)}")
            
        # 3. Extract Frames
        try:
            frame_paths = extract_frames(video_path)
        except Exception as e:
            logger.warning(f"Frame extraction failed: {str(e)}")
            frame_paths = []
            
        # 4. Vision
        ingredients_from_vision = []
        try:
            ingredients_from_vision = detect_ingredients_from_frames(frame_paths)
        except Exception as e:
            logger.error(f"YOLO vision processing failed: {str(e)}")
            pass

        # 5. OCR
        ingredients_from_ocr = []
        try:
            ocr_text_list = extract_text_from_frames(frame_paths)
            if ocr_text_list:
                ingredients_from_ocr = extract_ingredients_from_ocr(ocr_text_list)
        except Exception as e:
            logger.error(f"OCR processing failed: {str(e)}")
            pass

        # 6. Audio Transcription
        transcript = ""
        ingredients_from_audio = []
        try:
            transcript = transcribe_audio(audio_path)
            if transcript:
                ingredients_from_audio = extract_ingredients_from_text(transcript)
        except Exception as e:
            logger.error(f"Whisper processing failed: {str(e)}")
            pass

        # 6.5 NLP Description Scraping (Highest fidelity source if present)
        ingredients_from_desc = []
        try:
            if description:
                # 1. First, attempt to parse pristine description lists (e.g. "Eggs - 2", "Milk: 1 cup")
                import re
                for line in description.split('\n'):
                    line = line.strip()
                    # Match formatted lists like "Onion (chopped) - 1/4 cup" or "Eggs -- 2"
                    match = re.match(r'^([a-zA-Z\s\(\)]+?)\s*[-\u2013\u2014:]+\s*(.*?)$', line)
                    if match:
                        ing = match.group(1).strip()
                        qty = match.group(2).strip()
                        # Basic noise filter (must not be a link or massive sentence)
                        if len(ing) > 2 and len(ing) < 30 and len(qty) < 30 and "http" not in line and "www" not in line:
                            ingredients_from_desc.append({"name": ing.lower(), "quantity": qty, "source": "desc_explicit"})
                
                # 2. Add NER parsing for unstructured description paragraphs
                ner_desc = extract_exact_ingredients(description, source="description")
                
                # Merge unique items
                seen_desc = {item["name"] for item in ingredients_from_desc}
                for item in ner_desc:
                    if item["name"] not in seen_desc:
                        ingredients_from_desc.append(item)
                        seen_desc.add(item["name"])

        except Exception as e:
            logger.error(f"Description processing failed: {str(e)}")
            pass

        # 7. Fuse Ingredients
        final_ingredients = []
        try:
            # We append the extracted description directly to the audio list since it represents ground-truth textual context
            combined_context = ingredients_from_audio + ingredients_from_desc
            final_ingredients = fuse_ingredients(
                audio_list=combined_context,
                vision_list=ingredients_from_vision,
                ocr_list=ingredients_from_ocr
            )
        except Exception as e:
            logger.error(f"Ingredient fusion failed: {str(e)}")
            pass
            
        # 8. Generate NLP Summary
        summary = "No audio context found."
        try:
            if transcript:
                summary = generate_summary(transcript)
        except Exception as e:
            logger.error(f"Summary generation failed: {str(e)}")
            pass

        # Final Payload Structure
        return {
            "ingredients": final_ingredients,
            "summary": summary,
            "transcript": transcript,
            "language_detected": "auto",
            "message": "Processing complete"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")

import whisper
import logging
from .nlp_ner_service import extract_exact_ingredients

logger = logging.getLogger(__name__)

def transcribe_audio(audio_path: str) -> str:
    logger.info("Transcribing audio...")
    try:
        model = whisper.load_model("base")
        # task="translate" forces Whisper to directly output the transcript in English regardless of the spoken source language
        result = model.transcribe(audio_path, task="translate")
        return result["text"]
    except Exception as e:
        logger.error(f"Failed to transcribe audio: {e}")
        return ""

def extract_ingredients_from_text(text: str) -> list[dict]:
    logger.info("Extracting exact ingredients from speech using NER Model...")
    if not text:
        return []

    # Strip excessive newlines/spaces
    text_clean = text.replace('\n', ' ').strip()
    logger.info(f"Cleaned Whisper transcript: {text_clean[:200]}...")
    
    # Hand off entire extraction sequence to our AI NER Model!
    final_list = extract_exact_ingredients(text_clean, source="whisper")
    
    return final_list

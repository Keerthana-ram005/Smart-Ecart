import pytesseract
import cv2
import logging
import os
import shutil
from .nlp_ner_service import extract_exact_ingredients

logger = logging.getLogger(__name__)

# Configure Tesseract path
requested_path = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
if os.path.exists(requested_path):
    pytesseract.pytesseract.tesseract_cmd = requested_path
else:
    sys_path = shutil.which("tesseract")
    if sys_path:
        pytesseract.pytesseract.tesseract_cmd = sys_path

def preprocess_image(image_path: str):
    img = cv2.imread(image_path)
    if img is None:
        return None
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    _, thresh = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY)
    return thresh

def extract_text_from_frames(frame_paths: list[str]) -> list[str]:
    logger.info("Running OCR on frames...")
    if not frame_paths: return []
    
    # Dramatically increase sample rate to ensure brief textual panels aren't missed
    if len(frame_paths) > 40:
        frame_paths = frame_paths[::len(frame_paths)//40][:40]
        
    all_text = []
    for path in frame_paths:
        try:
            processed_img = preprocess_image(path)
            if processed_img is not None:
                text = pytesseract.image_to_string(processed_img, config='--psm 6')
                for line in text.split('\n'):
                    cleaned_line = line.strip()
                    if cleaned_line:
                        all_text.append(cleaned_line)
        except Exception as e:
            logger.warning(f"OCR failed for frame {path}: {str(e)}")
    return all_text

def extract_ingredients_from_ocr(text_list: list[str]) -> list[dict]:
    logger.info("Evaluating extracted OCR lines against AI NER Model...")
    
    # We combine the sequential OCR reads into one blob context so the model can read it fluidly
    blob_context = " ".join(text_list)
    
    final_list = extract_exact_ingredients(blob_context, source="ocr")
            
    return final_list

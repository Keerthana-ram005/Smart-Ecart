import logging
from transformers import pipeline
import re

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

try:
    logger.info("Loading SOTA Recipe NER Token Classifier...")
    # Dizex InstaFoodRoBERTa-NER is specifically tailored for pinpointing exact FOOD structures flawlessly.
    ner_pipeline = pipeline("ner", model="Dizex/InstaFoodRoBERTa-NER", aggregation_strategy="simple")
except Exception as e:
    logger.error(f"Failed to load NER model: {str(e)}")
    ner_pipeline = None

def extract_exact_ingredients(text: str, source: str = "nlp") -> list[dict]:
    """Uses Hugging Face Food-NER to extract exact ingredients dynamically."""
    if not text or not ner_pipeline:
        return []
        
    try:
        results = ner_pipeline(text)
        
        ingredients = []
        # Quantities Regex (retained backward compatibility for measurement extraction)
        UNITS_PATTERN = r"(?:cup|cups|tablespoon|tablespoons|tbsp|teaspoon|teaspoons|tsp|gram|grams|g|kg|ml|l|pinch|dash|clove|cloves|slice|slices)"
        QTY_PATTERN = rf"(\d+(?:/\d+|\.\d+)?\s*{UNITS_PATTERN}?|\bto taste\b|some|a little|a pinch of|a dash of|half a)"

        for entity in results:
            if entity.get("entity_group") == "FOOD":
                word = entity.get("word", "").strip().lower()
                
                # Sanitize typical tokenizer subword hashes
                word = word.replace("#", "")
                word = word.replace(' \'', '\'')
                
                # Strict noise filter to prevent broken OCR pieces or Whisper hallucinations
                if len(word) <= 2 or not word.isalpha() and ' ' not in word:
                    # Ignore single letters, "zz", and punctuation blocks
                    continue
                    
                # Look for matching quantities appearing directly before the found item
                matched_qty = "approx"
                safe_word_regex = re.escape(word)
                pattern = rf"\b({QTY_PATTERN}(?:\s+of)?\s+)?{safe_word_regex}\b"
                qty_match = re.search(pattern, text.lower())
                
                if qty_match and qty_match.group(1):
                    matched_qty = qty_match.group(1).strip()
                
                ingredients.append({
                    "name": word,
                    "quantity": matched_qty,
                    "source": source
                })
                
        # Deduplication mapping
        deduped = {}
        for item in ingredients:
            n = item["name"]
            if n not in deduped or (item["quantity"] != "approx" and deduped[n]["quantity"] == "approx"):
                deduped[n] = item
                
        final_list = list(deduped.values())
        logger.info(f"NER Extract ({source}): {final_list}")
        return final_list

    except Exception as e:
        logger.error(f"Error during NER parse sequence: {str(e)}")
        return []

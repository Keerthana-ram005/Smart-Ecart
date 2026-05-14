import logging
from utils.ingredient_list import normalize_ingredient_name

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def fuse_ingredients(audio_list, vision_list, ocr_list):
    logger.info("Fusing ingredients dynamically with scoring system...")
    
    # Dictionary tracked by normalized name
    fused_map = {}
    
    def process_list(items, source, points):
        for item in items:
            name = item["name"] # already normalized by origin service
            qty = item.get("quantity")
            
            if name not in fused_map:
                fused_map[name] = {"score": 0, "quantities": {}}
                
            fused_map[name]["score"] += points
            
            # Map valid quantities to their source
            if qty and qty != "approx" and qty != "some" and not str(qty).startswith("detected"):
                if source not in fused_map[name]["quantities"]:
                    fused_map[name]["quantities"][source] = qty
                    
    # Points allocation strategy to aggressively filter out noise
    # Whisper (+2), OCR (+1), YOLO (+0.5)
    process_list(audio_list, "whisper", 2.0)
    process_list(ocr_list, "ocr", 1.0)
    process_list(vision_list, "yolo", 0.5)

    final_list = []
    
    for name, data in fused_map.items():
        # Print Debug Log exactly as requested
        logger.info(f"Ingredient Evaulation -> Name: {name}, Current Score: {data['score']}")
        
    # Validation: Keep only ingredients with score >= 2 
        # However, for 'Tasty' style videos (music only, no speech), Whisper will be empty.
        # We dynamically lower threshold to 1.0 (OCR weight) if there's zero audio context.
        dynamic_threshold = 2.0 if audio_list else 1.0
        
        if data["score"] >= dynamic_threshold:
            
            # Quantity assignment priority: 1. OCR, 2. Whisper, 3. Default "approx"
            qty = "approx"
            if "ocr" in data["quantities"] and data["quantities"]["ocr"]:
                qty = data["quantities"]["ocr"]
            elif "whisper" in data["quantities"] and data["quantities"]["whisper"]:
                qty = data["quantities"]["whisper"]
                
            final_list.append({"name": name, "quantity": qty})
            
    # Print Final Log
    logger.info(f"Final filtered list: {[i['name'] for i in final_list]}")
    return final_list

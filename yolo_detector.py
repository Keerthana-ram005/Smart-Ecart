from ultralytics import YOLO
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

try:
    logger.info("Loading YOLOv8n model...")
    model = YOLO("yolov8n.pt")
except Exception as e:
    logger.error(f"Failed to load YOLO model: {e}")
    model = None

# A basic generic set of likely food objects found natively in COCO 80 list
# We loosen this because our NLP model is now perfectly accurate.
COCO_FOOD_CLASSES = {
    "banana", "apple", "sandwich", "orange", "broccoli", 
    "carrot", "hot dog", "pizza", "donut", "cake", 
    "bowl", "cup"
}

def detect_ingredients_from_frames(frame_paths: list[str]) -> list[dict]:
    logger.info("Running YOLO on frames...")
    
    if not model or not frame_paths:
        return []
        
    detected_objects = {}
    if len(frame_paths) > 20:
        step = len(frame_paths) // 20
        frame_paths = frame_paths[::step][:20]

    try:
        results = model(frame_paths, stream=True, verbose=False)
        for r in results:
            for box in r.boxes:
                cls_id = int(box.cls[0])
                conf = float(box.conf[0])
                label = model.names[cls_id].lower()
                
                # Check against broad COCO food classes
                if label in COCO_FOOD_CLASSES:
                    if label not in detected_objects or conf > detected_objects[label]:
                        detected_objects[label] = conf
                        
        final_list = [
            {"name": name, "confidence": round(conf, 2), "source": "yolo"} 
            for name, conf in detected_objects.items()
        ]
        
        logger.info(f"YOLO Detected objects: {[item['name'] for item in final_list]}")
        return final_list
        
    except Exception as e:
        logger.error(f"Error during YOLO detection: {str(e)}")
        return []

from ultralytics import YOLO
import cv2
import os
from pathlib import Path
import easyocr
import requests
import time
from datetime import datetime
from pymongo import MongoClient


def process_image(image_path, output_dir="outputs", confidence=0.25):
    """Process a single image for helmet detection and return detection data"""

    # Create output directory
    os.makedirs(output_dir, exist_ok=True)

    # Initialize EasyOCR reader
    reader = easyocr.Reader(['en'])

    # Load the trained model (or use pre-trained if not found)
    model_path = "runs/detect/helmet_detection/weights/best.pt"
    if os.path.exists(model_path):
        model = YOLO(model_path)
    else:
        model = YOLO("yolov8n.pt")

    img = cv2.imread(image_path)
    results = model(image_path, conf=confidence)

    detection_data = {
        "timestamp": datetime.now().isoformat(),
        "image_path": image_path,
        "detections": []
    }

    for result in results:
        output_path = os.path.join(output_dir, f"helmet_detection_{Path(image_path).stem}.jpg")
        result.save(filename=output_path)
        detection_data["image_path"] = output_path

        boxes = result.boxes

        if boxes is not None and len(boxes) > 0:
            for box in boxes:
                cls = int(box.cls.item())
                conf = box.conf.item()
                class_name = result.names[cls]

                det = {
                    "class": class_name,
                    "confidence": conf
                }

                # OCR if license plate detected
                if class_name.lower() in ["vehicle_registration_plate", "license_plate", "number_plate"]:
                    xyxy = box.xyxy[0].cpu().numpy().astype(int)
                    x1, y1, x2, y2 = xyxy
                    cropped_plate = img[y1:y2, x1:x2]
                    ocr_result = reader.readtext(cropped_plate)
                    plate_text = " ".join([res[1] for res in ocr_result]) if ocr_result else "N/A"
                    det["plate_text"] = plate_text

                detection_data["detections"].append(det)

    return detection_data


def send_detection_to_flask(detection_data, vehicle_no=None):
    payload = {
        "source": "web_upload",
        "timestamp": time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
        "detection": detection_data,
        "vehicle_no": vehicle_no,
        "image_path": detection_data.get('image_path')
    }
    try:
        r = requests.post("http://localhost:5000/detect", json=payload, timeout=5)
        return r.json()
    except Exception as e:
        print(f"❌ Failed to send to Flask: {e}")
        return {"status": "error", "message": str(e)}

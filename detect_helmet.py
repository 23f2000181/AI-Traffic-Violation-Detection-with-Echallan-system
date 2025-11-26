from ultralytics import YOLO
import cv2
import os
from pathlib import Path
import easyocr
import requests
import time
from datetime import datetime
from pymongo import MongoClient


def detect_helmets(image_path=None, video_path=None, output_dir="outputs", confidence=0.25):
    """Detect helmets in images or videos using trained YOLO model"""

    # Create output directory
    os.makedirs(output_dir, exist_ok=True)

    # Initialize EasyOCR reader
    reader = easyocr.Reader(['en'])

    # Initialize MongoDB client
    client = MongoClient("mongodb://localhost:27018/")
    db = client["helmet_detection_db"]
    collection = db["detections"]

    # Load the trained model (or use pre-trained if not found)
    model_path = "D:/Codes/Miniproj/runs/detect/helmet_detection/weights/best.pt"
    if os.path.exists(model_path):
        print(f"📱 Loading trained model: {model_path}")
        model = YOLO(model_path)
    else:
        print("⚠️  Trained model not found, using pre-trained YOLOv8n")
        model = YOLO("yolov8n.pt")

    def send_detection_to_flask(detection_data, vehicle_no=None):
        payload = {
            "source": "camera_1",
            "timestamp": time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
            "detection": detection_data,
            "vehicle_no": vehicle_no,
            "image_path": detection_data.get('image_path')
        }
        try:
            r = requests.post("http://localhost:5000/detect", json=payload, timeout=5)
            print(f"📤 Sent detection to Flask: {r.json()}")
        except Exception as e:
            print(f"❌ Failed to send to Flask: {e}")

    # ✅ COLLECT ALL DETECTIONS TO RETURN
    all_detections = []

    # Process image
    if image_path:
        print(f"🖼️  Processing image: {image_path}")

        img = cv2.imread(image_path)
        results = model(image_path, conf=confidence)  # Lowered confidence

        for i, result in enumerate(results):
            output_path = os.path.join(output_dir, f"helmet_detection_{Path(image_path).stem}.jpg")
            result.save(filename=output_path)
            print(f"✅ Detection saved to: {output_path}")

            detection_data = {
                "timestamp": datetime.now().isoformat(),
                "image_path": output_path,
                "detections": []
            }

            boxes = result.boxes
            print(f"🧠 Model classes: {result.names}")
            print(f"📦 Raw detection data:\n{result.boxes.data}")

            if boxes is not None and len(boxes) > 0:
                print(f"📊 Found {len(boxes)} objects:")
                for j, box in enumerate(boxes):
                    cls = int(box.cls.item())
                    conf = box.conf.item()
                    class_name = result.names[cls]
                    bbox = box.xyxy[0].cpu().numpy().astype(int).tolist()
                    print(f"   - {class_name}: {conf:.2f} confidence")

                    # OCR if license plate detected
                    if class_name.lower() in ["vehicle_registration_plate", "license_plate", "number_plate"]:
                        xyxy = box.xyxy[0].cpu().numpy().astype(int)
                        x1, y1, x2, y2 = xyxy
                        cropped_plate = img[y1:y2, x1:x2]
                        ocr_result = reader.readtext(cropped_plate)
                        plate_text = " ".join([res[1] for res in ocr_result]) if ocr_result else "N/A"
                        print(f"   🔍 OCR License Plate Text: {plate_text}")

                        detection_item = {
                            "class": class_name,
                            "confidence": conf,
                            "bbox": bbox,
                            "plate_text": plate_text
                        }
                        detection_data["detections"].append(detection_item)
                        all_detections.append(detection_item)
                    else:
                        detection_item = {
                            "class": class_name,
                            "confidence": conf,
                            "bbox": bbox,
                            "type": class_name  # Add type field for compatibility
                        }
                        detection_data["detections"].append(detection_item)
                        all_detections.append(detection_item)

                    # Detection summary
                    if class_name.lower() in ["helmet"]:
                        print("   🟢 Helmet detected!")
                    elif class_name.lower() in ["nohelmet", "without_helmet", "no_helmet"]:
                        print("   🔴 No helmet detected!")
            else:
                print("❌ No objects detected")

            # Send detection to Flask
            vehicle_no = None
            for det in detection_data["detections"]:
                if det["class"].lower() in ["vehicle_registration_plate", "license_plate", "number_plate"] and \
                   det.get("plate_text") and det["plate_text"] != "N/A":
                    vehicle_no = det["plate_text"].replace(" ", "").upper()
                    break
            send_detection_to_flask(detection_data, vehicle_no)
        
        # ✅ RETURN THE DETECTIONS
        print(f"🎯 Returning {len(all_detections)} helmet detections")
        return all_detections

    elif video_path:
        print(f"🎥 Processing video: {video_path}")

        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            print(f"❌ Error opening video: {video_path}")
            return []

        frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        fps = int(cap.get(cv2.CAP_PROP_FPS))

        output_video_path = os.path.join(output_dir, f"helmet_detection_{Path(video_path).stem}.mp4")
        out = cv2.VideoWriter(output_video_path, cv2.VideoWriter_fourcc(*'mp4v'), fps, (frame_width, frame_height))

        frame_count = 0
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break

            frame_count += 1
            results = model(frame, conf=confidence)
            annotated_frame = results[0].plot()
            out.write(annotated_frame)

            if frame_count % 30 == 0:
                print(f"📹 Processed {frame_count} frames...")

        cap.release()
        out.release()
        print(f"✅ Video processing completed: {output_video_path}")
        return []  # Video processing doesn't return detections for now

    else:
        print("❌ Please provide either image_path or video_path")
        return []


def process_video(video_path, output_dir="outputs"):
    """Process video file for helmet detection"""
    detect_helmets(video_path=video_path, output_dir=output_dir)


def process_image(image_path, output_dir="outputs"):
    """Process image file for helmet detection"""
    detect_helmets(image_path=image_path, output_dir=output_dir)


if __name__ == "__main__":
    print("🎯 Helmet Detection System")
    print("=" * 50)
    detect_helmets(image_path="detect2.jpg")

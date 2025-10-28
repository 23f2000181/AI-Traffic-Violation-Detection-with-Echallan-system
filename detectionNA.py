from ultralytics import YOLO
import cv2
import os
from pathlib import Path
import easyocr
import requests
import time
from datetime import datetime
from pymongo import MongoClient

def detect_helmets(image_path=None, video_path=None, output_dir="outputs", confidence=0.5):
    """Detect helmets in images or videos using trained YOLO model"""

    # Create output directory
    os.makedirs(output_dir, exist_ok=True)

    # Initialize EasyOCR reader
    reader = easyocr.Reader(['en'])

    # Initialize MongoDB client (using port 27018 to avoid conflicts with other projects)
    client = MongoClient("mongodb://localhost:27018/")
    db = client["helmet_detection_db"]
    collection = db["detections"]

    # Load the trained model (or use pre-trained if no trained model exists)
    model_path = "runs/detect/helmet_detection_fixed/weights/best.pt"
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

    # Process image
    if image_path:
        print(f"🖼️  Processing image: {image_path}")

        # Read image
        img = cv2.imread(image_path)

        # Run detection
        results = model(image_path, conf=confidence)  # Confidence threshold

        # Process results
        for i, result in enumerate(results):
            # Save annotated image
            output_path = os.path.join(output_dir, f"helmet_detection_{Path(image_path).stem}.jpg")
            result.save(filename=output_path)

            print(f"✅ Detection saved to: {output_path}")

            # Prepare data for DB
            detection_data = {
                "timestamp": datetime.now().isoformat(),
                "image_path": output_path,
                "detections": []
            }

            # Print detection info
            boxes = result.boxes
            if boxes is not None:
                print(f"📊 Found {len(boxes)} objects:")
                for j, box in enumerate(boxes):
                    cls = int(box.cls.item())
                    conf = box.conf.item()
                    class_name = result.names[cls]
                    print(f"   - {class_name}: {conf:.2f} confidence")

                    # Crop license plate and run OCR
                    if class_name == "Vehicle_registration_plate":
                        # Get bounding box coordinates
                        xyxy = box.xyxy[0].cpu().numpy().astype(int)
                        x1, y1, x2, y2 = xyxy
                        cropped_plate = img[y1:y2, x1:x2]

                        # OCR on cropped plate
                        ocr_result = reader.readtext(cropped_plate)
                        plate_text = " ".join([res[1] for res in ocr_result]) if ocr_result else "N/A"
                        print(f"   🔍 OCR License Plate Text: {plate_text}")

                        detection_data["detections"].append({
                            "class": class_name,
                            "confidence": conf,
                            "plate_text": plate_text
                        })
                    else:
                        detection_data["detections"].append({
                            "class": class_name,
                            "confidence": conf
                        })

                    # Color coding: Green for Helmet, Red for NoHelmet
                    if class_name == "Helmet":
                        print("   🟢 Helmet detected!")
                    else:
                        print("   🔴 No helmet detected!")
            else:
                print("❌ No objects detected")

            # Send detection to Flask app
            vehicle_no = None
            for det in detection_data["detections"]:
                if det["class"] == "Vehicle_registration_plate" and det.get("plate_text") and det["plate_text"] != "N/A":
                    vehicle_no = det["plate_text"].replace(" ", "").upper()  # Clean plate text
                    break
            send_detection_to_flask(detection_data, vehicle_no)

    # Process video
    elif video_path:
        print(f"🎥 Processing video: {video_path}")

        # Open video
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            print(f"❌ Error opening video: {video_path}")
            return

        # Get video properties
        frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        fps = int(cap.get(cv2.CAP_PROP_FPS))

        # Output video path
        output_video_path = os.path.join(output_dir, f"helmet_detection_{Path(video_path).stem}.mp4")
        out = cv2.VideoWriter(output_video_path, cv2.VideoWriter_fourcc(*'mp4v'), fps, (frame_width, frame_height))

        frame_count = 0
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break

            frame_count += 1

            # Run detection on frame
            results = model(frame, conf=0.5)

            # Annotate frame
            annotated_frame = results[0].plot()

            # Write frame
            out.write(annotated_frame)

            # Print progress every 30 frames
            if frame_count % 30 == 0:
                print(f"📹 Processed {frame_count} frames...")

        cap.release()
        out.release()
        print(f"✅ Video processing completed: {output_video_path}")

    else:
        print("❌ Please provide either image_path or video_path")

def process_video(video_path, output_dir="outputs"):
    """Process video file for helmet detection"""
    detect_helmets(video_path=video_path, output_dir=output_dir)

def process_image(image_path, output_dir="outputs"):
    """Process image file for helmet detection"""
    detect_helmets(image_path=image_path, output_dir=output_dir)

if __name__ == "__main__":
    print("🎯 Helmet Detection System")
    print("=" * 50)

    # Example usage
    # For image detection:
    # detect_helmets(image_path="bus.jpg")

    # For video detection:
    # detect_helmets(video_path="your_video.mp4")

    # Or use the convenience functions:
    # process_image("bus.jpg")
    # process_video("your_video.mp4")

    print("💡 To use this script:")
    print("   - For images: detect_helmets(image_path='your_image.jpg')")
    print("   - For videos: detect_helmets(video_path='your_video.mp4')")
    print("   - Or use: process_image('your_image.jpg')")
    print("   - Or use: process_video('your_video.mp4')")

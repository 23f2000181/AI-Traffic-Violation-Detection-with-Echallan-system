import cv2
import easyocr
import numpy as np
import os
import json
from ultralytics import YOLO

class AutoLicensePlateRecognizer:
    def __init__(self):
        print("🚗 Initializing Auto License Plate Recognizer...")
        self.reader = easyocr.Reader(['en'])
        print("✅ EasyOCR ready!")
    
    def preprocess_plate(self, plate_image):
        """Optimal preprocessing for license plates"""
        if len(plate_image.shape) == 3:
            gray = cv2.cvtColor(plate_image, cv2.COLOR_BGR2GRAY)
        else:
            gray = plate_image

        scale_factor = 6
        enlarged = cv2.resize(gray, (gray.shape[1]*scale_factor, gray.shape[0]*scale_factor), interpolation=cv2.INTER_CUBIC)
        kernel = np.array([[-1,-1,-1], [-1,9,-1], [-1,-1,-1]])
        sharpened = cv2.filter2D(enlarged, -1, kernel)
        _, binary = cv2.threshold(sharpened, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        kernel_morph = cv2.getStructuringElement(cv2.MORPH_RECT, (2,2))
        cleaned = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, kernel_morph)
        return cleaned
    
    def extract_license_text(self, image_path, bbox):
        """Extract license plate text"""
        try:
            image = cv2.imread(image_path)
            x1, y1, x2, y2 = bbox
            h, w = image.shape[:2]

            pad_x = int((x2 - x1) * 0.3)
            pad_y = int((y2 - y1) * 0.3)

            x1 = max(0, x1 - pad_x)
            y1 = max(0, y1 - pad_y)
            x2 = min(w, x2 + pad_x)
            y2 = min(h, y2 + pad_y)

            cropped_plate = image[y1:y2, x1:x2]
            if cropped_plate.size == 0:
                return "No plate region", 0

            processed = self.preprocess_plate(cropped_plate)
            results = self.reader.readtext(
                processed,
                allowlist='ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789',
                detail=1
            )

            plate_text = ""
            total_conf, count = 0, 0
            for (_, text, conf) in results:
                if conf > 0.3:
                    clean = ''.join(c for c in text.upper() if c in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789')
                    plate_text += clean
                    total_conf += conf
                    count += 1

            avg_conf = total_conf / count if count else 0
            return plate_text, avg_conf

        except Exception as e:
            return f"Error: {str(e)}", 0


def detect_single_image(model_path, image_path, save_dir="results"):
    """Detect and recognize license plates from a single local image"""
    os.makedirs(save_dir, exist_ok=True)
    model = YOLO(model_path)
    ocr = AutoLicensePlateRecognizer()

    print(f"📸 Processing: {os.path.basename(image_path)}")
    results = model(image_path)

    image = cv2.imread(image_path)
    detections = []

    for result in results:
        for box in result.boxes:
            bbox = box.xyxy[0].cpu().numpy().astype(int)
            det_conf = float(box.conf[0].cpu().numpy())

            plate_text, ocr_conf = ocr.extract_license_text(image_path, bbox)

            x1, y1, x2, y2 = bbox
            cv2.rectangle(image, (x1, y1), (x2, y2), (0, 255, 0), 2)
            cv2.putText(image, plate_text, (x1, y1 - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 0, 0), 2)

            detections.append({
                "bbox": bbox.tolist(),
                "detection_confidence": det_conf,
                "plate_text": plate_text,
                "ocr_confidence": ocr_conf
            })

            print(f"✅ Plate: {plate_text} | Det Conf: {det_conf:.3f} | OCR Conf: {ocr_conf:.3f}")

    save_path = os.path.join(save_dir, os.path.basename(image_path))
    cv2.imwrite(save_path, image)
    print(f"💾 Saved annotated result: {save_path}")

    # Save JSON
    json_path = os.path.join(save_dir, "results.json")
    with open(json_path, "w") as f:
        json.dump(detections, f, indent=2)
    print(f"📄 Results saved to {json_path}")

    return detections


if __name__ == "__main__":
    # 💡 Update this to your own file path
    model_path = "models/best.pt"
    image_path = r"D:\Codes\Miniproj\detect.jpg"   # 🔹 your image path here

    detect_single_image(model_path, image_path)

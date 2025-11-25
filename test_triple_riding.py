# quick_model_test.py
from ultralytics import YOLO
import numpy as np

# Quick test to see if model works at all
model = YOLO("D:/Codes/Miniproj/triple_riding/best.pt")

# Create a simple test image with colored rectangles
test_image = np.random.randint(0, 255, (416, 416, 3), dtype=np.uint8)

# Add some colored rectangles that might trigger detection
cv2.rectangle(test_image, (50, 50), (150, 200), (100, 100, 100), -1)  # Gray rectangle
cv2.rectangle(test_image, (200, 100), (300, 250), (50, 50, 50), -1)   # Dark gray

print("🧪 Testing model with synthetic image...")
results = model(test_image, conf=0.01, verbose=True)  # Very low confidence

if len(results[0].boxes) == 0:
    print("❌ MODEL MIGHT BE FAULTY - No detections even at 0.01 confidence")
    print("💡 Ask your friend to verify the model works on their end")
else:
    print("✅ Model is detecting something!")
    for box in results[0].boxes:
        cls = int(box.cls.item())
        conf = float(box.conf[0].cpu().numpy())
        print(f"   Class: {cls}, Confidence: {conf:.3f}")
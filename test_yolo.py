from ultralytics import YOLO

# Load pre-trained YOLOv8 model
model = YOLO("yolov8n.pt")

# Run detection on sample image
results = model("bus.jpg")  # You already downloaded it

# Loop through results and show each
for r in results:
    r.show()       # Opens an image window with detections
    # OR save it as a new image:
    r.save(filename="output.jpg")

from ultralytics import YOLO
import os

def train_helmet_model():
    """Train YOLOv8 model on helmet dataset"""

    # Load pre-trained YOLOv8 nano model
    model = YOLO("yolov8n.pt")

    # Training configuration optimized for helmet detection
    results = model.train(
        data='datasets/helmet/data.yaml',  # Path to dataset config
        epochs=50,                        # Number of training epochs
        batch=16,                         # Batch size (adjust based on your RAM)
        imgsz=640,                        # Image size
        device='cpu',                     # Use CPU (change to '0' for GPU)
        workers=4,                        # Number of worker threads
        patience=10,                      # Early stopping patience
        save=True,                        # Save model checkpoints
        project='runs/detect',            # Project directory
        name='helmet_detection',          # Experiment name
        exist_ok=True,                    # Overwrite existing runs
        pretrained=True,                  # Use pre-trained weights
        optimizer='Adam',                 # Optimizer
        lr0=0.001,                        # Initial learning rate
        lrf=0.01,                         # Final learning rate
        momentum=0.937,                   # SGD momentum
        weight_decay=0.0005,              # Weight decay
        warmup_epochs=3,                  # Warmup epochs
        warmup_momentum=0.8,              # Warmup momentum
        warmup_bias_lr=0.1,               # Warmup bias learning rate
        box=7.5,                          # Box loss weight
        cls=0.5,                          # Classification loss weight
        dfl=1.5,                          # DFL loss weight
        val=True,                         # Validate during training
        plots=True,                       # Create plots
        save_period=10,                   # Save checkpoint every N epochs
        cache=False,                      # Cache images
        amp=True,                         # Automatic mixed precision
        fraction=1.0,                     # Dataset fraction
        verbose=True                      # Show training progress
    )

    print("✅ Training completed!")
    print(f"📁 Results saved to: {results.save_dir}")
    print(f"🏆 Best model: {results.save_dir}/weights/best.pt")

    return results

if __name__ == "__main__":
    print("🚀 Starting helmet detection model training...")
    train_helmet_model()

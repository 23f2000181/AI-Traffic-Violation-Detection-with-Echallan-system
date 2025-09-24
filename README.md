# 🪖 Helmet Detection System

A complete YOLOv8-based helmet detection system that can detect helmets and no-helmet cases in images and videos.

## 🚀 Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Test the System
```bash
python test_helmet_system.py
```

### 3. Train Your Model
```bash
python train_helmet_clean.py
```

### 4. Detect Helmets
```bash
python detect_helmet_fixed.py
```

## 📁 Project Structure

```
helmet-detection/
├── datasets/
│   └── helmet/
│       ├── data.yaml          # Dataset configuration
│       ├── images/
│       │   ├── train/         # Training images
│       │   └── val/           # Validation images
│       └── labels/            # Annotation files
├── runs/
│   └── detect/               # Training outputs
├── test_yolo.py              # Basic YOLO test
├── train_helmet_clean.py     # Model training script
├── detect_helmet_fixed.py    # Detection script
├── requirements.txt          # Dependencies
├── pyproject.toml           # Project configuration
└── README.md                # This file
```

## 🎯 Features

- ✅ **Helmet Detection**: Detects helmets with high accuracy
- ✅ **No-Helmet Detection**: Identifies when helmets are missing
- ✅ **Image Processing**: Works with JPG, PNG images
- ✅ **Video Processing**: Real-time video analysis
- ✅ **Custom Training**: Train on your own dataset
- ✅ **Pre-trained Models**: Ready-to-use detection
- ✅ **Confidence Scoring**: Shows detection confidence levels

## 🛠️ Usage

### Basic Detection
```python
from detect_helmet_fixed import detect_helmets

# Detect in image
detect_helmets(image_path="bus.jpg")

# Detect in video
detect_helmets(video_path="video.mp4")
```

### Training Your Model
```python
from train_helmet_clean import train_helmet_model

# Train the model
results = train_helmet_model()
```

## 📊 Dataset Format

Your dataset should be organized as:

```
datasets/helmet/
├── data.yaml
├── images/
│   ├── train/
│   │   ├── image1.jpg
│   │   └── image2.jpg
│   └── val/
│       ├── image3.jpg
│       └── image4.jpg
└── labels/
    ├── train/
    │   ├── image1.txt
    │   └── image2.txt
    └── val/
        ├── image3.txt
        └── image4.txt
```

### Label Format
Each label file should contain one line per object:
```
class_id x_center y_center width height
```

Where:
- `class_id`: 0 for Helmet, 1 for NoHelmet
- `x_center`, `y_center`, `width`, `height`: Normalized coordinates (0-1)

## 🎨 Output

### Image Detection
- **Green boxes**: Helmets detected
- **Red boxes**: No helmets detected
- **Confidence scores**: Shown for each detection
- **Output saved**: `outputs/helmet_detection_filename.jpg`

### Video Detection
- **Real-time processing**: Frame-by-frame analysis
- **Annotated video**: Saved as MP4
- **Progress tracking**: Shows processing status

## ⚙️ Configuration

### Training Parameters
- **Model**: YOLOv8n (nano) - lightweight and fast
- **Epochs**: 50 (adjustable)
- **Batch Size**: 16 (adjust based on your RAM)
- **Image Size**: 640x640
- **Device**: CPU (change to '0' for GPU)

### Detection Parameters
- **Confidence Threshold**: 0.5 (50% confidence minimum)
- **Classes**: 2 (Helmet, NoHelmet)
- **Output Directory**: `outputs/` (configurable)

## 🔧 Troubleshooting

### Common Issues

1. **"No module named 'ultralytics'"**
   ```bash
   pip install ultralytics
   ```

2. **"Dataset not found"**
   - Check `datasets/helmet/data.yaml` paths
   - Ensure images are in correct directories
   - Verify label files exist and are properly formatted

3. **"CUDA out of memory"**
   - Reduce batch size in training script
   - Use CPU instead of GPU: `device='cpu'`

4. **Poor detection accuracy**
   - Train longer (increase epochs)
   - Add more training data
   - Adjust confidence threshold

### Performance Tips

- **For faster training**: Use GPU if available
- **For better accuracy**: Increase epochs and add more data
- **For real-time detection**: Use smaller models (YOLOv8n)
- **For higher accuracy**: Use larger models (YOLOv8s, YOLOv8m)

## 📈 Model Performance

### Metrics to Track
- **mAP@0.5**: Mean Average Precision (higher is better)
- **Precision**: Correct positive detections
- **Recall**: Detection coverage
- **F1-Score**: Balance of precision and recall

### Expected Results
- **Training time**: 30-60 minutes on CPU
- **Model size**: ~6MB for YOLOv8n
- **Detection speed**: ~50-100 FPS on CPU
- **Accuracy**: 80-95% depending on training data quality

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch
3. Add your improvements
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- [Ultralytics](https://github.com/ultralytics/ultralytics) for YOLOv8
- Open source community for datasets and tools
- Contributors and testers

---

**Happy helmet detecting! 🪖✨**

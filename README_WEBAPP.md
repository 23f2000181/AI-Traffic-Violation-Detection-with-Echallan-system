# Traffic Violation Detection Web Application

A comprehensive web application for AI-powered traffic violation detection using YOLOv8 models. Features include license plate recognition, helmet violation detection, and red light violation detection with a modern React UI and Flask backend.

## Features

- 🚗 **License Plate Detection**: Automatic license plate recognition with OCR
- 🛵 **Helmet Violation Detection**: Detect riders without helmets
- 🚦 **Red Light Violation Detection**: Identify vehicles crossing red lights
- 📊 **Real-time Dashboard**: Statistics and violation trends
- 📤 **Drag & Drop Upload**: Easy image upload interface
- 📋 **Violation History**: Searchable and filterable violation records
- 🎨 **Modern UI**: Dark mode with glassmorphism effects

## Tech Stack

**Backend:**
- Python 3.8+
- Flask (REST API)
- MongoDB (Database)
- YOLOv8 (Object Detection)
- EasyOCR (License Plate Recognition)
- OpenCV (Image Processing)

**Frontend:**
- React 18
- Vite (Build Tool)
- Recharts (Data Visualization)
- Axios (HTTP Client)
- React Router (Navigation)

## Prerequisites

- Python 3.8 or higher
- Node.js 16 or higher
- MongoDB (local or cloud)
- CUDA-capable GPU (optional, for faster processing)

## Installation

### 1. Clone the Repository

```bash
git clone <repository-url>
cd Miniproj
```

### 2. Backend Setup

```bash
# Install Python dependencies
pip install -r requirements.txt

# Create .env file
cp .env.example .env

# Edit .env with your MongoDB URI
# MONGO_URI=mongodb://localhost:27017
```

### 3. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Return to root directory
cd ..
```

### 4. Verify Model Files

Ensure the following model files exist:
- `license_plate_detection/models/best.pt` - License plate detection model
- `runs/detect/helmet_detection/weights/best.pt` - Helmet detection model
- `yolov8n.pt` - Base YOLO model

## Running the Application

### Start Backend Server

```bash
# From project root
cd backend
python app.py
```

The API server will start on `http://localhost:5000`

### Start Frontend Development Server

```bash
# In a new terminal, from project root
cd frontend
npm run dev
```

The React app will start on `http://localhost:3000`

## Usage

1. **Navigate to Dashboard** - View overall statistics and recent activity
2. **Upload Image** - Go to Upload page and drag/drop an image
3. **View Results** - See detection results with annotated images
4. **Browse History** - Check all past violations in the History page

## API Endpoints

### Upload & Process Image
```
POST /api/upload-image
Content-Type: multipart/form-data
Body: { image: <file> }
```

### Get Violations
```
GET /api/violations?page=1&page_size=50
```

### Get Specific Violation
```
GET /api/violations/:id
```

### Delete Violation
```
DELETE /api/violations/:id
```

### Get Statistics
```
GET /api/statistics
```

### Configuration
```
GET /api/config
PUT /api/config
```

## Project Structure

```
Miniproj/
├── backend/
│   ├── app.py                 # Flask API server
│   ├── config.py              # Configuration
│   ├── database.py            # MongoDB operations
│   └── detection_service.py   # AI detection service
├── frontend/
│   ├── src/
│   │   ├── components/        # React components
│   │   ├── pages/             # Page components
│   │   ├── services/          # API services
│   │   ├── App.jsx            # Main app component
│   │   └── index.css          # Global styles
│   ├── package.json
│   └── vite.config.js
├── central_detection_manager.py  # Core AI engine
├── config.json                # Detection configuration
├── requirements.txt           # Python dependencies
└── README_WEBAPP.md          # This file
```

## Configuration

### Detection Settings (config.json)

```json
{
  "models": {
    "license_plate": "path/to/license_plate_model.pt",
    "helmet": "path/to/helmet_model.pt"
  },
  "confidence_thresholds": {
    "license_plate": 0.5,
    "helmet": 0.25,
    "red_light": 0.7
  },
  "violation_settings": {
    "stop_line": {
      "start": [100, 400],
      "end": [600, 400]
    },
    "traffic_light_roi": [50, 50, 100, 200]
  }
}
```

### Environment Variables (.env)

```
MONGO_URI=mongodb://localhost:27017
TWILIO_SID=your_twilio_sid (optional)
TWILIO_TOKEN=your_twilio_token (optional)
TWILIO_FROM=your_twilio_phone (optional)
```

## MongoDB Schema

### Violations Collection

```javascript
{
  _id: ObjectId,
  timestamp: ISODate,
  image_path: String,
  processed_image_path: String,
  detection_results: {
    license_plates: [{
      plate_text: String,
      confidence: Number,
      bbox: [Number],
      timestamp: ISODate
    }],
    helmet_violations: [{
      type: String,
      confidence: Number,
      bbox: [Number],
      timestamp: ISODate
    }],
    red_light_violations: [{
      vehicle_type: String,
      confidence: Number,
      bbox: [Number],
      light_state: String,
      timestamp: ISODate
    }]
  },
  processing_time: Number,
  status: String
}
```

## Docker Deployment

```bash
# Build and run with Docker Compose
docker-compose up -d
```

## Troubleshooting

### Backend Issues

**MongoDB Connection Error:**
- Verify MongoDB is running
- Check MONGO_URI in .env file
- Ensure MongoDB port (27017) is not blocked

**Model Loading Error:**
- Verify model file paths in config.json
- Ensure model files exist and are accessible
- Check Python dependencies are installed

### Frontend Issues

**API Connection Error:**
- Ensure backend is running on port 5000
- Check CORS configuration in backend/app.py
- Verify proxy settings in vite.config.js

**Build Errors:**
- Delete node_modules and reinstall: `npm install`
- Clear npm cache: `npm cache clean --force`

## Performance Optimization

- Use GPU acceleration for faster detection (CUDA)
- Adjust confidence thresholds for accuracy vs speed
- Enable image compression for faster uploads
- Use pagination for large violation datasets

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

This project is for educational and demonstration purposes.

## Support

For issues and questions, please open an issue on the repository.

## Acknowledgments

- YOLOv8 by Ultralytics
- EasyOCR for license plate recognition
- React and Vite communities

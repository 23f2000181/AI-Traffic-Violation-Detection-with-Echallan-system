# Quick Start Guide - Traffic Violation Detection Web App

## Prerequisites Check

- ✅ Python 3.8+ installed
- ✅ Node.js 16+ installed
- ✅ MongoDB running (local or cloud)
- ✅ All model files in place

## Step 1: Install Backend Dependencies

```bash
pip install flask-cors
```

All other dependencies should already be installed from your existing setup.

## Step 2: Start MongoDB

Make sure MongoDB is running on `mongodb://localhost:27017` or update your `.env` file with the correct URI.

## Step 3: Start Backend Server

```bash
cd backend
python app.py
```

You should see:
```
🚀 Starting Traffic Violation Detection API Server...
📁 Upload folder: D:\Codes\Miniproj\uploads
📁 Processed folder: D:\Codes\Miniproj\processed
🗄️  MongoDB URI: mongodb://localhost:27017
🌐 CORS origins: ['http://localhost:3000', 'http://localhost:5173']
✅ Connected to MongoDB successfully
✅ Database indexes created
✅ CentralDetectionManager initialized
 * Running on http://0.0.0.0:5000
```

## Step 4: Start Frontend (New Terminal)

```bash
cd frontend
npm run dev
```

You should see:
```
VITE v5.x.x  ready in xxx ms

➜  Local:   http://localhost:3000/
➜  Network: use --host to expose
```

## Step 5: Open Browser

Navigate to: **http://localhost:3000**

## Step 6: Test the Application

### Upload Test
1. Click "📤 Upload" in navigation
2. Drag and drop a test image (e.g., `detect2.jpg`, `bus.jpg`)
3. Watch the upload progress
4. View detection results

### Dashboard Test
1. Click "📊 Dashboard"
2. Verify statistics are displayed
3. Check the violation distribution chart

### History Test
1. Click "📋 History"
2. See your uploaded violations
3. Click "👁️ View" to see details
4. Test delete functionality

## Troubleshooting

### Backend Won't Start

**Error: MongoDB connection failed**
```bash
# Check if MongoDB is running
# Windows: Check Services
# Or start MongoDB manually
```

**Error: Module not found**
```bash
pip install -r requirements.txt
```

### Frontend Won't Start

**Error: Cannot find module**
```bash
cd frontend
rm -rf node_modules package-lock.json
npm install
```

### API Connection Error

**CORS Error in Browser Console**
- Verify backend is running on port 5000
- Check CORS_ORIGINS in `backend/config.py`

**404 Errors**
- Ensure both backend and frontend are running
- Check proxy configuration in `frontend/vite.config.js`

## Production Deployment

### Using Docker

```bash
# Build and start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

Access the app at: **http://localhost:3000**

## Next Steps

- Upload test images from your project directory
- Check MongoDB to see stored violations
- Customize detection thresholds in `config.json`
- Add more test cases

## Support

See `README_WEBAPP.md` for detailed documentation.

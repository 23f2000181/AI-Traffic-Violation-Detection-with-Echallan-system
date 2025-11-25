from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from werkzeug.utils import secure_filename
import os
import sys
import traceback
from datetime import datetime

# Add current and parent directory to path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, current_dir)
sys.path.insert(0, parent_dir)

import config as Config_module
import database as db_module
import detection_service as detection_service_module
import vehicle_service as vehicle_service_module
import challan_service as challan_service_module
import notification_service as notification_service_module

Config = Config_module.Config
db = db_module.db
detection_service = detection_service_module.detection_service
vehicle_service = vehicle_service_module.vehicle_service
challan_service = challan_service_module.challan_service
notification_service = notification_service_module.notification_service

app = Flask(__name__)
CORS(app, origins=Config.CORS_ORIGINS)

# Initialize app
Config.init_app()

def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in Config.ALLOWED_EXTENSIONS

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat()
    })

@app.route('/api/upload-image', methods=['POST'])
def upload_image():
    """
    Upload and process an image
    
    Request: multipart/form-data with 'image' file
    Response: Violation record with detection results
    """
    try:
        # Validate request
        if 'image' not in request.files:
            return jsonify({'error': 'No image file provided'}), 400
        
        file = request.files['image']
        
        if file.filename == '':
            return jsonify({'error': 'No selected file'}), 400
        
        if not allowed_file(file.filename):
            return jsonify({
                'error': f'Invalid file type. Allowed types: {", ".join(Config.ALLOWED_EXTENSIONS)}'
            }), 400
        
        # Save uploaded file
        filename = secure_filename(file.filename)
        timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
        filename = f"{timestamp}_{filename}"
        file_path = os.path.join(Config.UPLOAD_FOLDER, filename)
        file.save(file_path)
        
        print(f"📁 File saved: {file_path}")
        
        # Process image with CentralDetectionManager
        print("🔄 Processing image...")
        results = detection_service.process_uploaded_image(file_path)
        
        # Save to MongoDB
        violation_id = db.create_violation(results)
        
        print(f"✅ Violation created: {violation_id}")
        
        # Format response
        response_data = {
            'success': True,
            'violation_id': violation_id,
            'results': {
                'license_plates': results['detection_results']['license_plates'],
                'helmet_violations': results['detection_results']['helmet_violations'],
                'red_light_violations': results['detection_results']['red_light_violations'],
                'processing_time': results['processing_time'],
                'image_path': f'/api/images/uploads/{os.path.basename(file_path)}',
                'processed_image_path': f'/api/images/processed/{os.path.basename(results["processed_image_path"])}' if results.get('processed_image_path') else None
            }
        }
        
        return jsonify(response_data), 200
        
    except Exception as e:
        print(f"❌ Error in upload_image: {e}")
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@app.route('/api/violations', methods=['GET'])
def get_violations():
    """
    Get paginated violations with optional filters
    
    Query params:
        - page: Page number (default: 1)
        - page_size: Items per page (default: 50, max: 100)
        - status: Filter by status
        - date_from: Filter by date (ISO format)
        - date_to: Filter by date (ISO format)
    """
    try:
        # Parse query parameters
        page = int(request.args.get('page', 1))
        page_size = min(int(request.args.get('page_size', Config.DEFAULT_PAGE_SIZE)), Config.MAX_PAGE_SIZE)
        
        # Build filters
        filters = {}
        if request.args.get('status'):
            filters['status'] = request.args.get('status')
        if request.args.get('date_from'):
            filters['date_from'] = datetime.fromisoformat(request.args.get('date_from'))
        if request.args.get('date_to'):
            filters['date_to'] = datetime.fromisoformat(request.args.get('date_to'))
        
        # Get violations
        result = db.get_violations(page, page_size, filters)
        
        return jsonify(result), 200
        
    except Exception as e:
        print(f"❌ Error in get_violations: {e}")
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@app.route('/api/violations/<violation_id>', methods=['GET'])
def get_violation(violation_id):
    """Get a specific violation by ID"""
    try:
        violation = db.get_violation(violation_id)
        
        if not violation:
            return jsonify({'error': 'Violation not found'}), 404
        
        # Convert ObjectId to string
        violation['_id'] = str(violation['_id'])
        
        return jsonify(violation), 200
        
    except Exception as e:
        print(f"❌ Error in get_violation: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/violations/<violation_id>', methods=['DELETE'])
def delete_violation(violation_id):
    """Delete a violation by ID"""
    try:
        success = db.delete_violation(violation_id)
        
        if not success:
            return jsonify({'error': 'Violation not found'}), 404
        
        return jsonify({'success': True, 'message': 'Violation deleted'}), 200
        
    except Exception as e:
        print(f"❌ Error in delete_violation: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/statistics', methods=['GET'])
def get_statistics():
    """Get dashboard statistics"""
    try:
        stats = db.get_statistics()
        return jsonify(stats), 200
        
    except Exception as e:
        print(f"❌ Error in get_statistics: {e}")
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@app.route('/api/config', methods=['GET'])
def get_config():
    """Get system configuration"""
    try:
        config = db.get_config()
        return jsonify(config or {}), 200
        
    except Exception as e:
        print(f"❌ Error in get_config: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/config', methods=['PUT'])
def update_config():
    """Update system configuration"""
    try:
        config_data = request.json
        success = db.update_config(config_data)
        
        return jsonify({
            'success': success,
            'message': 'Configuration updated' if success else 'Failed to update configuration'
        }), 200 if success else 500
        
    except Exception as e:
        print(f"❌ Error in update_config: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/images/uploads/<filename>', methods=['GET'])
def serve_upload(filename):
    """Serve uploaded images"""
    return send_from_directory(Config.UPLOAD_FOLDER, filename)

@app.route('/api/images/processed/<filename>', methods=['GET'])
def serve_processed(filename):
    """Serve processed images"""
    return send_from_directory(Config.PROCESSED_FOLDER, filename)

@app.errorhandler(404)
def not_found(e):
    return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def internal_error(e):
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    print("🚀 Starting Traffic Violation Detection API Server...")
    print(f"📁 Upload folder: {Config.UPLOAD_FOLDER}")
    print(f"📁 Processed folder: {Config.PROCESSED_FOLDER}")
    print(f"🗄️  MongoDB URI: {Config.MONGO_URI}")
    print(f"🌐 CORS origins: {Config.CORS_ORIGINS}")
    
    app.run(host='0.0.0.0', port=5000, debug=True)

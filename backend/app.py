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
        
        # Auto-generate e-challan if license plate detected
        challan_generated = False
        challan_info = None
        
        license_plates = results['detection_results'].get('license_plates', [])
        has_violations = (
            len(results['detection_results'].get('helmet_violations', [])) > 0 or
            len(results['detection_results'].get('triple_riding_violations', [])) > 0 or
            len(results['detection_results'].get('red_light_violations', [])) > 0
        )
        
        if license_plates and has_violations:
            # Get the first detected license plate
            plate_text = license_plates[0].get('plate_text', '').strip()
            
            if plate_text:
                print(f"🔍 Looking up vehicle: {plate_text}")
                
                # Lookup vehicle in database
                vehicle_info = vehicle_service.lookup_vehicle(plate_text)
                
                if vehicle_info:
                    print(f"✅ Vehicle found! Generating e-challan...")
                    
                    # Add violation_id to results for challan generation
                    results['_id'] = violation_id
                    
                    # Generate challan
                    try:
                        challan = challan_service.generate_challan(results, vehicle_info)
                        challan_generated = True
                        challan_info = {
                            'challan_no': challan['challan_no'],
                            'total_penalty': challan['total_penalty'],
                            'vehicle_no': challan['vehicle_no'],
                            'owner_name': challan['owner_name']
                        }
                        
                        # Send notification
                        print(f"📱 Sending notification to owner...")
                        challan['owner_phone'] = vehicle_info['owner']['phone']
                        challan['owner_email'] = vehicle_info['owner'].get('email', '')
                        
                        notification_results = notification_service.send_challan_notification(
                            challan, 
                            methods=['sms']
                        )
                        
                        print(f"✅ E-Challan generated and notification sent!")
                        
                    except Exception as e:
                        print(f"⚠️ Error generating challan: {e}")
                else:
                    print(f"⚠️ Vehicle {plate_text} not found in database")
        
        # Format response - UPDATED: Include both helmet_detections and helmet_violations
        response_data = {
            'success': True,
            'violation_id': violation_id,
            'challan_generated': challan_generated,
            'challan_info': challan_info,
            'results': {
                'license_plates': results['detection_results']['license_plates'],
                'helmet_detections': results['detection_results'].get('helmet_detections', []),  # All helmet detections
                'helmet_violations': results['detection_results'].get('helmet_violations', []),  # Only actual violations
                'triple_riding_violations': results['detection_results']['triple_riding_violations'],
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

# ============================================================================
# E-CHALLAN ENDPOINTS
# ============================================================================

# Vehicle and Owner Management Endpoints

@app.route('/api/vehicles/<plate_number>', methods=['GET'])
def lookup_vehicle(plate_number):
    """Lookup vehicle by license plate"""
    try:
        vehicle_info = vehicle_service.lookup_vehicle(plate_number)
        
        if not vehicle_info:
            return jsonify({'error': 'Vehicle not found'}), 404
        
        return jsonify(vehicle_info), 200
        
    except Exception as e:
        print(f"❌ Error looking up vehicle: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/vehicles', methods=['POST'])
def register_vehicle():
    """Register a new vehicle"""
    try:
        vehicle_data = request.json
        vehicle_id = vehicle_service.register_vehicle(vehicle_data)
        
        return jsonify({
            'success': True,
            'vehicle_id': vehicle_id,
            'message': 'Vehicle registered successfully'
        }), 201
        
    except Exception as e:
        print(f"❌ Error registering vehicle: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/vehicles', methods=['GET'])
def get_all_vehicles():
    """Get all vehicles with pagination"""
    try:
        page = int(request.args.get('page', 1))
        page_size = int(request.args.get('page_size', 50))
        
        result = vehicle_service.get_all_vehicles(page, page_size)
        return jsonify(result), 200
        
    except Exception as e:
        print(f"❌ Error getting vehicles: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/owners', methods=['POST'])
def register_owner():
    """Register a new owner"""
    try:
        owner_data = request.json
        owner_id = vehicle_service.register_owner(owner_data)
        
        return jsonify({
            'success': True,
            'owner_id': owner_id,
            'message': 'Owner registered successfully'
        }), 201
        
    except Exception as e:
        print(f"❌ Error registering owner: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/owners', methods=['GET'])
def get_all_owners():
    """Get all owners with pagination"""
    try:
        page = int(request.args.get('page', 1))
        page_size = int(request.args.get('page_size', 50))
        
        result = vehicle_service.get_all_owners(page, page_size)
        return jsonify(result), 200
        
    except Exception as e:
        print(f"❌ Error getting owners: {e}")
        return jsonify({'error': str(e)}), 500

# Challan Management Endpoints

@app.route('/api/challans', methods=['GET'])
def get_all_challans():
    """Get all challans with pagination and filters"""
    try:
        page = int(request.args.get('page', 1))
        page_size = int(request.args.get('page_size', 50))
        
        filters = {}
        if request.args.get('status'):
            filters['status'] = request.args.get('status')
        if request.args.get('vehicle_no'):
            filters['vehicle_no'] = request.args.get('vehicle_no')
        
        result = challan_service.get_all_challans(page, page_size, filters)
        return jsonify(result), 200
        
    except Exception as e:
        print(f"❌ Error getting challans: {e}")
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@app.route('/api/challans/<challan_no>', methods=['GET'])
def get_challan(challan_no):
    """Get specific challan by number"""
    try:
        challan = challan_service.get_challan(challan_no)
        
        if not challan:
            return jsonify({'error': 'Challan not found'}), 404
        
        return jsonify(challan), 200
        
    except Exception as e:
        print(f"❌ Error getting challan: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/challans/<challan_no>/status', methods=['PUT'])
def update_challan_status(challan_no):
    """Update challan status"""
    try:
        data = request.json
        status = data.get('status')
        
        if not status:
            return jsonify({'error': 'Status is required'}), 400
        
        success = challan_service.update_challan_status(challan_no, status)
        
        if not success:
            return jsonify({'error': 'Challan not found'}), 404
        
        return jsonify({
            'success': True,
            'message': f'Challan status updated to {status}'
        }), 200
        
    except Exception as e:
        print(f"❌ Error updating challan status: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/challans/<challan_no>/notify', methods=['POST'])
def resend_notification(challan_no):
    """Resend notification for a challan"""
    try:
        challan = challan_service.get_challan(challan_no)
        
        if not challan:
            return jsonify({'error': 'Challan not found'}), 404
        
        # Get vehicle info to get owner contact
        vehicle_info = vehicle_service.lookup_vehicle(challan['vehicle_no'])
        
        if not vehicle_info:
            return jsonify({'error': 'Vehicle information not found'}), 404
        
        # Add owner contact to challan for notification
        challan['owner_phone'] = vehicle_info['owner']['phone']
        challan['owner_email'] = vehicle_info['owner']['email']
        
        # Send notification
        methods = request.json.get('methods', ['sms']) if request.json else ['sms']
        results = notification_service.send_challan_notification(challan, methods)
        
        return jsonify({
            'success': True,
            'notification_results': results
        }), 200
        
    except Exception as e:
        print(f"❌ Error resending notification: {e}")
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@app.route('/api/challans/statistics', methods=['GET'])
def get_challan_statistics():
    """Get challan statistics"""
    try:
        stats = challan_service.get_challan_statistics()
        return jsonify(stats), 200
        
    except Exception as e:
        print(f"❌ Error getting challan statistics: {e}")
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

# ============================================================================
# ERROR HANDLERS
# ============================================================================


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
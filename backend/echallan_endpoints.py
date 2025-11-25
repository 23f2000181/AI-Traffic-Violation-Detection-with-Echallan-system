# E-Challan API Endpoints
# Add these to backend/app.py after the existing endpoints (around line 227)

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

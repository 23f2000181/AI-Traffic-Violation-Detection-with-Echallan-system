import os, uuid, datetime, json
from flask import Flask, request, jsonify, render_template, redirect, url_for, flash
from werkzeug.utils import secure_filename
from pymongo import MongoClient
from twilio.rest import Client
from dotenv import load_dotenv
from detect_module import process_image, send_detection_to_flask

load_dotenv()
MONGO_URI = os.getenv('MONGO_URI')
TW_SID = os.getenv('TWILIO_SID')
TW_TOKEN = os.getenv('TWILIO_TOKEN')
TW_FROM = os.getenv('TWILIO_FROM')

client = MongoClient(MONGO_URI)
db = client['echallan']

tw_client = Client(TW_SID, TW_TOKEN) if TW_SID and TW_TOKEN else None

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'  # Change this in production
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Create upload folder if it doesn't exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

def find_applicable_rules(detection):
    # detection can be:
    # - A single detection dict: {"class":"NoHelmet","confidence":0.6}
    # - A list of detection dicts: [{"class":"NoHelmet","confidence":0.6}]
    # - A detection data dict with "detections" list: {"detections": [{"class":"NoHelmet","confidence":0.6}], ...}

    detections = []

    if isinstance(detection, dict):
        if 'detections' in detection:
            # New format from detect_helmet.py
            detections = detection['detections']
        else:
            # Single detection dict
            detections = [detection]
    elif isinstance(detection, list):
        # List of detections
        detections = detection
    else:
        return []

    applicable = []
    for det in detections:
        class_name = det.get('class')
        conf = det.get('confidence', 0.0)
        if not class_name:
            continue

        rules = list(db.rules.find({"violation_class": class_name, "active": True}))
        for r in rules:
            if conf >= r.get('min_confidence', 0.0):
                applicable.append(r)

    return applicable

def create_challan(vehicle_no, owner_id, rules_triggered, detection):
    challan_no = f"CH{datetime.datetime.utcnow().strftime('%Y%m%d%H%M%S')}-{str(uuid.uuid4())[:6]}"
    violations = []
    total = 0
    for r in rules_triggered:
        violations.append({"rule_id": r['rule_id'], "penalty": r['penalty'], "conf": detection.get('confidence', 0.0)})
        total += r['penalty']
    challan = {
        "challan_no": challan_no,
        "vehicle_no": vehicle_no,
        "owner_id": owner_id,
        "violations": violations,
        "total_penalty": total,
        "status": "issued",
        "issued_at": datetime.datetime.utcnow(),
        "notified": False,
        "notification_log": []
    }
    res = db.challans.insert_one(challan)
    return challan

def send_sms(to, body):
    if not tw_client:
        print("Twilio not configured; mock send:", to, body)
        return {"status":"mocked"}
    msg = tw_client.messages.create(body=body, from_=TW_FROM, to=to)
    return {"status":"sent", "sid": msg.sid}

@app.route('/detect', methods=['POST'])
def receive_detection():
    """
    Expected JSON payload from detector:
    {
      "source":"camera_1",
      "timestamp":"2025-10-28T18:00:00Z",
      "detection": {"class":"no_helmet","conf":0.92, "bbox":[x1,y1,x2,y2]},
      "vehicle_no": "MH01AB1234"  // optional if OCR matched
      "image_path": "/path/..."
    }
    """
    data = request.json
    detection = data.get('detection')
    src = data.get('source','unknown')
    vehicle_no = data.get('vehicle_no')  # may be None

    # Save raw violation log
    viol_log = {
        "timestamp": datetime.datetime.utcnow(),
        "source": src,
        "vehicle_no": vehicle_no,
        "detection": detection,
        "image_path": data.get('image_path'),
        "processed": False
    }
    db.violations.insert_one(viol_log)

    # Find rules
    rules = find_applicable_rules(detection)
    if not rules:
        return jsonify({"status":"ok","message":"no rule triggered"}), 200

    # Resolve owner via vehicle_no (if present)
    owner = None
    if vehicle_no:
        owner = db.vehicles.find_one({"vehicle_no": vehicle_no})
        if owner:
            owner_doc = db.owners.find_one({"owner_id": owner['owner_id']})
        else:
            owner_doc = None
    else:
        owner_doc = None

    # Create challan only if we have owner/vehicle or allow anonymous challans
    if owner_doc:
        challan = create_challan(vehicle_no, owner_doc['owner_id'], rules, detection)

        # Notify owner via SMS (if phone present)
        phone = owner_doc.get('phone')
        body = f"Violation: {detection['class']} detected for {vehicle_no}. Penalty INR {challan['total_penalty']}. Challan No: {challan['challan_no']}."
        sms_res = send_sms(phone, body)
        # update challan notification info
        db.challans.update_one({"challan_no": challan['challan_no']},
                               {"$set":{"notified": True}, "$push": {"notification_log": {"method":"sms","to":phone,"ts":datetime.datetime.utcnow(),"status":sms_res}}})
        return jsonify({"status":"challan_created", "challan_no": challan['challan_no']})
    else:
        # Option: create challan with vehicle_no null and mark for manual review
        review = {
            "vehicle_no": vehicle_no,
            "detection": detection,
            "status": "manual_review",
            "created_at": datetime.datetime.utcnow()
        }
        db.manual_reviews.insert_one(review)
        return jsonify({"status":"manual_review","message":"owner not found; logged for review"}), 200

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        if 'image' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['image']
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and file.filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif')):
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)

            # Process the image
            detection_data = process_image(filepath)

            # Send to Flask API
            flask_response = send_detection_to_flask(detection_data)

            # Check if challan was created
            challan = None
            if flask_response.get('status') == 'challan_created':
                challan_no = flask_response.get('challan_no')
                challan = db.challans.find_one({"challan_no": challan_no})

            return render_template('results.html',
                                 detections=detection_data['detections'],
                                 image_path=detection_data['image_path'],
                                 challan=challan)
        else:
            flash('Invalid file type. Please upload an image.')
            return redirect(request.url)
    return render_template('upload.html')

@app.route('/data')
def data():
    challans = list(db.challans.find().sort('issued_at', -1))
    violations = list(db.violations.find().sort('timestamp', -1))
    owners = list(db.owners.find())
    vehicles = list(db.vehicles.find())
    return render_template('data.html',
                         challans=challans,
                         violations=violations,
                         owners=owners,
                         vehicles=vehicles)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

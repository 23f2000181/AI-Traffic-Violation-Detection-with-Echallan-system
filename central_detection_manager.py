# central_detection_manager.py
import cv2
import os
import json
import time
from datetime import datetime
from pathlib import Path
from ultralytics import YOLO
import sys
import numpy as np

# Add the current directory and subdirectories to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'license_plate_detection'))

# Import your detection modules - with error handling
try:
    from license_plate_detection.detect_license_plate import AutoLicensePlateRecognizer, detect_single_image
    print("✅ License plate module imported successfully")
except ImportError as e:
    print(f"❌ Error importing license plate module: {e}")
    # Try direct import as fallback
    try:
        from detect_license_plate import AutoLicensePlateRecognizer, detect_single_image
        print("✅ License plate module imported directly")
    except ImportError:
        print("⚠️  Using fallback license plate recognizer")
        class AutoLicensePlateRecognizer:
            def __init__(self):
                print("⚠️  Using fallback license plate recognizer")
            def extract_license_text(self, image_path, bbox):
                return "LICENSE_PLATE_MODULE_NOT_FOUND", 0.0

        def detect_single_image(model_path, image_path, save_dir):
            print("⚠️  Using fallback license plate detection")
            return []

try:
    from detect_helmet import detect_helmets
    print("✅ Helmet detection module imported successfully")
except ImportError as e:
    print(f"❌ Error importing helmet module: {e}")
    def detect_helmets(**kwargs):
        print("⚠️  Using fallback helmet detection")
        return None

# NEW: Import our trained traffic light classifier
try:
    from tensorflow import keras
    TRAFFIC_LIGHT_MODEL_AVAILABLE = True
    print("✅ TensorFlow/Keras available for traffic light detection")
except ImportError:
    TRAFFIC_LIGHT_MODEL_AVAILABLE = False
    print("⚠️  TensorFlow not available, using color-based traffic light detection")

# Enhanced Red Light Violation Detector with AI model
class EnhancedRedLightViolationDetector:
    def __init__(self):
        print("🚦 Initializing Enhanced Red Light Violation Detector...")
        self.stop_line = None
        self.traffic_light_roi = None
        self.vehicle_model = YOLO("yolov8n.pt")  # Use YOLO for vehicle detection
        
        # Try to load the trained traffic light classifier
        self.traffic_light_model = None
        self.class_names = ['red', 'yellow', 'green']
        
        if TRAFFIC_LIGHT_MODEL_AVAILABLE:
            try:
                model_path = "D:\\Codes\\Miniproj\\models\\traffic_light_classifier.h5"
                class_names_path = "D:\\Codes\\Miniproj\\models\\class_names.json"
                
                if os.path.exists(model_path) and os.path.exists(class_names_path):
                    self.traffic_light_model = keras.models.load_model(model_path)
                    with open(class_names_path, 'r') as f:
                        self.class_names = json.load(f)
                    print("✅ Trained traffic light classifier loaded successfully!")
                else:
                    print("⚠️  Traffic light model files not found, using color-based detection")
            except Exception as e:
                print(f"⚠️  Could not load traffic light model: {e}")
        
        # Fallback: Color-based detection
        self.red_light_color_ranges = {
            'red': ([0, 100, 100], [10, 255, 255]),
            'yellow': ([20, 100, 100], [30, 255, 255]),
            'green': ([36, 100, 100], [86, 255, 255])
        }
        
        self.vehicle_tracks = {}
        print("✅ Enhanced Red Light Violation Detector Initialized!")
    
    def set_stop_line(self, start_point, end_point):
        """Set the stop line coordinates"""
        self.stop_line = (tuple(start_point), tuple(end_point))
        print(f"✅ Stop line set: {self.stop_line}")
    
    def set_traffic_light_roi(self, x, y, width, height):
        """Set traffic light region of interest"""
        self.traffic_light_roi = (x, y, width, height)
        print(f"✅ Traffic light ROI set: {self.traffic_light_roi}")
    
    def detect_traffic_light_state(self, frame):
        """
        Detect traffic light state using AI model (primary) or color detection (fallback)
        Returns: color, confidence
        """
        try:
            if self.traffic_light_roi is None:
                return "unknown", 0.0
            
            x, y, w, h = self.traffic_light_roi
            roi = frame[y:y+h, x:x+w]
            
            if roi.size == 0:
                return "unknown", 0.0
            
            # Try AI model first
            if self.traffic_light_model is not None:
                # Preprocess for AI model
                tl_resized = cv2.resize(roi, (64, 64))
                tl_normalized = tl_resized / 255.0
                tl_input = np.expand_dims(tl_normalized, axis=0)
                
                # Predict
                predictions = self.traffic_light_model.predict(tl_input, verbose=0)
                predicted_class = np.argmax(predictions[0])
                confidence = np.max(predictions[0])
                
                if confidence > 0.7:
                    return self.class_names[predicted_class], confidence
            
            # Fallback to color-based detection
            return self.detect_traffic_light_color(frame)
                
        except Exception as e:
            print(f"❌ Traffic light detection error: {e}")
            return "unknown", 0.0
    
    def detect_traffic_light_color(self, frame):
        """Fallback color-based traffic light detection"""
        try:
            if self.traffic_light_roi is None:
                return "unknown", 0.0
            
            x, y, w, h = self.traffic_light_roi
            roi = frame[y:y+h, x:x+w]
            
            if roi.size == 0:
                return "unknown", 0.0
            
            # Convert to HSV for better color detection
            hsv = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)
            
            # Check for each color
            color_scores = {}
            for color, (lower, upper) in self.red_light_color_ranges.items():
                lower = np.array(lower, dtype=np.uint8)
                upper = np.array(upper, dtype=np.uint8)
                mask = cv2.inRange(hsv, lower, upper)
                color_scores[color] = np.sum(mask) / (255 * mask.size)
            
            # Find the dominant color
            dominant_color = max(color_scores, key=color_scores.get)
            confidence = color_scores[dominant_color]
            
            if confidence > 0.01:
                return dominant_color, confidence
            else:
                return "unknown", 0.0
                
        except Exception as e:
            print(f"❌ Color-based traffic light detection error: {e}")
            return "unknown", 0.0
    
    def detect_vehicles_near_stop_line(self, frame):
        """Detect vehicles that might be violating the stop line"""
        violations = []
        
        try:
            # Detect vehicles using YOLO
            results = self.vehicle_model(frame)
            
            for result in results:
                for box in result.boxes:
                    cls = int(box.cls.item())
                    class_name = result.names[cls]
                    confidence = float(box.conf[0].cpu().numpy())
                    
                    # Filter for vehicles
                    if class_name.lower() in ['car', 'motorcycle', 'bus', 'truck', 'bike']:
                        bbox = box.xyxy[0].cpu().numpy().astype(int)
                        x1, y1, x2, y2 = bbox
                        
                        # Calculate vehicle center point
                        center_x = (x1 + x2) // 2
                        center_y = (y1 + y2) // 2
                        
                        # Check if vehicle is near or over stop line
                        if self.stop_line and self.is_vehicle_violating(center_x, center_y, bbox):
                            vehicle_id = f"{center_x}_{center_y}"
                            
                            violations.append({
                                'bbox': bbox.tolist(),
                                'class': class_name,
                                'confidence': confidence,
                                'center': [center_x, center_y],
                                'vehicle_id': vehicle_id,
                                'violation_type': 'RED_LIGHT'
                            })
            
            return violations
            
        except Exception as e:
            print(f"❌ Vehicle detection error: {e}")
            return []
    
    def is_vehicle_violating(self, center_x, center_y, bbox):
        """Check if vehicle is violating stop line rules"""
        if not self.stop_line:
            return False
            
        start_point, end_point = self.stop_line
        x1, y1, x2, y2 = bbox
        
        # Simple violation check: if vehicle center is beyond stop line
        stop_line_y = start_point[1]  # Assuming horizontal stop line
        
        # Vehicle is violating if its center is beyond the stop line
        if center_y < stop_line_y:  # Assuming stop line is at bottom of image
            return True
        
        return False
    
    def detect_violations(self, frame, vehicle_detections=None):
        """
        Main violation detection method
        Returns: violations, light_state, confidence
        """
        try:
            # Detect traffic light state
            light_state, confidence = self.detect_traffic_light_state(frame)
            
            # If light is red, check for violations
            violations = []
            if light_state == 'red' and confidence > 0.1:
                print("🔴 RED LIGHT DETECTED - Checking for violations...")
                violations = self.detect_vehicles_near_stop_line(frame)
                print(f"🚨 Found {len(violations)} potential violations")
            
            return violations, light_state, confidence
            
        except Exception as e:
            print(f"❌ Violation detection error: {e}")
            return [], "unknown", 0.0

class CentralDetectionManager:
    def __init__(self, config_path="config.json"):
        """
        Central manager for all detection systems
        """
        print("🚀 Initializing Central Detection Manager...")
        
        # Load configuration
        self.config = self.load_config(config_path)
        
        # Initialize detection systems
        self.license_plate_recognizer = AutoLicensePlateRecognizer()
        self.red_light_detector = EnhancedRedLightViolationDetector()
        self.helmet_model = None
        self.triple_riding_model = None
        
        # Verify license plate recognizer import
        self.verify_license_plate_module()
        
        # Initialize models based on config
        self.initialize_models()
        
        # Setup red light detector
        self.setup_red_light_detector()
        
        # Detection results storage
        self.detection_results = {
            "license_plates": [],
            "helmet_violations": [],
            "red_light_violations": [],
            "triple_riding_violations": [],
            "timestamps": []
        }
        
        print("✅ Central Detection Manager Ready!")
    
    def setup_red_light_detector(self):
        """Setup the red light violation detector with configuration"""
        try:
            # Configure stop line and ROI from config
            violation_settings = self.config["violation_settings"]
            stop_line = violation_settings["stop_line"]
            tl_roi = violation_settings["traffic_light_roi"]
            
            self.red_light_detector.set_stop_line(
                stop_line["start"], stop_line["end"]
            )
            self.red_light_detector.set_traffic_light_roi(*tl_roi)
            print("✅ Red light violation detector configured")
            
        except Exception as e:
            print(f"⚠️  Red light detector setup failed: {e}")
    
    def verify_license_plate_module(self):
        """Verify that the correct license plate module is being used"""
        try:
            print(f"🔍 Using AutoLicensePlateRecognizer from: {AutoLicensePlateRecognizer.__module__}")
            print(f"🔍 License plate recognizer class: {self.license_plate_recognizer.__class__.__name__}")
            
            if hasattr(self.license_plate_recognizer, 'preprocess_plate'):
                print("✅ Binary preprocessing method found in license plate recognizer")
            else:
                print("⚠️  Binary preprocessing method NOT found in license plate recognizer")
                
        except Exception as e:
            print(f"❌ Error verifying license plate module: {e}")
    
    def load_config(self, config_path):
        """Load configuration from JSON file"""
        default_config = {
            "models": {
                "license_plate": "D:/Codes/Miniproj/license_plate_detection/models/best.pt",
                "helmet": "D:/Codes/Miniproj/runs/detect/helmet_detection/weights/best.pt",
                "triple_riding": "D:/Codes/Miniproj/triple_riding/yolov8n.pt"  # ✅ Using standard YOLOv8n model
            },
            "output_dirs": {
                "license_plates": "results/license_plates",
                "helmets": "results/helmet_detection",
                "red_light": "results/red_light_violations",
                "triple_riding": "results/triple_riding",
                "combined": "results/combined"
            },
            "confidence_thresholds": {
                "license_plate": 0.5,
                "helmet": 0.25,
                "red_light": 0.3,
                "triple_riding": 0.4
            },
            "violation_settings": {
                "stop_line": {
                    "start": [100, 400], 
                    "end": [600, 400]
                },
                "traffic_light_roi": [500, 50, 100, 200]
            },
            "preprocessing": {
                "apply_binary_preprocessing": True,
                "scale_factor": 6,
                "use_otsu_threshold": True
            }
        }
        
        if os.path.exists(config_path):
            with open(config_path, 'r') as f:
                user_config = json.load(f)
                # Merge with default config
                default_config.update(user_config)
        
        # Create output directories
        for dir_path in default_config["output_dirs"].values():
            os.makedirs(dir_path, exist_ok=True)
        
        return default_config
    
    def initialize_models(self):
        """Initialize all detection models"""
        try:
            # Initialize helmet detection model
            helmet_model_path = self.config["models"]["helmet"]
            if os.path.exists(helmet_model_path):
                self.helmet_model = YOLO(helmet_model_path)
                print("✅ Helmet detection model loaded")
            else:
                print("⚠️  Helmet model not found, using YOLOv8n as fallback")
                self.helmet_model = YOLO("yolov8n.pt")
            
            # Initialize triple riding detection model
            triple_riding_model_path = self.config["models"].get("triple_riding")
            if triple_riding_model_path and os.path.exists(triple_riding_model_path):
                self.triple_riding_model = YOLO(triple_riding_model_path)
                print("✅ Triple riding detection model loaded")
            else:
                print("⚠️  Triple riding model not found, using YOLOv8n as fallback")
                self.triple_riding_model = YOLO("yolov8n.pt")
                
        except Exception as e:
            print(f"❌ Error initializing models: {e}")
    
    def process_image(self, image_path, detection_types=None):
        """
        Process a single image with specified detection types
        """
        if detection_types is None:
            detection_types = ['license_plate', 'helmet', 'triple_riding', 'red_light']
        
        print(f"📸 Processing image: {os.path.basename(image_path)}")
        print(f"🔍 Detection types: {detection_types}")
        
        # Load image once for all detections
        image = cv2.imread(image_path)
        if image is None:
            print(f"❌ Could not load image: {image_path}")
            return None
        
        # Create annotated image for visualization
        annotated_image = image.copy()
        
        results = {}
        timestamp = datetime.now().isoformat()
        
        # License Plate Detection
        if 'license_plate' in detection_types:
            print("\n🚗 Processing License Plates...")
            lp_results = self.detect_license_plates(image_path, image)
            results['license_plates'] = lp_results
            
            # Annotate license plates on image
            for lp in lp_results:
                bbox = lp['bbox']
                text = lp['plate_text']
                x1, y1, x2, y2 = bbox
                cv2.rectangle(annotated_image, (int(x1), int(y1)), (int(x2), int(y2)), (0, 255, 0), 2)
                cv2.putText(annotated_image, text, (int(x1), int(y1-10)), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 0, 0), 2)
        
        # Helmet Detection
        if 'helmet' in detection_types:
            print("\n🛵 Processing Helmet Detection...")
            helmet_results = self.detect_helmets(image_path, image)
            results['helmets'] = helmet_results
            results['helmet_violations'] = getattr(self, 'helmet_violations_cache', [])
    
            # Annotate helmet detections on image
            for helmet in helmet_results:
                bbox = helmet.get('bbox')
                class_name = helmet.get('class', '')
                confidence = helmet.get('confidence', 0.0)
        
                if bbox and len(bbox) == 4:
                    x1, y1, x2, y2 = bbox
                    # Use red for violations, green for proper helmets
                    color = (0, 0, 255) if class_name.lower() in ["nohelmet", "without_helmet", "no_helmet"] else (0, 255, 0)
                    thickness = 3 if class_name.lower() in ["nohelmet", "without_helmet", "no_helmet"] else 2
            
                    cv2.rectangle(annotated_image, (int(x1), int(y1)), (int(x2), int(y2)), color, thickness)
                    label = f"{class_name} {confidence:.2f}"
                    cv2.putText(annotated_image, label, (int(x1), int(y1-10)), 
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
        
        # Triple Riding Detection - USING BALANCED LOGIC
        if 'triple_riding' in detection_types:
            print("\n🏍️  Processing Triple Riding Detection...")
            triple_riding_results = self.detect_triple_riding_balanced(image, annotated_image)
            results['triple_riding_violations'] = triple_riding_results
        
        # Red Light Violation Detection
        if 'red_light' in detection_types:
            print("\n🚦 Processing Red Light Violations...")
            red_light_results = self.detect_red_light_violations(image, annotated_image)
            results['red_light_violations'] = red_light_results
            
            # Draw stop line and traffic light ROI on annotated image
            self.draw_red_light_elements(annotated_image)
        
        # Combine and save results
        combined_results = self.combine_results(results, timestamp)
        self.save_results(combined_results, image_path, annotated_image)
        
        return combined_results
    
    def draw_red_light_elements(self, image):
        """Draw stop line and traffic light ROI on image for visualization"""
        try:
            # Draw stop line
            if self.red_light_detector.stop_line:
                start, end = self.red_light_detector.stop_line
                cv2.line(image, start, end, (0, 0, 255), 2)
                cv2.putText(image, "STOP LINE", (start[0], start[1]-10), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
            
            # Draw traffic light ROI
            if self.red_light_detector.traffic_light_roi:
                x, y, w, h = self.red_light_detector.traffic_light_roi
                cv2.rectangle(image, (x, y), (x+w, y+h), (255, 255, 0), 2)
                cv2.putText(image, "TRAFFIC LIGHT ROI", (x, y-10), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 0), 2)
                
        except Exception as e:
            print(f"⚠️  Error drawing red light elements: {e}")
    
    def detect_license_plates(self, image_path, image):
        """Detect and recognize license plates"""
        try:
            model_path = self.config["models"]["license_plate"]
            if os.path.exists(model_path):
                print(f"🔍 Using license plate model: {model_path}")
                
                detections = detect_single_image(
                    model_path, 
                    image_path, 
                    self.config["output_dirs"]["license_plates"]
                )
                return detections
            else:
                print(f"⚠️  License plate model not found at: {model_path}")
                return []
        except Exception as e:
            print(f"❌ License plate detection error: {e}")
            return []
    
    def detect_helmets(self, image_path, image):
        """Detect helmets using the actual helmet detection module with custom logic"""
        try:
            print(f"🔍 [HELMET] Calling actual detect_helmets function...")
        
            # Call your actual function with proper parameters
            results = detect_helmets(
                image_path=image_path,
                output_dir=self.config["output_dirs"]["helmets"],
                confidence=self.config["confidence_thresholds"]["helmet"]
            )
        
            print(f"🔍 [HELMET] Raw results from detect_helmets: {results}")
        
            # Return ALL detections for drawing, but also identify violations
            all_detections = []
            helmet_violations = []
        
            if results:
                for detection in results:
                    class_name = detection.get('class', '').lower()
                
                    # Add to all detections for drawing
                    all_detections.append(detection)
                
                    # Use YOUR custom logic from detect_helmet.py
                    if class_name in ["nohelmet", "without_helmet", "no_helmet"]:
                        print(f"🚨 HELMET VIOLATION DETECTED: {class_name}")
                        helmet_violations.append({
                            'class': detection.get('class', 'no_helmet'),
                            'confidence': detection.get('confidence', 0.0),
                            'bbox': detection.get('bbox', []),
                            'type': 'helmet_violation',
                            'timestamp': datetime.now().isoformat()
                        })
                    elif class_name == "helmet":
                        print(f"✅ Helmet detected (no violation): {class_name}")
        
            print(f"✅ [HELMET] Found {len(all_detections)} total detections, {len(helmet_violations)} violations")
        
            # Store violations separately for the results
            self.helmet_violations_cache = helmet_violations
        
            return all_detections  # Return all for drawing
        
        except Exception as e:
            print(f"❌ [HELMET] Error in helmet detection: {e}")
            import traceback
            traceback.print_exc()
            return []
    
    def detect_triple_riding_balanced(self, image, annotated_image):
        """Detect triple riding violations using balanced approach"""
        try:
            print("🏍️  Running balanced triple riding detection...")
            
            # Run detection with confidence threshold
            results = self.triple_riding_model(image, conf=0.5)
            
            violations = []
            
            for result in results:
                boxes = result.boxes.xyxy.cpu().numpy()
                class_ids = result.boxes.cls.cpu().numpy().astype(int)
                confidences = result.boxes.conf.cpu().numpy()
                
                motorcycles = []
                persons = []
                
                # ✅ FIXED: Correct class IDs for YOLOv8n COCO dataset
                for i, cls_id in enumerate(class_ids):
                    if cls_id == 3:  # ✅ FIXED: motorcycle in YOLO COCO (was 1)
                        motorcycles.append({
                            'bbox': boxes[i].tolist(),  # ✅ Convert numpy array to list
                            'confidence': float(confidences[i])  # ✅ Convert to Python float
                        })
                    elif cls_id == 0:  # ✅ person in YOLO COCO (correct)
                        persons.append({
                            'bbox': boxes[i].tolist(),  # ✅ Convert numpy array to list
                            'confidence': float(confidences[i])  # ✅ Convert to Python float
                        })
                
                print(f"🔍 Found {len(motorcycles)} motorcycles and {len(persons)} persons")
                
                # Triple riding analysis using balanced logic
                for i, moto in enumerate(motorcycles):
                    # ✅ Convert bbox to list and extract coordinates
                    moto_bbox = moto['bbox']
                    mx1, my1, mx2, my2 = moto_bbox
                    moto_width = mx2 - mx1
                    moto_height = my2 - my1
                    
                    # Count likely riders using balanced criteria
                    riders = []
                    rider_boxes = []
                    
                    for person in persons:
                        person_bbox = person['bbox']
                        px1, py1, px2, py2 = person_bbox
                        person_center_x = (px1 + px2) / 2
                        person_center_y = (py1 + py2) / 2
                        
                        moto_center_x = (mx1 + mx2) / 2
                        
                        # Balanced criteria for rider detection
                        horizontal_bound = moto_width * 0.8  # 80% wider than bike
                        vertical_upper_bound = my1 - moto_height * 0.2  # Allow some above
                        vertical_lower_bound = my2 + moto_height * 0.3  # Allow some below
                        
                        if (moto_center_x - horizontal_bound <= person_center_x <= moto_center_x + horizontal_bound and
                            vertical_upper_bound <= person_center_y <= vertical_lower_bound):
                            
                            riders.append(person)
                            rider_boxes.append(person_bbox)  # Already converted to list
                    
                    rider_count = len(riders)
                    
                    # Log detection status
                    status = "✅ Single rider"
                    if rider_count == 2:
                        status = "⚠️ Double riding"
                    elif rider_count >= 3:
                        status = "🚨 TRIPLE RIDING DETECTED!"
                        
                        violation = {
                            'type': 'triple_riding',
                            'motorbike_bbox': moto_bbox,  # Already converted to list
                            'person_count': rider_count,
                            'persons': riders,
                            'rider_boxes': rider_boxes,  # Already converted to list
                            'confidence': moto['confidence'],
                            'timestamp': datetime.now().isoformat()
                        }
                        violations.append(violation)
                        
                        print(f"🚨 TRIPLE RIDING! Motorcycle {i+1} has {rider_count} riders")
                        
                        # ✅ FIXED: Convert bbox coordinates to integers for OpenCV
                        cv2.rectangle(annotated_image, 
                                    (int(mx1), int(my1)), 
                                    (int(mx2), int(my2)), 
                                    (0, 0, 255), 3)
                        cv2.putText(annotated_image, f"TRIPLE RIDING ({rider_count} people)", 
                                  (int(mx1), int(my1-10)), 
                                  cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                        
                        # ✅ FIXED: Convert rider bbox coordinates to integers for OpenCV
                        for rider_bbox in rider_boxes:
                            rx1, ry1, rx2, ry2 = rider_bbox
                            cv2.rectangle(annotated_image, 
                                        (int(rx1), int(ry1)), 
                                        (int(rx2), int(ry2)), 
                                        (255, 0, 0), 2)
                    
                    print(f"   Motorcycle {i+1}: {rider_count} rider(s) - {status}")
        
            print(f"✅ Balanced triple riding detection complete. Violations found: {len(violations)}")
            return violations
            
        except Exception as e:
            print(f"❌ Balanced triple riding detection error: {e}")
            import traceback
            traceback.print_exc()
            return []
    
    def detect_red_light_violations(self, image, annotated_image):
        """Detect red light violations using enhanced approach"""
        try:
            violations, light_state, confidence = self.red_light_detector.detect_violations(image)
            
            print(f"🚦 Traffic Light State: {light_state} (confidence: {confidence:.2f})")
            print(f"🚨 Red Light Violations: {len(violations)}")
            
            # Draw violations on image
            for violation in violations:
                bbox = violation['bbox']
                x1, y1, x2, y2 = bbox
                cv2.rectangle(annotated_image, (int(x1), int(y1)), (int(x2), int(y2)), (0, 0, 255), 3)
                cv2.putText(annotated_image, "RED LIGHT VIOLATION", (int(x1), int(y1-10)), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
            
            return violations
            
        except Exception as e:
            print(f"❌ Red light violation detection error: {e}")
            return []
    
    def combine_results(self, results, timestamp):
        """Combine results from all detection systems - ensure JSON serializable"""
        # Helper function to make sure all data is JSON serializable
        def make_json_serializable(obj):
            if isinstance(obj, (np.integer, np.int64)):
                return int(obj)
            elif isinstance(obj, (np.floating, np.float32, np.float64)):
                return float(obj)
            elif isinstance(obj, np.ndarray):
                return obj.tolist()
            elif isinstance(obj, dict):
                return {k: make_json_serializable(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [make_json_serializable(item) for item in obj]
            else:
                return obj
        
        combined = {
            "timestamp": timestamp,
            "license_plates": make_json_serializable(results.get('license_plates', [])),
            "helmet_violations": make_json_serializable(results.get('helmets', [])),
            "triple_riding_violations": make_json_serializable(results.get('triple_riding_violations', [])),
            "red_light_violations": make_json_serializable(results.get('red_light_violations', [])),
            "preprocessing_applied": self.config["preprocessing"]["apply_binary_preprocessing"],
            "summary": {
                "total_license_plates": len(results.get('license_plates', [])),
                "total_helmet_violations": len(results.get('helmets', [])),
                "total_triple_riding_violations": len(results.get('triple_riding_violations', [])),
                "total_red_light_violations": len(results.get('red_light_violations', []))
            }
        }
        return combined
    
    def save_results(self, results, image_path, annotated_image=None):
        """Save detection results and annotated image"""
        try:
            output_dir = self.config["output_dirs"]["combined"]
            base_name = Path(image_path).stem
            
            # Save JSON results
            json_path = os.path.join(output_dir, f"{base_name}_results.json")
            with open(json_path, 'w') as f:
                json.dump(results, f, indent=2)
            
            # Save annotated image
            if annotated_image is not None:
                img_path = os.path.join(output_dir, f"{base_name}_annotated.jpg")
                cv2.imwrite(img_path, annotated_image)
                print(f"💾 Annotated image saved to: {img_path}")
            
            print(f"💾 Results saved to: {json_path}")
            
        except Exception as e:
            print(f"❌ Error saving results: {e}")
    
    def get_detection_summary(self):
        """Get summary of all detections"""
        summary = {
            "total_processed": len(self.detection_results["timestamps"]),
            "license_plates_found": len(self.detection_results["license_plates"]),
            "helmet_violations": len(self.detection_results["helmet_violations"]),
            "triple_riding_violations": len(self.detection_results["triple_riding_violations"]),
            "red_light_violations": len(self.detection_results["red_light_violations"]),
            "binary_preprocessing_applied": self.config["preprocessing"]["apply_binary_preprocessing"],
            "last_processed": self.detection_results["timestamps"][-1] if self.detection_results["timestamps"] else None
        }
        return summary


def main():
    """Main function to demonstrate the central detection manager"""
    # Initialize the central manager
    manager = CentralDetectionManager()
    
    # Verify model paths
    print("\n🔍 Verifying model paths...")
    config = manager.config
    print(f"License plate model: {os.path.exists(config['models']['license_plate'])}")
    print(f"Helmet model: {os.path.exists(config['models']['helmet'])}")
    print(f"Triple riding model: {os.path.exists(config['models'].get('triple_riding', ''))}")
    print(f"Traffic light model: {os.path.exists('D:/Codes/Miniproj/models/traffic_light_classifier.h5')}")
    print(f"Binary preprocessing enabled: {config['preprocessing']['apply_binary_preprocessing']}")
    
    # Example usage
    image_path = r"D:\Codes\Miniproj\detect2.jpg"
    
    if os.path.exists(image_path):
        # Process image with all detection types
        results = manager.process_image(
            image_path, 
            detection_types=['license_plate', 'helmet', 'triple_riding', 'red_light']
        )
        
        # Print summary
        if results:
            print("\n" + "="*50)
            print("📊 DETECTION SUMMARY")
            print("="*50)
            print(f"License Plates Found: {results['summary']['total_license_plates']}")
            print(f"Helmet Violations: {results['summary']['total_helmet_violations']}")
            print(f"Triple Riding Violations: {results['summary']['total_triple_riding_violations']}")
            print(f"Red Light Violations: {results['summary']['total_red_light_violations']}")
            print(f"Binary Preprocessing Applied: {results['preprocessing_applied']}")
            print(f"Timestamp: {results['timestamp']}")
    else:
        print(f"❌ Test image not found: {image_path}")
        print("💡 Please update the image_path in main() function")


if __name__ == "__main__":
    main()
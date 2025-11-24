# central_detection_manager.py
import cv2
import os
import json
import time
from datetime import datetime
from pathlib import Path
from ultralytics import YOLO
import sys

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

try:
    from red_light_violation import RedLightViolationDetector
    print("✅ Red light violation module imported successfully")
except ImportError as e:
    print(f"❌ Error importing red light violation module: {e}")
    # Create a proper fallback class
    class RedLightViolationDetector:
        def __init__(self, model_path=None, class_names_path=None):
            print("⚠️  Using fallback red light violation detector")
            self.stop_line = None
            self.traffic_light_roi = None
        
        def set_stop_line(self, start_point, end_point):
            self.stop_line = (start_point, end_point)
            print(f"✅ Stop line set: {start_point} to {end_point}")
        
        def set_traffic_light_roi(self, x, y, width, height):
            self.traffic_light_roi = (x, y, width, height)
            print(f"✅ Traffic light ROI set: {self.traffic_light_roi}")
        
        def detect_traffic_light_state(self, frame):
            return "unknown", 0.0
        
        def detect_violations(self, frame, vehicle_detections):
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
        self.red_light_detector = None
        self.helmet_model = None
        
        # Initialize models based on config
        self.initialize_models()
        
        # Detection results storage
        self.detection_results = {
            "license_plates": [],
            "helmet_violations": [],
            "red_light_violations": [],
            "timestamps": []
        }
        
        print("✅ Central Detection Manager Ready!")
    
    def load_config(self, config_path):
        """Load configuration from JSON file"""
        default_config = {
            "models": {
                "license_plate": "D:/Codes/Miniproj/license_plate_detection/models/best.pt",
                "helmet": "D:/Codes/Miniproj/runs/detect/helmet_detection/weights/best.pt",
                "red_light": {
                    "model": "D:/Codes/Miniproj/models/traffic_light_classifier.h5",
                    "class_names": "D:/Codes/Miniproj/models/class_names.json"
                }
            },
            "output_dirs": {
                "license_plates": "results/license_plates",
                "helmets": "results/helmet_detection",
                "red_light": "results/red_light_violations",
                "combined": "results/combined"
            },
            "confidence_thresholds": {
                "license_plate": 0.5,
                "helmet": 0.25,
                "red_light": 0.7
            },
            "violation_settings": {
                "stop_line": {"start": [100, 400], "end": [600, 400]},
                "traffic_light_roi": [50, 50, 100, 200]
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
            
            # Initialize red light violation detector (even without tensorflow)
            red_light_config = self.config["models"]["red_light"]
            try:
                if (os.path.exists(red_light_config["model"]) and 
                    os.path.exists(red_light_config["class_names"])):
                    self.red_light_detector = RedLightViolationDetector(
                        red_light_config["model"],
                        red_light_config["class_names"]
                    )
                    
                    # Configure stop line and ROI
                    violation_settings = self.config["violation_settings"]
                    stop_line = violation_settings["stop_line"]
                    tl_roi = violation_settings["traffic_light_roi"]
                    
                    self.red_light_detector.set_stop_line(
                        tuple(stop_line["start"]),
                        tuple(stop_line["end"])
                    )
                    self.red_light_detector.set_traffic_light_roi(*tl_roi)
                    print("✅ Red light violation detector initialized")
                else:
                    print("⚠️  Red light detection models not found, using fallback")
                    self.red_light_detector = RedLightViolationDetector()
            except Exception as e:
                print(f"⚠️  Red light detector initialization failed: {e}")
                self.red_light_detector = RedLightViolationDetector()
                
        except Exception as e:
            print(f"❌ Error initializing models: {e}")
    
    def process_image(self, image_path, detection_types=None):
        """
        Process a single image with specified detection types
        
        Args:
            image_path: Path to the input image
            detection_types: List of detection types to perform
                           ['license_plate', 'helmet', 'red_light']
        """
        if detection_types is None:
            detection_types = ['license_plate', 'helmet']
        
        print(f"📸 Processing image: {os.path.basename(image_path)}")
        print(f"🔍 Detection types: {detection_types}")
        
        # Load image once for all detections
        image = cv2.imread(image_path)
        if image is None:
            print(f"❌ Could not load image: {image_path}")
            return None
        
        results = {}
        timestamp = datetime.now().isoformat()
        
        # License Plate Detection
        if 'license_plate' in detection_types:
            print("\n🚗 Processing License Plates...")
            lp_results = self.detect_license_plates(image_path, image)
            results['license_plates'] = lp_results
        
        # Helmet Detection
        if 'helmet' in detection_types:
            print("\n🛵 Processing Helmet Detection...")
            helmet_results = self.detect_helmets(image_path, image)
            results['helmets'] = helmet_results
        
        # Red Light Violation Detection (requires vehicle tracking)
        if 'red_light' in detection_types and self.red_light_detector:
            print("\n🚦 Processing Red Light Violations...")
            red_light_results = self.detect_red_light_violations(image_path, image)
            results['red_light_violations'] = red_light_results
        
        # Combine and save results
        combined_results = self.combine_results(results, timestamp)
        self.save_results(combined_results, image_path, image)
        
        return combined_results
    
    def detect_license_plates(self, image_path, image):
        """Detect and recognize license plates using your specialized module"""
        try:
            model_path = self.config["models"]["license_plate"]
            if os.path.exists(model_path):
                print(f"🔍 Using license plate model: {model_path}")
                # Use your existing license plate detection function
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
        """Detect helmets using the helmet detection module"""
        try:
            # Use your existing helmet detection function
            detect_helmets(
                image_path=image_path,
                output_dir=self.config["output_dirs"]["helmets"]
            )
            
            # For now, return placeholder results
            return [{"status": "helmet_detection_completed"}]
            
        except Exception as e:
            print(f"❌ Helmet detection error: {e}")
            return []
    
    def detect_red_light_violations(self, image_path, image):
        """Detect red light violations"""
        try:
            if not self.red_light_detector:
                return []
            
            # First detect vehicles (you might want to use YOLO for this)
            vehicle_detections = self.detect_vehicles(image)
            
            # Check for violations
            violations, light_state, confidence = self.red_light_detector.detect_violations(
                image, vehicle_detections
            )
            
            print(f"🚦 Traffic Light State: {light_state} (confidence: {confidence:.2f})")
            print(f"🚨 Red Light Violations: {len(violations)}")
            
            return violations
            
        except Exception as e:
            print(f"❌ Red light violation detection error: {e}")
            return []
    
    def detect_vehicles(self, image):
        """Detect vehicles for red light violation checking"""
        vehicle_detections = []
        
        try:
            # Use YOLO for vehicle detection
            vehicle_model = YOLO("yolov8n.pt")
            results = vehicle_model(image)
            
            for result in results:
                for box in result.boxes:
                    cls = int(box.cls.item())
                    class_name = result.names[cls]
                    
                    # Filter for vehicles
                    if class_name.lower() in ['car', 'motorcycle', 'bus', 'truck']:
                        bbox = box.xyxy[0].cpu().numpy().astype(int)
                        vehicle_detections.append({
                            'track_id': len(vehicle_detections),  # Simple ID assignment
                            'bbox': bbox.tolist(),
                            'class': class_name,
                            'confidence': float(box.conf[0].cpu().numpy())
                        })
                        
        except Exception as e:
            print(f"⚠️  Vehicle detection error: {e}")
        
        return vehicle_detections
    
    def combine_results(self, results, timestamp):
        """Combine results from all detection systems"""
        combined = {
            "timestamp": timestamp,
            "license_plates": results.get('license_plates', []),
            "helmet_violations": results.get('helmets', []),
            "red_light_violations": results.get('red_light_violations', []),
            "summary": {
                "total_license_plates": len(results.get('license_plates', [])),
                "total_helmet_violations": len(results.get('helmets', [])),
                "total_red_light_violations": len(results.get('red_light_violations', []))
            }
        }
        return combined
    
    def save_results(self, results, image_path, annotated_image=None):
        """Save detection results and annotated image"""
        try:
            # Save JSON results
            output_dir = self.config["output_dirs"]["combined"]
            base_name = Path(image_path).stem
            
            json_path = os.path.join(output_dir, f"{base_name}_results.json")
            with open(json_path, 'w') as f:
                json.dump(results, f, indent=2)
            
            # Save annotated image if provided
            if annotated_image is not None:
                image_path = os.path.join(output_dir, f"{base_name}_annotated.jpg")
                cv2.imwrite(image_path, annotated_image)
            
            print(f"💾 Results saved to: {json_path}")
            
        except Exception as e:
            print(f"❌ Error saving results: {e}")
    
    def get_detection_summary(self):
        """Get summary of all detections"""
        summary = {
            "total_processed": len(self.detection_results["timestamps"]),
            "license_plates_found": len(self.detection_results["license_plates"]),
            "helmet_violations": len(self.detection_results["helmet_violations"]),
            "red_light_violations": len(self.detection_results["red_light_violations"]),
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
    print(f"Red light model: {os.path.exists(config['models']['red_light']['model'])}")
    print(f"Class names: {os.path.exists(config['models']['red_light']['class_names'])}")
    
    # Example usage
    image_path = r"D:\Codes\Miniproj\detect2.jpg"
    
    if os.path.exists(image_path):
        # Process image with all detection types
        results = manager.process_image(
            image_path, 
            detection_types=['license_plate', 'helmet']  # Start with these two
        )
        
        # Print summary
        if results:
            print("\n" + "="*50)
            print("📊 DETECTION SUMMARY")
            print("="*50)
            print(f"License Plates Found: {results['summary']['total_license_plates']}")
            print(f"Helmet Violations: {results['summary']['total_helmet_violations']}")
            print(f"Red Light Violations: {results['summary']['total_red_light_violations']}")
            print(f"Timestamp: {results['timestamp']}")
    else:
        print(f"❌ Test image not found: {image_path}")
        print("💡 Please update the image_path in main() function")


if __name__ == "__main__":
    main()
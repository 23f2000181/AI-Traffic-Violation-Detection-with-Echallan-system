import cv2
import numpy as np
import json
from tensorflow import keras

class RedLightViolationDetector:
    def __init__(self, model_path, class_names_path):
        # Load trained traffic light classifier
        self.tl_classifier = keras.models.load_model(model_path)
        with open(class_names_path, 'r') as f:
            self.class_names = json.load(f)
        
        # Violation tracking
        self.stop_line = None
        self.traffic_light_roi = None
        self.vehicle_tracks = {}
        self.violations_log = []
        
        print("🚦 Red Light Violation Detector Initialized!")
    
    def set_stop_line(self, start_point, end_point):
        """Define the stop line coordinates"""
        self.stop_line = (start_point, end_point)
    
    def set_traffic_light_roi(self, x, y, width, height):
        """Define traffic light region of interest"""
        self.traffic_light_roi = (x, y, width, height)
    
    def detect_traffic_light_state(self, frame):
        """Detect traffic light state in the defined ROI"""
        if self.traffic_light_roi is None:
            return "unknown", 0.0
        
        x, y, w, h = self.traffic_light_roi
        
        # Extract ROI
        tl_region = frame[y:y+h, x:x+w]
        if tl_region.size == 0:
            return "unknown", 0.0
        
        # Preprocess for model
        tl_resized = cv2.resize(tl_region, (64, 64))
        tl_normalized = tl_resized / 255.0
        tl_input = np.expand_dims(tl_normalized, axis=0)
        
        # Predict
        predictions = self.tl_classifier.predict(tl_input, verbose=0)
        predicted_class = np.argmax(predictions[0])
        confidence = np.max(predictions[0])
        
        if confidence > 0.7:
            return self.class_names[predicted_class], confidence
        else:
            return "unknown", confidence
    
    def is_vehicle_crossing_line(self, vehicle_bbox, previous_bbox):
        """Check if vehicle crossed the stop line"""
        if self.stop_line is None or previous_bbox is None:
            return False
        
        line_start, line_end = self.stop_line
        line_y = line_start[1]  # Assuming horizontal line
        
        current_bottom = vehicle_bbox[3]  # Bottom y-coordinate
        previous_bottom = previous_bbox[3]
        
        # Check if crossed from above to below the line
        if previous_bottom < line_y and current_bottom >= line_y:
            return True
        return False
    
    def detect_violations(self, frame, vehicle_detections):
        """Main function to detect red light violations"""
        violations = []
        
        # Detect traffic light state
        light_state, confidence = self.detect_traffic_light_state(frame)
        
        # Only check for violations if light is red
        if light_state == "red":
            for vehicle in vehicle_detections:
                vehicle_id = vehicle['track_id']
                current_bbox = vehicle['bbox']
                
                # Check if this vehicle has previous position
                if vehicle_id in self.vehicle_tracks:
                    previous_bbox = self.vehicle_tracks[vehicle_id]
                    
                    # Check if vehicle crossed stop line during red light
                    if self.is_vehicle_crossing_line(current_bbox, previous_bbox):
                        violation_data = {
                            'vehicle_id': vehicle_id,
                            'bbox': current_bbox,
                            'violation_type': 'RED_LIGHT',
                            'light_state': light_state,
                            'confidence': confidence
                        }
                        violations.append(violation_data)
                        self.violations_log.append(violation_data)
                
                # Update vehicle track
                self.vehicle_tracks[vehicle_id] = current_bbox
        
        return violations, light_state, confidence
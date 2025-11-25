import os
import sys
import time
import shutil
from datetime import datetime
from pathlib import Path

# Add current and parent directory to path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, current_dir)
sys.path.insert(0, parent_dir)

from central_detection_manager import CentralDetectionManager
import config as Config_module
Config = Config_module.Config

class DetectionService:
    """Service layer for image detection processing"""
    
    def __init__(self):
        self.manager = None
        self.initialize_manager()
    
    def initialize_manager(self):
        """Initialize the CentralDetectionManager"""
        try:
            self.manager = CentralDetectionManager(Config.CONFIG_JSON_PATH)
            print("✅ CentralDetectionManager initialized")
        except Exception as e:
            print(f"❌ Error initializing CentralDetectionManager: {e}")
            raise
    
    def process_uploaded_image(self, image_path):
        """
        Process an uploaded image with CentralDetectionManager
        
        Args:
            image_path: Path to the uploaded image
            
        Returns:
            dict: Processing results formatted for frontend
        """
        try:
            start_time = time.time()
            
            # Process image with all detection types
            results = self.manager.process_image(
                image_path,
                detection_types=['license_plate', 'helmet', 'red_light']
            )
            
            processing_time = time.time() - start_time
            
            # Find the annotated image
            processed_image_path = self._find_processed_image(image_path)
            
            # Move processed image to processed folder
            if processed_image_path and os.path.exists(processed_image_path):
                dest_path = os.path.join(
                    Config.PROCESSED_FOLDER,
                    os.path.basename(processed_image_path)
                )
                shutil.copy2(processed_image_path, dest_path)
                processed_image_path = dest_path
            
            # Format results for frontend
            formatted_results = self._format_results(
                results,
                image_path,
                processed_image_path,
                processing_time
            )
            
            return formatted_results
            
        except Exception as e:
            print(f"❌ Error processing image: {e}")
            raise
    
    def _find_processed_image(self, original_path):
        """Find the annotated/processed image"""
        try:
            # Check in combined results directory
            base_name = Path(original_path).stem
            combined_dir = "results/combined"
            
            annotated_path = os.path.join(combined_dir, f"{base_name}_annotated.jpg")
            
            if os.path.exists(annotated_path):
                return annotated_path
            
            return None
        except Exception as e:
            print(f"⚠️ Error finding processed image: {e}")
            return None
    
    def _format_results(self, results, image_path, processed_image_path, processing_time):
        """Format detection results for frontend consumption"""
        try:
            # Extract detection data
            license_plates = results.get('license_plates', [])
            helmet_violations = results.get('helmet_violations', [])
            red_light_violations = results.get('red_light_violations', [])
            
            # Format license plates
            formatted_lp = []
            for lp in license_plates:
                formatted_lp.append({
                    'plate_text': lp.get('plate_text', 'UNKNOWN'),
                    'confidence': float(lp.get('confidence', 0.0)),
                    'bbox': lp.get('bbox', []),
                    'timestamp': datetime.utcnow().isoformat()
                })
            
            # Format helmet violations
            formatted_helmets = []
            for helmet in helmet_violations:
                if isinstance(helmet, dict):
                    formatted_helmets.append({
                        'type': helmet.get('class', helmet.get('type', 'helmet_violation')),
                        'confidence': float(helmet.get('confidence', 0.0)),
                        'bbox': helmet.get('bbox', []),
                        'timestamp': datetime.utcnow().isoformat()
                    })
            
            # Format red light violations
            formatted_red_light = []
            for violation in red_light_violations:
                if isinstance(violation, dict):
                    formatted_red_light.append({
                        'vehicle_type': violation.get('class', 'vehicle'),
                        'confidence': float(violation.get('confidence', 0.0)),
                        'bbox': violation.get('bbox', []),
                        'light_state': 'red',
                        'timestamp': datetime.utcnow().isoformat()
                    })
            
            # Create violation record
            violation_record = {
                'timestamp': datetime.utcnow(),
                'image_path': image_path,
                'processed_image_path': processed_image_path,
                'detection_results': {
                    'license_plates': formatted_lp,
                    'helmet_violations': formatted_helmets,
                    'red_light_violations': formatted_red_light
                },
                'processing_time': processing_time,
                'status': 'processed'
            }
            
            return violation_record
            
        except Exception as e:
            print(f"❌ Error formatting results: {e}")
            raise

# Global service instance
detection_service = DetectionService()

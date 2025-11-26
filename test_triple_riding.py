import torch
from ultralytics import YOLO
import cv2
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image
import os

class TripleRidingDetector:
    def __init__(self, model_path='D:/Codes/Miniproj/triple_riding/yolov8n.pt'):
        """Initialize the detector with YOLO model"""
        try:
            self.model = YOLO(model_path)
            print(f"✅ Triple Riding Detector initialized with model: {model_path}")
        except Exception as e:
            print(f"❌ Error loading model: {e}")
            raise
    
    def balanced_triple_riding_detection(self, image_path, confidence=0.5, save_result=True):
        """
        Balanced triple riding detection - detects people actually sitting on motorcycles
        Returns: result_image, violation_count, detailed_results
        """
        try:
            # Check if image exists
            if not os.path.exists(image_path):
                print(f"❌ Image not found: {image_path}")
                return None, 0, {}
            
            print(f"🔍 Processing image: {image_path}")
            
            # Run detection
            results = self.model(image_path, conf=confidence)
            
            if len(results) == 0:
                print("❌ No objects detected in the image")
                return None, 0, {}
            
            result = results[0]
            boxes = result.boxes.xyxy.cpu().numpy()
            class_ids = result.boxes.cls.cpu().numpy().astype(int)
            confidences = result.boxes.conf.cpu().numpy()
            
            motorcycles = []
            persons = []
            
            # Organize detections
            for i, cls_id in enumerate(class_ids):
                if cls_id == 3:  # motorcycle
                    motorcycles.append({
                        'bbox': boxes[i],
                        'confidence': confidences[i]
                    })
                elif cls_id == 0:  # person
                    persons.append({
                        'bbox': boxes[i],
                        'confidence': confidences[i]
                    })
            
            print(f"✅ Found {len(motorcycles)} motorcycles and {len(persons)} persons")
            
            triple_riding_cases = []
            motorcycle_analyses = []
            
            # Analyze each motorcycle
            for i, moto in enumerate(motorcycles):
                mx1, my1, mx2, my2 = moto['bbox']
                moto_width = mx2 - mx1
                moto_height = my2 - my1
                
                # Count likely riders
                riders = []
                rider_boxes = []
                
                for person in persons:
                    px1, py1, px2, py2 = person['bbox']
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
                        rider_boxes.append(person['bbox'])
                
                rider_count = len(riders)
                analysis = {
                    'motorcycle_id': i,
                    'rider_count': rider_count,
                    'motorcycle_bbox': moto['bbox'],
                    'rider_boxes': rider_boxes,
                    'confidence': moto['confidence']
                }
                motorcycle_analyses.append(analysis)
                
                status = "✅ Single rider"
                if rider_count == 2:
                    status = "⚠️ Double riding"
                elif rider_count >= 3:
                    status = "🚨 TRIPLE RIDING DETECTED!"
                    triple_riding_cases.append(analysis)
                
                print(f"   Motorcycle {i+1}: {rider_count} rider(s) - {status}")
            
            # Create detailed results
            detailed_results = {
                'total_motorcycles': len(motorcycles),
                'total_persons': len(persons),
                'triple_riding_violations': len(triple_riding_cases),
                'motorcycle_analyses': motorcycle_analyses,
                'violations': triple_riding_cases
            }
            
            # Display summary
            print(f"\n" + "="*60)
            print("📊 DETECTION SUMMARY:")
            print(f"   Total motorcycles: {len(motorcycles)}")
            print(f"   Total persons: {len(persons)}")
            print(f"   Triple riding violations: {len(triple_riding_cases)}")
            
            if triple_riding_cases:
                print("   🚨 VIOLATIONS FOUND! 🚨")
            else:
                print("   ✅ No violations detected")
            print("="*60)
            
            # Generate result image
            result_image = self._create_result_image(results, triple_riding_cases, save_result)
            
            return result_image, len(triple_riding_cases), detailed_results
            
        except Exception as e:
            print(f"❌ Error during detection: {e}")
            return None, 0, {}
    
    def _create_result_image(self, results, violations, save_result=True):
        """Create and save the result image with annotations"""
        try:
            for r in results:
                im_array = r.plot()  # Get image with default bounding boxes
                
                # Convert to PIL Image for additional annotations
                pil_image = Image.fromarray(im_array[..., ::-1])
                
                # Create matplotlib figure for better annotations
                plt.figure(figsize=(15, 10))
                plt.imshow(np.array(pil_image))
                
                # Add custom annotations for violations
                for violation in violations:
                    mx1, my1, mx2, my2 = violation['motorcycle_bbox']
                    
                    # Draw highlighted red box around violating motorcycle
                    rect = plt.Rectangle((mx1, my1), mx2-mx1, my2-my1, 
                                       linewidth=4, edgecolor='red', facecolor='none')
                    plt.gca().add_patch(rect)
                    
                    # Add violation text
                    plt.text(mx1, my1 - 20, f'TRIPLE RIDING: {violation["rider_count"]} people', 
                            bbox=dict(boxstyle="round,pad=0.3", facecolor='red', alpha=0.9),
                            fontsize=12, color='white', weight='bold')
                
                plt.axis('off')
                title = f"Triple Riding Detection - Violations: {len(violations)}"
                if violations:
                    title += " 🚨"
                plt.title(title, fontsize=16, fontweight='bold')
                plt.tight_layout()
                
                # Save result
                if save_result:
                    output_path = 'triple_riding_result.jpg'
                    plt.savefig(output_path, dpi=150, bbox_inches='tight')
                    print(f"💾 Result saved as: {output_path}")
                
                plt.show()
                
                return output_path if save_result else None
                
        except Exception as e:
            print(f"❌ Error creating result image: {e}")
            return None

def main():
    """Example usage of the TripleRidingDetector"""
    
    # Initialize detector
    detector = TripleRidingDetector()
    
    # Example usage with an image
    image_path = "D:/Codes/Miniproj/new5.jpg"  # Replace with your image path
    
    if os.path.exists(image_path):
        result_image, violations, details = detector.balanced_triple_riding_detection(image_path)
        
        if result_image:
            print(f"\n🎉 Detection completed!")
            print(f"📁 Result image: {result_image}")
            print(f"🚨 Violations found: {violations}")
    else:
        print(f"❌ Test image not found: {image_path}")
        print("💡 Please update the image_path variable with your image path")

if __name__ == "__main__":
    main()
# detect_triple_riding.py
import argparse
import cv2
import os
from pathlib import Path
from ultralytics import YOLO

def detect_triple_riding(weights, images, output):
    """Detect triple riding violations"""
    
    # Load model
    model = YOLO(weights)
    print(f"✅ Model loaded: {weights}")
    print(f"📁 Classes: {model.names}")
    
    # Create output directory
    os.makedirs(output, exist_ok=True)
    
    # Handle single image or directory
    if os.path.isfile(images):
        image_paths = [images]
    else:
        image_paths = [os.path.join(images, f) for f in os.listdir(images) 
                      if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
    
    print(f"🔍 Processing {len(image_paths)} images...")
    
    for image_path in image_paths:
        print(f"\n📸 Processing: {os.path.basename(image_path)}")
        
        # Load image
        image = cv2.imread(image_path)
        if image is None:
            print(f"❌ Could not load: {image_path}")
            continue
        
        # Run detection
        results = model(image, conf=0.3)
        
        persons = []
        motorbikes = []
        
        for result in results:
            for box in result.boxes:
                cls = int(box.cls.item())
                confidence = float(box.conf[0].cpu().numpy())
                bbox = box.xyxy[0].cpu().numpy().astype(int)
                
                if cls == 0:  # Person
                    persons.append({
                        'bbox': bbox.tolist(),
                        'confidence': confidence
                    })
                elif cls == 1:  # Motorbike
                    motorbikes.append({
                        'bbox': bbox.tolist(),
                        'confidence': confidence
                    })
        
        print(f"   👤 Persons: {len(persons)}, 🏍️ Motorbikes: {len(motorbikes)}")
        
        # Check for triple riding
        violations = []
        for motorbike in motorbikes:
            mb_bbox = motorbike['bbox']
            
            # Count persons near this motorbike
            persons_on_bike = []
            for person in persons:
                if is_person_on_motorbike(person['bbox'], mb_bbox):
                    persons_on_bike.append(person)
            
            # Triple riding = 3+ persons
            if len(persons_on_bike) >= 3:
                violations.append({
                    'motorbike_bbox': mb_bbox,
                    'person_count': len(persons_on_bike)
                })
                print(f"   🚨 TRIPLE RIDING DETECTED! ({len(persons_on_bike)} persons)")
        
        # Create annotated image
        annotated_image = image.copy()
        
        # Draw detections
        for person in persons:
            x1, y1, x2, y2 = person['bbox']
            cv2.rectangle(annotated_image, (x1, y1), (x2, y2), (255, 0, 0), 2)
        
        for motorbike in motorbikes:
            x1, y1, x2, y2 = motorbike['bbox']
            cv2.rectangle(annotated_image, (x1, y1), (x2, y2), (0, 255, 0), 2)
        
        # Highlight violations
        for violation in violations:
            x1, y1, x2, y2 = violation['motorbike_bbox']
            cv2.rectangle(annotated_image, (x1, y1), (x2, y2), (0, 0, 255), 3)
            cv2.putText(annotated_image, f"TRIPLE RIDING ({violation['person_count']})", 
                       (x1, y1-10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
        
        # Save result
        output_path = os.path.join(output, f"result_{os.path.basename(image_path)}")
        cv2.imwrite(output_path, annotated_image)
        print(f"   💾 Saved: {output_path}")

def is_person_on_motorbike(person_bbox, motorbike_bbox):
    """Check if person is on/near motorbike"""
    p_x1, p_y1, p_x2, p_y2 = person_bbox
    m_x1, m_y1, m_x2, m_y2 = motorbike_bbox
    
    # Calculate centers
    p_center_x = (p_x1 + p_x2) / 2
    p_center_y = (p_y1 + p_y2) / 2
    m_center_x = (m_x1 + m_x2) / 2
    m_center_y = (m_y1 + m_y2) / 2
    
    # Check distance
    distance = ((p_center_x - m_center_x)**2 + (p_center_y - m_center_y)**2)**0.5
    m_width = m_x2 - m_x1
    
    return distance < (m_width * 1.5)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Triple Riding Detection')
    parser.add_argument('--weights', type=str, required=True, help='Model weights path')
    parser.add_argument('--images', type=str, required=True, help='Image or directory path')
    parser.add_argument('--output', type=str, required=True, help='Output directory')
    
    args = parser.parse_args()
    
    detect_triple_riding(args.weights, args.images, args.output)
"""
Debug triple riding detection to see what's happening
"""
import sys
import os
import cv2
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ultralytics import YOLO

def debug_triple_riding():
    """Debug triple riding model directly"""
    print("="*70)
    print("🔬 DEBUGGING TRIPLE RIDING DETECTION")
    print("="*70)
    
    model_path = "D:/Codes/Miniproj/triple_riding/yolov8n.pt"
    test_image = "D:/Codes/Miniproj/new5.jpg"    
    if not os.path.exists(model_path):
        print(f"❌ Model not found: {model_path}")
        return
    
    if not os.path.exists(test_image):
        print(f"❌ Test image not found: {test_image}")
        return
    
    print(f"\n1️⃣ Loading model: {model_path}")
    model = YOLO(model_path)
    print(f"✅ Model loaded")
    print(f"   Model classes: {model.names}")
    
    print(f"\n2️⃣ Running detection on: {test_image}")
    image = cv2.imread(test_image)
    results = model(test_image, conf=0.3)  # Lower confidence for debugging
    
    print(f"\n3️⃣ Analyzing results...")
    
    for i, result in enumerate(results):
        print(f"\n   Result {i+1}:")
        print(f"   Total detections: {len(result.boxes)}")
        
        persons = []
        motorbikes = []
        
        for j, box in enumerate(result.boxes):
            cls = int(box.cls.item())
            conf = float(box.conf[0].cpu().numpy())
            bbox = box.xyxy[0].cpu().numpy().astype(int)
            class_name = result.names[cls]
            
            print(f"\n   Detection {j+1}:")
            print(f"   - Class ID: {cls}")
            print(f"   - Class Name: {class_name}")
            print(f"   - Confidence: {conf:.2f}")
            print(f"   - BBox: {bbox.tolist()}")
            
            if cls == 0:  # Person
                persons.append({
                    'bbox': bbox.tolist(),
                    'confidence': conf
                })
            elif cls == 1:  # Motorbike
                motorbikes.append({
                    'bbox': bbox.tolist(),
                    'confidence': conf
                })
        
        print(f"\n4️⃣ Summary:")
        print(f"   Total persons detected: {len(persons)}")
        print(f"   Total motorbikes detected: {len(motorbikes)}")
        
        if len(persons) > 0:
            print(f"\n   Persons:")
            for idx, p in enumerate(persons, 1):
                print(f"   {idx}. Confidence: {p['confidence']:.2f}, BBox: {p['bbox']}")
        
        if len(motorbikes) > 0:
            print(f"\n   Motorbikes:")
            for idx, m in enumerate(motorbikes, 1):
                print(f"   {idx}. Confidence: {m['confidence']:.2f}, BBox: {m['bbox']}")
        
        # Check for triple riding
        print(f"\n5️⃣ Checking for triple riding...")
        for mb_idx, motorbike in enumerate(motorbikes, 1):
            mb_bbox = motorbike['bbox']
            mb_x1, mb_y1, mb_x2, mb_y2 = mb_bbox
            
            print(f"\n   Motorbike {mb_idx}: {mb_bbox}")
            
            persons_on_bike = []
            for p_idx, person in enumerate(persons, 1):
                p_bbox = person['bbox']
                p_x1, p_y1, p_x2, p_y2 = p_bbox
                
                # Calculate intersection
                inter_x1 = max(p_x1, mb_x1)
                inter_y1 = max(p_y1, mb_y1)
                inter_x2 = min(p_x2, mb_x2)
                inter_y2 = min(p_y2, mb_y2)
                
                # Check overlap
                has_overlap = inter_x2 > inter_x1 and inter_y2 > inter_y1
                
                # Calculate centers
                p_center_x = (p_x1 + p_x2) / 2
                p_center_y = (p_y1 + p_y2) / 2
                m_center_x = (mb_x1 + mb_x2) / 2
                m_center_y = (mb_y1 + mb_y2) / 2
                
                # Distance
                distance = ((p_center_x - m_center_x)**2 + (p_center_y - m_center_y)**2)**0.5
                m_width = mb_x2 - mb_x1
                
                print(f"   Person {p_idx}: {p_bbox}")
                print(f"      Overlap: {has_overlap}")
                print(f"      Distance: {distance:.1f}px")
                print(f"      Motorbike width: {m_width}px")
                print(f"      Distance threshold (1.5x width): {m_width * 1.5:.1f}px")
                
                if has_overlap or distance < (m_width * 1.5):
                    persons_on_bike.append(person)
                    print(f"      ✅ Person is ON/NEAR motorbike")
                else:
                    print(f"      ❌ Person is NOT on motorbike")
            
            print(f"\n   Total persons on/near motorbike {mb_idx}: {len(persons_on_bike)}")
            if len(persons_on_bike) >= 3:
                print(f"   🚨 TRIPLE RIDING DETECTED! {len(persons_on_bike)} persons")
            elif len(persons_on_bike) >= 2:
                print(f"   ⚠️  Double riding detected ({len(persons_on_bike)} persons)")
            else:
                print(f"   ✅ No violation ({len(persons_on_bike)} person(s))")
    
    print("\n" + "="*70)
    print("✅ DEBUG COMPLETE")
    print("="*70)

if __name__ == "__main__":
    debug_triple_riding()

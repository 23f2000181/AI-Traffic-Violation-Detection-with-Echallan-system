# Triple Riding Integration Guide for CentralDetectionManager

## Step 1: Add these two methods to CentralDetectionManager class

Add these methods after the `detect_helmets` method (around line 370):

```python
def detect_triple_riding(self, image_path, image):
    """
    Detect triple riding violations (3 or more people on a motorcycle)
    
    Model classes: 0-person, 1-motorbike
    """
    try:
        if self.triple_riding_model is None:
            print("⚠️  Triple riding model not loaded")
            return []
        
        print("🏍️  Detecting triple riding violations...")
        
        # Run YOLO detection
        results = self.triple_riding_model(image)
        
        violations = []
        
        for result in results:
            # Get all detections
            persons = []
            motorbikes = []
            
            for box in result.boxes:
                cls = int(box.cls.item())
                confidence = float(box.conf[0].cpu().numpy())
                bbox = box.xyxy[0].cpu().numpy().astype(int)
                
                # Class 0 = person, Class 1 = motorbike
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
            
            # Check for triple riding: 3+ persons near a motorbike
            for motorbike in motorbikes:
                mb_bbox = motorbike['bbox']
                mb_x1, mb_y1, mb_x2, mb_y2 = mb_bbox
                
                # Count persons near this motorbike
                persons_on_bike = []
                
                for person in persons:
                    p_bbox = person['bbox']
                    
                    # Check if person overlaps or is near the motorbike
                    if self.is_person_on_motorbike(p_bbox, mb_bbox):
                        persons_on_bike.append(person)
                
                # Triple riding = 3 or more persons on one motorbike
                if len(persons_on_bike) >= 3:
                    violation = {
                        'type': 'triple_riding',
                        'motorbike_bbox': mb_bbox,
                        'person_count': len(persons_on_bike),
                        'persons': persons_on_bike,
                        'confidence': motorbike['confidence'],
                        'timestamp': datetime.now().isoformat()
                    }
                    violations.append(violation)
                    
                    print(f"🚨 Triple riding detected! {len(persons_on_bike)} persons on motorbike")
                    
                    # Draw on annotated image
                    cv2.rectangle(image, (mb_x1, mb_y1), (mb_x2, mb_y2), (0, 0, 255), 3)
                    cv2.putText(image, f"TRIPLE RIDING ({len(persons_on_bike)} persons)", 
                              (mb_x1, mb_y1-10), 
                              cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                    
                    # Draw person bounding boxes
                    for person in persons_on_bike:
                        px1, py1, px2, py2 = person['bbox']
                        cv2.rectangle(image, (px1, py1), (px2, py2), (255, 0, 0), 2)
        
        print(f"✅ Triple riding violations found: {len(violations)}")
        return violations
        
    except Exception as e:
        print(f"❌ Triple riding detection error: {e}")
        import traceback
        traceback.print_exc()
        return []

def is_person_on_motorbike(self, person_bbox, motorbike_bbox):
    """
    Check if a person is on/near a motorbike using IoU and proximity
    """
    p_x1, p_y1, p_x2, p_y2 = person_bbox
    m_x1, m_y1, m_x2, m_y2 = motorbike_bbox
    
    # Calculate intersection
    inter_x1 = max(p_x1, m_x1)
    inter_y1 = max(p_y1, m_y1)
    inter_x2 = min(p_x2, m_x2)
    inter_y2 = min(p_y2, m_y2)
    
    if inter_x2 < inter_x1 or inter_y2 < inter_y1:
        # No overlap - check proximity
        p_center_x = (p_x1 + p_x2) / 2
        p_center_y = (p_y1 + p_y2) / 2
        m_center_x = (m_x1 + m_x2) / 2
        m_center_y = (m_y1 + m_y2) / 2
        
        # Check if person is within reasonable distance
        distance = ((p_center_x - m_center_x)**2 + (p_center_y - m_center_y)**2)**0.5
        m_width = m_x2 - m_x1
        
        # Person should be within 1.5x motorbike width
        return distance < (m_width * 1.5)
    
    # Calculate IoU
    inter_area = (inter_x2 - inter_x1) * (inter_y2 - inter_y1)
    p_area = (p_x2 - p_x1) * (p_y2 - p_y1)
    m_area = (m_x2 - m_x1) * (m_y2 - m_y1)
    union_area = p_area + m_area - inter_area
    
    iou = inter_area / union_area if union_area > 0 else 0
    
    # Consider person on bike if IoU > 0.1 or significant overlap
    return iou > 0.1
```

## Summary of Changes Already Made:

✅ config.json - Added triple_riding model path
✅ Model initialization - Added in initialize_models()
✅ Detection results - Added triple_riding_violations to storage
✅ process_image - Added 'triple_riding' to default detection types
✅ process_image - Added triple riding detection call

## What's Left:

Just add the two methods above to central_detection_manager.py and restart the backend!

The triple riding detection will:
1. Detect persons and motorbikes using your trained model
2. Associate persons with nearby motorbikes
3. Flag violations when 3+ persons are on one motorbike
4. Draw bounding boxes on the annotated image
5. Work with license plate detection on the same image

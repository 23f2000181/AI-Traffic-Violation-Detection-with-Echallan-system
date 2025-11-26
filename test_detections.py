"""
Comprehensive test for both helmet and triple riding detection
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from central_detection_manager import CentralDetectionManager
import cv2

def test_all_detections():
    """Test all detection types"""
    print("="*70)
    print("🚀 COMPREHENSIVE DETECTION TEST")
    print("="*70)
    
    # Initialize manager
    print("\n1️⃣ Initializing Central Detection Manager...")
    try:
        manager = CentralDetectionManager()
        print("✅ Manager initialized successfully")
    except Exception as e:
        print(f"❌ Failed to initialize manager: {e}")
        import traceback
        traceback.print_exc()
        return
    
    # Check models
    print("\n2️⃣ Checking Models...")
    print(f"   Helmet model: {'✅ Loaded' if manager.helmet_model else '❌ Not loaded'}")
    print(f"   Triple riding model: {'✅ Loaded' if manager.triple_riding_model else '❌ Not loaded'}")
    
    # Test image
    test_image = "D:/Codes/Miniproj/detect2.jpg"
    
    if not os.path.exists(test_image):
        print(f"\n❌ Test image not found: {test_image}")
        print("Please provide a test image path")
        return
    
    print(f"\n3️⃣ Testing with image: {test_image}")
    
    # Test each detection type separately
    print("\n" + "="*70)
    print("🛵 TESTING HELMET DETECTION")
    print("="*70)
    try:
        helmet_results = manager.process_image(
            test_image,
            detection_types=['helmet']
        )
        
        if helmet_results:
            helmets = helmet_results.get('helmet_violations', [])
            print(f"✅ Helmet detection completed")
            print(f"   Found: {len(helmets)} helmet-related detections")
            
            for i, h in enumerate(helmets[:3], 1):  # Show first 3
                print(f"\n   Detection {i}:")
                print(f"   - Type: {h.get('type', h.get('class', 'N/A'))}")
                print(f"   - Confidence: {h.get('confidence', 0):.2f}")
                print(f"   - BBox: {h.get('bbox', 'N/A')}")
        else:
            print("❌ Helmet detection returned None")
    except Exception as e:
        print(f"❌ Helmet detection error: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "="*70)
    print("🏍️  TESTING TRIPLE RIDING DETECTION")
    print("="*70)
    try:
        triple_results = manager.process_image(
            test_image,
            detection_types=['triple_riding']
        )
        
        if triple_results:
            violations = triple_results.get('triple_riding_violations', [])
            print(f"✅ Triple riding detection completed")
            print(f"   Found: {len(violations)} triple riding violations")
            
            for i, v in enumerate(violations, 1):
                print(f"\n   Violation {i}:")
                print(f"   - Person count: {v.get('person_count', 'N/A')}")
                print(f"   - Confidence: {v.get('confidence', 0):.2f}")
                print(f"   - Motorbike BBox: {v.get('motorbike_bbox', 'N/A')}")
        else:
            print("❌ Triple riding detection returned None")
    except Exception as e:
        print(f"❌ Triple riding detection error: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "="*70)
    print("🎯 TESTING ALL DETECTIONS TOGETHER")
    print("="*70)
    try:
        all_results = manager.process_image(
            test_image,
            detection_types=['license_plate', 'helmet', 'triple_riding', 'red_light']
        )
        
        if all_results:
            summary = all_results.get('summary', {})
            print("✅ All detections completed")
            print(f"\n📊 SUMMARY:")
            print(f"   License Plates: {summary.get('total_license_plates', 0)}")
            print(f"   Helmet Violations: {summary.get('total_helmet_violations', 0)}")
            print(f"   Triple Riding: {summary.get('total_triple_riding_violations', 0)}")
            print(f"   Red Light: {summary.get('total_red_light_violations', 0)}")
            
            # Show annotated image path
            output_dir = manager.config['output_dirs']['combined']
            print(f"\n📁 Check annotated images in: {output_dir}")
        else:
            print("❌ All detections returned None")
    except Exception as e:
        print(f"❌ All detections error: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "="*70)
    print("✅ TESTING COMPLETE")
    print("="*70)

if __name__ == "__main__":
    test_all_detections()

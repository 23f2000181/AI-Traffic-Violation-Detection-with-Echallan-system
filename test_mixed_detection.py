#!/usr/bin/env python3
"""
Test script to demonstrate helmet and no-helmet detection simultaneously
"""

from detect_helmet_fixed import detect_helmets

def test_mixed_detection():
    """Test detection on an image with both helmet and no-helmet cases"""

    print("🧪 Testing Mixed Helmet Detection")
    print("=" * 50)

    # This will test with an image that should have both classes
    # Replace 'mixed_helmet.jpg' with your actual image filename
    image_path = "mixed_helmet.jpg"  # Change this to your image with both types

    print(f"🖼️  Testing with: {new.jpeg}")
    print("Expected: Both 'Helmet' and 'NoHelmet' detections")
    print("-" * 50)

    # Use lower confidence to catch more detections
    detect_helmets(image_path=image_path, confidence=0.3)

    print("\n" + "=" * 50)
    print("📊 If you see both classes (Helmet and NoHelmet), the system works!")
    print("📊 If you only see one class, the image only contains that type.")

def simple_test():
    """Simple test function you can call directly"""

    # Test with your existing images
    print("Testing existing images...")

    # Test bus.jpg (might have helmets)
    detect_helmets(image_path="bus.jpg", confidence=0.3)

    # Test OIP.jpeg
    detect_helmets(image_path="OIP.jpeg", confidence=0.3)

if __name__ == "__main__":
    print("Choose a test:")
    print("1. Test mixed detection (needs image with both classes)")
    print("2. Test existing images")

    choice = input("Enter 1 or 2: ").strip()

    if choice == "1":
        test_mixed_detection()
    elif choice == "2":
        simple_test()
    else:
        print("Running default test...")
        simple_test()

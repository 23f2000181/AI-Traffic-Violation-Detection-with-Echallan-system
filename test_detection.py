#!/usr/bin/env python3
"""
Test script for helmet detection with custom confidence threshold
"""

from detect_helmet import detect_helmets

def test_helmet_detection():
    """Test helmet detection on sample images with different confidence levels"""

    print("🧪 Testing Helmet Detection System")
    print("=" * 50)

    # Test with default confidence (0.5)
    print("\n📊 Test 1: Default confidence (0.5)")
    print("-" * 30)
    detect_helmets(image_path="new.jpeg", confidence=0.5)

    # Test with lower confidence (0.3) to catch more detections
    print("\n📊 Test 2: Lower confidence (0.3)")
    print("-" * 30)
    detect_helmets(image_path="new.jpeg", confidence=0.3)

    # Test with another image if available
    print("\n📊 Test 3: Testing new1.jpeg")
    print("-" * 30)
    detect_helmets(image_path="new1.jpeg", confidence=0.3)

if __name__ == "__main__":
    test_helmet_detection()

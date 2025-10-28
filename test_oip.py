from detect_helmet_fixed import detect_helmets

# Test helmet detection on oip2.jpg with lower confidence to detect plates
detect_helmets(image_path="oip2.jpg", confidence=0.1)

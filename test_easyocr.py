import easyocr

# Initialize the reader
reader = easyocr.Reader(['en'])

# Test on an image
image_path = 'oip2.jpg'
results = reader.readtext(image_path)

print("OCR Results:")
for result in results:
    print(f"Text: {result[1]}, Confidence: {result[2]:.2f}")

if not results:
    print("No text detected in the image.")

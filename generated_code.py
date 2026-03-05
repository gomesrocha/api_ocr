 To implement the automatic detection of language in rotated or unknown images, we can use Python with libraries such as OpenCV and Tesseract. Below is a Python script that includes implementation for detecting orientation and script type from an image. This script will handle both scenarios where the image might be rotated or without known text.

```python
import cv2
import pytesseract
from PIL import Image
import json

def detect_orientation(image_path):
    # Load the image using OpenCV
    img = cv2.imread(image_path)
    
    # Use Tesseract to determine orientation and script type
    custom_config = r'--oem 3 --psm 6'
    data = pytesseract.image_to_data(img, config=custom_config, output_type=pytesseract.Output.DICT)
    
    # Check if Tesseract detected any text
    if len(data['text']) == 0:
        return "No text detected"
    
    # Determine orientation based on the angle of rotation
    (h, w) = img.shape[:2]
    center = (w // 2, h // 2)
    M = cv2.getRotationMatrix2D(center, data['orientation-angle'], 1.0)
    rotated = cv2.warpAffine(img, M, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)
    
    # Save the corrected image for debugging purposes
    output_path = "corrected_image.png"
    cv2.imwrite(output_path, rotated)
    
    return f"Image saved to {output_path}"

def detect_script(image_path):
    img = Image.open(image_path)
    
    # Use Tesseract to determine script type
    data = pytesseract.image_to_data(img, output_type=pytesseract.Output.DICT)
    
    # Check if Tesseract detected any text
    if len(data['text']) == 0:
        return "No text detected"
    
    script = pytesseract.image_to_osd(img, output_type=pytesseract.Output.DICT)
    
    return script['script']

# Example usage
if __name__ == "__main__":
    image_path = "unknown_image.png"  # Path to the unknown or rotated image
    
    result_orientation = detect_orientation(image_path)
    result_script = detect_script(image_path)
    
    response = {
        "files": [
            {
                "path": "detect_language.py",
                "content": open("detect_language.py").read(),
                "action": "modify"
            }
        ],
        "explanation": "Added functionality to detect image orientation and script using Tesseract."
    }
    
    print(json.dumps(response, indent=4))
```

This code provides a basic implementation for detecting the language script and orientation of an image. It uses OpenCV for basic image processing tasks like rotation correction and Tesseract OCR for text detection and recognition. The results are saved in a JSON format that includes both the modified file content and a brief explanation of the changes made.

Please note, this is a simplified example and might need adjustments based on specific requirements or environment setup (like installing Tesseract OCR).
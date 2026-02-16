import asyncio
import pytesseract
from PIL import Image, ImageOps

async def read_image(img_path, lang='eng+por', mode='fast', auto=False):
    """
    Reads text from an image using Tesseract.

    Args:
        img_path (str): Path to the image file.
        lang (str): Language code (default: 'eng+por').
        mode (str): 'fast' (default) or 'accurate'.
        auto (bool): If True, enables OSD (Orientation and Script Detection) via Tesseract config.
    """
    try:
        # Configuration for Tesseract
        custom_config = ""
        if auto:
            # PSM 1: Automatic page segmentation with OSD.
            custom_config += " --psm 1"
        else:
            # PSM 3: Fully automatic page segmentation, but no OSD. (Default)
            custom_config += " --psm 3"

        # Load image
        image = Image.open(img_path)

        if mode == 'accurate':
            # Preprocessing for accuracy:
            # 1. Convert to grayscale
            image = image.convert('L')
            # 2. Resize (Scale 2x) for better character recognition
            width, height = image.size
            image = image.resize((width * 2, height * 2), Image.Resampling.LANCZOS)
            # 3. Enhance contrast (optional, but histogram equalization often helps)
            image = ImageOps.autocontrast(image)

        # Run OCR in a separate thread
        def run_ocr():
            return pytesseract.image_to_string(image, lang=lang, config=custom_config)

        text = await asyncio.to_thread(run_ocr)
        return text
    except Exception as e:
        return f"[ERROR] Unable to process file: {img_path}. Error: {str(e)}"

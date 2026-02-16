import asyncio
import pytesseract

async def read_image(img_path, lang='eng'):
    try:
        # Run blocking tesseract call in a separate thread
        text = await asyncio.to_thread(pytesseract.image_to_string, img_path, lang=lang)
        return text
    except Exception as e:
        return f"[ERROR] Unable to process file: {img_path}. Error: {str(e)}"

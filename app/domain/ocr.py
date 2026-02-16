import asyncio
import pytesseract
import logging

log = logging.getLogger("uvicorn")

async def read_image(img_path: str, lang: str = 'eng') -> str:
    try:
        # Run pytesseract in a separate thread to avoid blocking the event loop
        text = await asyncio.to_thread(pytesseract.image_to_string, img_path, lang=lang)
        return text
    except Exception as e:
        log.error(f"Error processing file {img_path}: {e}")
        return f"[ERROR] Unable to process file: {img_path}"

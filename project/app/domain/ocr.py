import asyncio
import pytesseract
async def read_image(img_path, lang='eng'):
    try:
        text = pytesseract.image_to_string(img_path, lang=lang)
        await asyncio.sleep(2)
        return text
    except ValueError:
        return "[ERROR] Unable to process file: {0}".format(img_path)
import asyncio
import tempfile
import os
from pdf2image import convert_from_path, pdfinfo_from_path
from app.domain import ocr
from fastapi import HTTPException

async def process_pdf(
    file_path: str,
    lang: str = 'eng+por',
    mode: str = 'fast',
    auto: bool = False,
    force_processing: bool = False
) -> str:
    """
    Converts PDF to images and extracts text from each page.

    Args:
        file_path (str): Path to the PDF file.
        lang (str): Language code.
        mode (str): 'fast' or 'accurate'.
        auto (bool): Enable OSD.
        force_processing (bool): If True, ignores the 10-page limit.

    Returns:
        str: Concatenated text from all processed pages.
    """
    try:
        # Check page count
        # pdfinfo_from_path runs 'pdfinfo' command which is part of poppler-utils
        info = await asyncio.to_thread(pdfinfo_from_path, file_path)
        page_count = info.get("Pages", 0)

        if page_count > 10 and not force_processing:
            raise HTTPException(
                status_code=400,
                detail=f"PDF has {page_count} pages. Limit is 10. Set 'force_processing' to True to override."
            )

        # Determine DPI based on mode
        dpi = 300 if mode == 'accurate' else 200

        # Convert PDF to images
        # We run this in a thread because it's CPU bound
        def convert():
            return convert_from_path(file_path, dpi=dpi)

        images = await asyncio.to_thread(convert)

        extracted_text = []

        for i, image in enumerate(images):
            # Save image to temp file to reuse existing OCR logic
            # Use delete=False so we can close it before OCR reads it (Windows compat, though running on Linux)
            with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as temp_img:
                image.save(temp_img.name)
                temp_img_path = temp_img.name

            try:
                # Reuse the existing OCR logic which handles preprocessing based on mode
                page_text = await ocr.read_image(temp_img_path, lang=lang, mode=mode, auto=auto)
                extracted_text.append(f"--- Page {i+1} ---\n{page_text}")
            finally:
                if os.path.exists(temp_img_path):
                    os.remove(temp_img_path)

        return "\n\n".join(extracted_text)

    except HTTPException as he:
        raise he
    except Exception as e:
        # Log the error here if logging was set up
        raise HTTPException(status_code=500, detail=f"Error processing PDF: {str(e)}")

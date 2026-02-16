from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from typing import List, Optional
import time
import os

from app.domain import ocr, fileUpload
from app.model.TextSchema import TextExtractDocument

router = APIRouter()

@router.post("/extract_text", response_model=List[TextExtractDocument])
async def extract_text(
    input_images: List[UploadFile] = File(...),
    lang: str = Form("eng+por", description="Language code (eng, por, eng+por). Use 'auto' to enable OSD."),
    mode: str = Form("fast", description="OCR mode: 'fast' or 'accurate'."),
    auto_detect: bool = Form(False, description="Enable Orientation and Script Detection (OSD).")
):
    """
    Extract text from uploaded images using Tesseract OCR.

    - **input_images**: List of image files to process.
    - **lang**: Language(s) to use for OCR. Defaults to 'eng+por'. set to 'auto' to force OSD.
    - **mode**: processing mode. 'fast' is quicker, 'accurate' performs preprocessing (rescaling, etc.).
    - **auto_detect**: Explicitly enable OSD (Orientation and Script Detection).
    """

    # Validate mode
    if mode not in ["fast", "accurate"]:
        raise HTTPException(status_code=400, detail="Invalid mode. Use 'fast' or 'accurate'.")

    # Handle 'auto' lang as auto_detect=True
    if lang == "auto":
        auto_detect = True
        lang = "eng+por" # Default to mixed if user said auto but didn't specify lang. OSD handles orientation.

    results = []

    for img in input_images:
        start_time = time.time()
        print(f"Processing image: {img.filename}")

        # Validate file type
        fileUpload.validate_image_file(img)

        # Save file using tempfile
        temp_file = fileUpload._save_file_to_server(img)

        try:
            # Process OCR
            text = await ocr.read_image(
                img_path=temp_file,
                lang=lang,
                mode=mode,
                auto=auto_detect
            )
        finally:
            if os.path.exists(temp_file):
                os.remove(temp_file)

        time_taken = str(round((time.time() - start_time), 2))

        results.append(TextExtractDocument(
            file_name=img.filename or "unknown",
            text=text,
            time_taken=time_taken
        ))

    return results

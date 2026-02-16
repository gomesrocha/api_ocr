from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from typing import List, Optional
import time
import os

from app.domain import pdf_ocr, fileUpload
from app.model.TextSchema import TextExtractDocument

router = APIRouter()

@router.post("/extract_pdf", response_model=List[TextExtractDocument])
async def extract_pdf(
    input_file: UploadFile = File(..., description="PDF file to process"),
    lang: str = Form("eng+por", description="Language code (eng, por, eng+por). Use 'auto' to enable OSD."),
    mode: str = Form("fast", description="OCR mode: 'fast' or 'accurate'."),
    auto_detect: bool = Form(False, description="Enable Orientation and Script Detection (OSD)."),
    force_processing: bool = Form(False, description="Force processing even if page count > 10.")
):
    """
    Extract text from uploaded PDF document.

    - **input_file**: PDF file to process.
    - **lang**: Language(s) to use for OCR. Defaults to 'eng+por'.
    - **mode**: processing mode. 'fast' is quicker, 'accurate' performs preprocessing.
    - **auto_detect**: Explicitly enable OSD (Orientation and Script Detection).
    - **force_processing**: Set to True to bypass the 10-page limit safeguard.
    """

    # Validate mode
    if mode not in ["fast", "accurate"]:
        raise HTTPException(status_code=400, detail="Invalid mode. Use 'fast' or 'accurate'.")

    # Handle 'auto' lang
    if lang == "auto":
        auto_detect = True
        lang = "eng+por"

    start_time = time.time()
    print(f"Processing PDF: {input_file.filename}")

    # Validate file type
    fileUpload.validate_pdf_file(input_file)

    # Save file using tempfile
    temp_file = fileUpload._save_file_to_server(input_file)

    try:
        # Process PDF
        text = await pdf_ocr.process_pdf(
            file_path=temp_file,
            lang=lang,
            mode=mode,
            auto=auto_detect,
            force_processing=force_processing
        )
    finally:
        if os.path.exists(temp_file):
            os.remove(temp_file)

    time_taken = str(round((time.time() - start_time), 2))

    # Return list with single document result (consistent with image endpoint structure)
    return [TextExtractDocument(
        file_name=input_file.filename or "unknown",
        text=text,
        time_taken=time_taken
    )]

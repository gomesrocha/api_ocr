from fastapi import APIRouter, UploadFile, File
from typing import List
import time
import os

from app.domain import ocr, fileUpload
from app.model.TextSchema import TextExtractDocument

router = APIRouter()

@router.post("/extract_text", response_model=List[TextExtractDocument])
async def extract_text(input_images: List[UploadFile] = File(...)):
    results = []

    for img in input_images:
        start_time = time.time()
        print(f"Processing image: {img.filename}")

        # Save file using tempfile (refactored fileUpload)
        temp_file = fileUpload._save_file_to_server(img)

        try:
            text = await ocr.read_image(temp_file)
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

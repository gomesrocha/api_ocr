from fastapi import APIRouter, File, UploadFile
from typing import List
import time
import os

from app.domain.ocr import read_image
from app.domain.fileUpload import _save_file_to_server
from app.model.TextSchema import TextExtractDocument, TextExtractResponse

router = APIRouter()

@router.post("/extract_text", response_model=TextExtractResponse)
async def extract_text(input_images: List[UploadFile] = File(...)):
    results = []
    start_time = time.time()

    for img in input_images:
        # Save file to temp location
        temp_file_path = _save_file_to_server(img)
        try:
            # Process OCR
            text = await read_image(temp_file_path)
            results.append(TextExtractDocument(
                file_name=img.filename,
                text=text
            ))
        finally:
            # Cleanup temp file
            if os.path.exists(temp_file_path):
                os.remove(temp_file_path)

    total_time = round((time.time() - start_time), 2)
    return TextExtractResponse(
        documents=results,
        total_time_taken=str(total_time)
    )

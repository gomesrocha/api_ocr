from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from typing import List, Optional
import time
import os

from app.domain import ocr, fileUpload
from app.model.TextSchema import TextExtractDocument
from app.services import storage

router = APIRouter()

@router.post("/extract_text", response_model=List[TextExtractDocument])
async def extract_text(
    input_images: Optional[List[UploadFile]] = File(None, description="List of image files to process (required if source='upload')"),
    source: str = Form("upload", description="Source of the file: 'upload' or 'object_storage'"),
    client_id: Optional[str] = Form(None, description="Client ID for object storage (required if source='object_storage')"),
    object_keys: Optional[List[str]] = Form(None, description="List of object keys (paths) in the bucket (required if source='object_storage')"),
    lang: str = Form("eng+por", description="Language code (eng, por, eng+por). Use 'auto' to enable OSD."),
    mode: str = Form("fast", description="OCR mode: 'fast' or 'accurate'."),
    auto_detect: bool = Form(False, description="Enable Orientation and Script Detection (OSD).")
):
    """
    Extract text from uploaded images or from object storage using Tesseract OCR.

    - **input_images**: List of image files to process (required if source='upload').
    - **source**: Source of the file: 'upload' or 'object_storage'. Defaults to 'upload'.
    - **client_id**: Client ID for object storage (required if source='object_storage').
    - **object_keys**: List of object keys (paths) in the bucket (required if source='object_storage').
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

    if source == "upload":
        if not input_images:
             raise HTTPException(status_code=400, detail="input_images is required when source is 'upload'.")

        if client_id or object_keys:
             raise HTTPException(status_code=400, detail="Ambiguous request: cannot provide both upload files and object storage parameters.")

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

    elif source == "object_storage":
        if input_images:
             raise HTTPException(status_code=400, detail="Ambiguous request: cannot provide both upload files and object storage parameters.")

        if not client_id or not object_keys:
             raise HTTPException(status_code=400, detail="client_id and object_keys are required when source is 'object_storage'.")

        for key in object_keys:
            start_time = time.time()
            print(f"Processing image from storage: {client_id}/{key}")

            temp_file = None
            try:
                try:
                    temp_file = storage.download_file_from_storage(client_id, key)
                except ValueError as e:
                    raise HTTPException(status_code=400, detail=str(e))
                except Exception as e:
                     print(f"Error downloading file {key}: {e}")
                     raise HTTPException(status_code=500, detail=f"Error retrieving file {key} from storage.")

                # Process OCR
                text = await ocr.read_image(
                    img_path=temp_file,
                    lang=lang,
                    mode=mode,
                    auto=auto_detect
                )

                time_taken = str(round((time.time() - start_time), 2))
                results.append(TextExtractDocument(
                    file_name=key,
                    text=text,
                    time_taken=time_taken
                ))
            finally:
                if temp_file and os.path.exists(temp_file):
                    os.remove(temp_file)
    else:
        raise HTTPException(status_code=400, detail="Invalid source. Use 'upload' or 'object_storage'.")

    return results

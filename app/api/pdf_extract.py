from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from typing import List, Optional
import time
import os

from app.domain import pdf_ocr, fileUpload
from app.model.TextSchema import TextExtractDocument
from app.services import storage

router = APIRouter()

@router.post("/extract_pdf", response_model=List[TextExtractDocument])
async def extract_pdf(
    input_file: Optional[UploadFile] = File(None, description="PDF file to process (required if source='upload')"),
    source: str = Form("upload", description="Source of the file: 'upload' or 'object_storage'"),
    client_id: Optional[str] = Form(None, description="Client ID for object storage (required if source='object_storage')"),
    object_key: Optional[str] = Form(None, description="Object key (path) in the bucket (required if source='object_storage')"),
    lang: str = Form("eng+por", description="Language code (eng, por, eng+por). Use 'auto' to enable OSD."),
    mode: str = Form("fast", description="OCR mode: 'fast' or 'accurate'."),
    auto_detect: bool = Form(False, description="Enable Orientation and Script Detection (OSD)."),
    force_processing: bool = Form(False, description="Force processing even if page count > 10.")
):
    """
    Extract text from uploaded PDF document or from object storage.

    - **input_file**: PDF file to process (required if source='upload').
    - **source**: Source of the file: 'upload' or 'object_storage'. Defaults to 'upload'.
    - **client_id**: Client ID for object storage (required if source='object_storage').
    - **object_key**: Object key (path) in the bucket (required if source='object_storage').
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
    filename = "unknown"
    temp_file = None

    try:
        if source == "upload":
            if not input_file:
                raise HTTPException(status_code=400, detail="input_file is required when source is 'upload'.")

            # Reject if object storage params are present to avoid ambiguity
            if client_id or object_key:
                 raise HTTPException(status_code=400, detail="Ambiguous request: cannot provide both upload file and object storage parameters.")

            filename = input_file.filename
            print(f"Processing PDF upload: {filename}")

            # Validate file type
            fileUpload.validate_pdf_file(input_file)

            # Save file using tempfile
            temp_file = fileUpload._save_file_to_server(input_file)

        elif source == "object_storage":
            if input_file:
                 raise HTTPException(status_code=400, detail="Ambiguous request: cannot provide both upload file and object storage parameters.")

            if not client_id or not object_key:
                raise HTTPException(status_code=400, detail="client_id and object_key are required when source is 'object_storage'.")

            filename = object_key
            print(f"Processing PDF from storage: {client_id}/{object_key}")

            # Download file
            try:
                temp_file = storage.download_file_from_storage(client_id, object_key)
            except ValueError as e:
                raise HTTPException(status_code=400, detail=str(e))
            except Exception as e:
                # Log error
                print(f"Error downloading file: {e}")
                raise HTTPException(status_code=500, detail="Error retrieving file from storage.")

            # Validate PDF header (simple check)
            try:
                with open(temp_file, "rb") as f:
                    header = f.read(5)
                if header != b"%PDF-":
                    raise HTTPException(status_code=400, detail="Downloaded file is not a valid PDF.")
            except HTTPException:
                raise
            except Exception as e:
                 raise HTTPException(status_code=400, detail=f"Error validating file: {e}")

        else:
             raise HTTPException(status_code=400, detail="Invalid source. Use 'upload' or 'object_storage'.")

        # Process PDF
        text = await pdf_ocr.process_pdf(
            file_path=temp_file,
            lang=lang,
            mode=mode,
            auto=auto_detect,
            force_processing=force_processing
        )

    except HTTPException as e:
        raise e
    except Exception as e:
        # Log unexpected errors
        print(f"Error processing PDF: {e}")
        raise HTTPException(status_code=500, detail=f"Error processing PDF: {str(e)}")
    finally:
        if temp_file and os.path.exists(temp_file):
            os.remove(temp_file)

    time_taken = str(round((time.time() - start_time), 2))

    return [TextExtractDocument(
        file_name=filename or "unknown",
        text=text,
        time_taken=time_taken
    )]

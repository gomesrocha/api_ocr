from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from typing import List, Optional
import time
import os

from app.domain import ocr, pdf_ocr, fileUpload, structured_extraction
from app.model.StructuredSchema import StructuredExtractionResult
from app.services import storage

router = APIRouter()

@router.post("/extract_structured", response_model=List[StructuredExtractionResult])
async def extract_structured(
    input_files: Optional[List[UploadFile]] = File(None, description="List of files (Images or PDFs) to process (required if source='upload')"),
    source: str = Form("upload", description="Source of the file: 'upload' or 'object_storage'"),
    client_id: Optional[str] = Form(None, description="Client ID for object storage (required if source='object_storage')"),
    object_keys: Optional[List[str]] = Form(None, description="List of object keys in the bucket (required if source='object_storage')"),
    lang: str = Form("eng+por", description="Language code (eng, por, eng+por)."),
    mode: str = Form("fast", description="OCR mode: 'fast' or 'accurate'."),
    auto_detect: bool = Form(False, description="Enable Orientation and Script Detection (OSD)."),
    model_provider: str = Form("local_tesseract", description="Provider for structured extraction (e.g., 'local_tesseract', 'openai', 'ollama', 'azure')"),
    model_name: str = Form("", description="Model name to use (e.g., 'gpt-4o-mini', 'llama3'). Required if provider is not 'local_tesseract'"),
    force_processing: bool = Form(False, description="Force PDF processing even if page count > 10.")
):
    """
    Extract structured data from uploaded images or PDFs.
    First performs OCR, then optionally passes the raw text to an LLM for structured JSON output.
    """

    if mode not in ["fast", "accurate"]:
        raise HTTPException(status_code=400, detail="Invalid mode. Use 'fast' or 'accurate'.")

    if lang == "auto":
        auto_detect = True
        lang = "eng+por"

    if model_provider != "local_tesseract" and not model_name:
        raise HTTPException(status_code=400, detail="model_name is required when model_provider is not 'local_tesseract'.")

    results = []

    if source == "upload":
        if not input_files:
             raise HTTPException(status_code=400, detail="input_files is required when source is 'upload'.")

        if client_id or object_keys:
             raise HTTPException(status_code=400, detail="Ambiguous request: cannot provide both upload files and object storage parameters.")

        for file in input_files:
            start_time = time.time()
            filename = file.filename

            # Determine file type
            is_pdf = filename.lower().endswith(".pdf")

            # Save file
            temp_file = fileUpload._save_file_to_server(file)

            try:
                # Perform OCR
                if is_pdf:
                    # Basic PDF header check
                    try:
                        with open(temp_file, "rb") as f:
                            header = f.read(5)
                        if header != b"%PDF-":
                            raise HTTPException(status_code=400, detail="Downloaded file is not a valid PDF.")
                    except HTTPException:
                        raise
                    except Exception as e:
                         raise HTTPException(status_code=400, detail=f"Error validating file: {e}")

                    raw_text = await pdf_ocr.process_pdf(
                        file_path=temp_file,
                        lang=lang,
                        mode=mode,
                        auto=auto_detect,
                        force_processing=force_processing
                    )
                else:
                    fileUpload.validate_image_file(file)
                    raw_text = await ocr.read_image(
                        img_path=temp_file,
                        lang=lang,
                        mode=mode,
                        auto=auto_detect
                    )

                # Extract Structured Data
                structured_data = structured_extraction.extract_structured_data(
                    text=raw_text,
                    provider=model_provider,
                    model_name=model_name,
                    lang_hint=lang
                )

            finally:
                if os.path.exists(temp_file):
                    os.remove(temp_file)

            time_taken = str(round((time.time() - start_time), 2))

            results.append(StructuredExtractionResult(
                file_name=filename or "unknown",
                provider_used=model_provider,
                model_used=model_name if model_provider != "local_tesseract" else None,
                data=structured_data,
                time_taken=time_taken
            ))

    elif source == "object_storage":
        if input_files:
             raise HTTPException(status_code=400, detail="Ambiguous request: cannot provide both upload files and object storage parameters.")

        if not client_id or not object_keys:
             raise HTTPException(status_code=400, detail="client_id and object_keys are required when source is 'object_storage'.")

        for key in object_keys:
            start_time = time.time()

            is_pdf = key.lower().endswith(".pdf")
            temp_file = None

            try:
                try:
                    temp_file = storage.download_file_from_storage(client_id, key)
                except ValueError as e:
                    raise HTTPException(status_code=400, detail=str(e))
                except Exception as e:
                     raise HTTPException(status_code=500, detail=f"Error retrieving file {key} from storage.")

                if is_pdf:
                    try:
                        with open(temp_file, "rb") as f:
                            header = f.read(5)
                        if header != b"%PDF-":
                            raise HTTPException(status_code=400, detail="Downloaded file is not a valid PDF.")
                    except HTTPException:
                        raise
                    except Exception as e:
                         raise HTTPException(status_code=400, detail=f"Error validating file: {e}")

                    raw_text = await pdf_ocr.process_pdf(
                        file_path=temp_file,
                        lang=lang,
                        mode=mode,
                        auto=auto_detect,
                        force_processing=force_processing
                    )
                else:
                    raw_text = await ocr.read_image(
                        img_path=temp_file,
                        lang=lang,
                        mode=mode,
                        auto=auto_detect
                    )

                # Extract Structured Data
                structured_data = structured_extraction.extract_structured_data(
                    text=raw_text,
                    provider=model_provider,
                    model_name=model_name,
                    lang_hint=lang
                )

                time_taken = str(round((time.time() - start_time), 2))
                results.append(StructuredExtractionResult(
                    file_name=key,
                    provider_used=model_provider,
                    model_used=model_name if model_provider != "local_tesseract" else None,
                    data=structured_data,
                    time_taken=time_taken
                ))
            finally:
                if temp_file and os.path.exists(temp_file):
                    os.remove(temp_file)
    else:
        raise HTTPException(status_code=400, detail="Invalid source. Use 'upload' or 'object_storage'.")

    return results

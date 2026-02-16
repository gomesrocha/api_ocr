import shutil
import tempfile
import os
import filetype
from fastapi import UploadFile, HTTPException

def _save_file_to_server(uploaded_file):
    suffix = os.path.splitext(uploaded_file.filename)[1]
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as buffer:
        shutil.copyfileobj(uploaded_file.file, buffer)
        return buffer.name

def validate_image_file(file: UploadFile):
    """
    Validates if the uploaded file is a valid image using magic bytes.
    Raises HTTPException(400) if invalid.
    """
    try:
        # Read the first 2048 bytes to detect file type
        header = file.file.read(2048)
        file.file.seek(0)  # Reset file pointer

        if not header:
            raise HTTPException(status_code=400, detail="Empty file uploaded.")

        kind = filetype.guess(header)

        if kind is None:
            raise HTTPException(status_code=400, detail="Could not determine file type. Please upload a valid image.")

        if not kind.mime.startswith("image/"):
            raise HTTPException(status_code=400, detail=f"Invalid file type: {kind.mime}. Only images are allowed.")

        return True
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=400, detail=f"Error validating file: {str(e)}")

def validate_pdf_file(file: UploadFile):
    """
    Validates if the uploaded file is a valid PDF using magic bytes.
    Raises HTTPException(400) if invalid.
    """
    try:
        # Read the first 2048 bytes to detect file type
        header = file.file.read(2048)
        file.file.seek(0)  # Reset file pointer

        if not header:
            raise HTTPException(status_code=400, detail="Empty file uploaded.")

        kind = filetype.guess(header)

        # PDF magic bytes might not always be detected by filetype if it's not strictly following standard or is a fragment,
        # but filetype lib is generally good.
        # However, specifically check for PDF mime type.

        if kind is None:
             # Fallback check for %PDF-
            if header.startswith(b"%PDF-"):
                return True
            raise HTTPException(status_code=400, detail="Could not determine file type. Please upload a valid PDF.")

        if kind.mime != "application/pdf":
             # Fallback check for %PDF-
            if header.startswith(b"%PDF-"):
                return True
            raise HTTPException(status_code=400, detail=f"Invalid file type: {kind.mime}. Only PDF files are allowed.")

        return True
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=400, detail=f"Error validating file: {str(e)}")

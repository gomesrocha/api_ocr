import shutil
import tempfile
from fastapi import UploadFile

def _save_file_to_server(uploaded_file: UploadFile) -> str:
    """
    Saves the uploaded file to a temporary file.
    Returns the path to the temporary file.
    The caller is responsible for deleting the file when done.
    """
    # Create a named temporary file
    # delete=False because we need to close it and then let another process (tesseract) read it
    with tempfile.NamedTemporaryFile(delete=False, suffix=f"_{uploaded_file.filename}") as temp_file:
        shutil.copyfileobj(uploaded_file.file, temp_file)
        return temp_file.name

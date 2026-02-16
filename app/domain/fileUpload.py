import shutil
import tempfile
import os

def _save_file_to_server(uploaded_file):
    suffix = os.path.splitext(uploaded_file.filename)[1]
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as buffer:
        shutil.copyfileobj(uploaded_file.file, buffer)
        return buffer.name

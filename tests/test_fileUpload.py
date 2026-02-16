import os
import shutil
import tempfile
from fastapi import UploadFile
from unittest.mock import MagicMock
from app.domain.fileUpload import _save_file_to_server

# Mock UploadFile
class MockUploadFile:
    def __init__(self, filename, content=b"test content"):
        self.filename = filename
        self.file = MagicMock()
        # Mocking read method is not enough because copyfileobj uses read() on the file object.
        # So we use a BytesIO object.
        import io
        self.file = io.BytesIO(content)

def test_save_file_to_server():
    uploaded_file = MockUploadFile("test.png")

    # Act
    actual_file = _save_file_to_server(uploaded_file)

    # Assert
    assert os.path.exists(actual_file)
    # The suffix should be preserved
    assert actual_file.endswith(".png")

    # Verify content
    with open(actual_file, "rb") as f:
        content = f.read()
    assert content == b"test content"

    # Cleanup
    os.remove(actual_file)

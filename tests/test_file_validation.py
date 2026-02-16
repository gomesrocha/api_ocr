from fastapi import UploadFile
from app.domain.fileUpload import validate_image_file
from io import BytesIO
import pytest
from fastapi import HTTPException

def test_validate_valid_image():
    # Create a dummy PNG file (signature: 89 50 4E 47 0D 0A 1A 0A)
    png_header = b'\x89PNG\r\n\x1a\n'
    file = UploadFile(filename="test.png", file=BytesIO(png_header))
    assert validate_image_file(file) is True

def test_validate_invalid_file():
    # Create a text file
    file = UploadFile(filename="test.txt", file=BytesIO(b"Hello World"))
    with pytest.raises(HTTPException) as exc:
        validate_image_file(file)
    assert exc.value.status_code == 400
    assert "Could not determine file type" in exc.value.detail

def test_validate_empty_file():
    file = UploadFile(filename="empty.txt", file=BytesIO(b""))
    with pytest.raises(HTTPException) as exc:
        validate_image_file(file)
    assert exc.value.status_code == 400
    assert "Empty file uploaded" in exc.value.detail

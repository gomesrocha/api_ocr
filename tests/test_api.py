from fastapi.testclient import TestClient
from app.main import app
from unittest.mock import patch, AsyncMock
import pytest
import os

client = TestClient(app)

@pytest.fixture
def mock_ocr_read_image():
    # Use AsyncMock to mock an async function
    with patch("app.domain.ocr.read_image", new_callable=AsyncMock) as mock:
        mock.return_value = "API OCR text"
        yield mock

def test_extract_text(mock_ocr_read_image):
    # Create a dummy image file for upload (must be valid image structure for validation)
    # Using PNG header: 89 50 4E 47 0D 0A 1A 0A
    img_content = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15\xc4\x89'
    files = {"input_images": ("test.png", img_content, "image/png")}

    response = client.post("/extract_text", files=files)

    # If status code is 400, it means validation failed.
    if response.status_code == 400:
        print(response.json())

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 1
    assert data[0]["file_name"] == "test.png"
    assert data[0]["text"] == "API OCR text"

    # Verify mock was called
    mock_ocr_read_image.assert_called_once()

def test_extract_text_custom_params(mock_ocr_read_image):
    # Valid PNG header
    img_content = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15\xc4\x89'
    files = {"input_images": ("test.png", img_content, "image/png")}
    data = {
        "lang": "por",
        "mode": "accurate",
        "auto_detect": "true"
    }

    response = client.post("/extract_text", files=files, data=data)

    assert response.status_code == 200
    mock_ocr_read_image.assert_called_once()

    # Verify arguments passed to read_image
    call_args = mock_ocr_read_image.call_args
    assert call_args.kwargs['lang'] == 'por'
    assert call_args.kwargs['mode'] == 'accurate'
    assert call_args.kwargs['auto'] is True

def test_extract_text_auto_lang(mock_ocr_read_image):
    # Valid PNG header
    img_content = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15\xc4\x89'
    files = {"input_images": ("test.png", img_content, "image/png")}
    data = {
        "lang": "auto"
    }

    response = client.post("/extract_text", files=files, data=data)

    assert response.status_code == 200
    mock_ocr_read_image.assert_called_once()

    call_args = mock_ocr_read_image.call_args
    assert call_args.kwargs['lang'] == 'eng+por' # Should default to eng+por
    assert call_args.kwargs['auto'] is True # Should be True due to lang='auto'

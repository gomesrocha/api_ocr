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
    # Create a dummy image file for upload
    img_content = b"fake image content"
    files = {"input_images": ("test.png", img_content, "image/png")}

    response = client.post("/extract_text", files=files)

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 1
    assert data[0]["file_name"] == "test.png"
    assert data[0]["text"] == "API OCR text"

    # Verify mock was called
    mock_ocr_read_image.assert_called_once()

    # Check if temp file was cleaned up (hard to check directly since we don't know the exact path)
    # But we can verify no error occurred.

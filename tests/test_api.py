from fastapi.testclient import TestClient
from unittest.mock import patch, AsyncMock
from app.main import app
import os
import io

client = TestClient(app)

@patch("app.api.text_extract.read_image", new_callable=AsyncMock)
def test_extract_text_endpoint(mock_read_image):
    # Setup mock
    mock_read_image.return_value = "Mocked OCR Text"

    # Ensure test file exists
    if not os.path.exists("test.png"):
        with open("test.png", "wb") as f:
            f.write(b"dummy image data")

    with open("test.png", "rb") as f:
        files = [
            ("input_images", ("test.png", f, "image/png"))
        ]

        response = client.post("/extract_text", files=files)

    assert response.status_code == 200
    data = response.json()

    assert "documents" in data
    assert "total_time_taken" in data
    assert len(data["documents"]) == 1
    assert data["documents"][0]["file_name"] == "test.png"
    assert data["documents"][0]["text"] == "Mocked OCR Text"

@patch("app.api.text_extract.read_image", new_callable=AsyncMock)
def test_extract_text_multiple_files(mock_read_image):
    # Setup mock
    mock_read_image.side_effect = ["Text 1", "Text 2"]

    files = [
        ("input_images", ("test1.png", io.BytesIO(b"data1"), "image/png")),
        ("input_images", ("test2.png", io.BytesIO(b"data2"), "image/png"))
    ]

    response = client.post("/extract_text", files=files)

    assert response.status_code == 200
    data = response.json()

    assert len(data["documents"]) == 2
    assert data["documents"][0]["file_name"] == "test1.png"
    assert data["documents"][0]["text"] == "Text 1"
    assert data["documents"][1]["file_name"] == "test2.png"
    assert data["documents"][1]["text"] == "Text 2"

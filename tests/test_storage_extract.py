import os
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from app.main import app

client = TestClient(app)

PDF_HEADER = b"%PDF-1.4\n"

@pytest.fixture
def dummy_pdf(tmp_path):
    p = tmp_path / "dummy.pdf"
    p.write_bytes(PDF_HEADER + b"dummy content")
    return str(p)

@pytest.fixture
def mock_storage_download(dummy_pdf):
    with patch("app.services.storage.download_file_from_storage") as mock:
        # Return a copy so deletion doesn't affect source
        def side_effect(client_id, key):
            import shutil
            dest = dummy_pdf + ".tmp"
            shutil.copy(dummy_pdf, dest)
            return dest
        mock.side_effect = side_effect
        yield mock

def test_extract_pdf_storage_success(mock_storage_download):
    with patch("app.domain.pdf_ocr.process_pdf") as mock_ocr:
        mock_ocr.return_value = "Extracted PDF Text"

        response = client.post(
            "/extract_pdf",
            data={
                "source": "object_storage",
                "client_id": "client_a",
                "object_key": "path/to/file.pdf"
            }
        )

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["text"] == "Extracted PDF Text"
        assert data[0]["file_name"] == "path/to/file.pdf"

        mock_storage_download.assert_called_once_with("client_a", "path/to/file.pdf")
        mock_ocr.assert_called_once()

def test_extract_pdf_storage_missing_params():
    response = client.post(
        "/extract_pdf",
        data={"source": "object_storage"}
    )
    assert response.status_code == 400
    assert "client_id and object_key are required" in response.json()["detail"]

def test_extract_pdf_ambiguous(dummy_pdf):
    with open(dummy_pdf, "rb") as f:
        response = client.post(
            "/extract_pdf",
            data={
                "source": "object_storage",
                "client_id": "client_a",
                "object_key": "path/to/file.pdf"
            },
            files={"input_file": ("test.pdf", f, "application/pdf")}
        )
    assert response.status_code == 400
    assert "Ambiguous request" in response.json()["detail"]

def test_extract_text_storage_success(mock_storage_download):
    with patch("app.domain.ocr.read_image") as mock_ocr:
        mock_ocr.return_value = "Extracted Image Text"

        # Requests/TestClient handles list in data by repeating keys
        data = {
            "source": "object_storage",
            "client_id": "client_a",
            "object_keys": ["img1.png", "img2.jpg"]
        }

        response = client.post("/extract_text", data=data)

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        assert data[0]["file_name"] == "img1.png"
        assert data[0]["text"] == "Extracted Image Text"
        assert data[1]["file_name"] == "img2.jpg"

        assert mock_storage_download.call_count == 2
        assert mock_ocr.call_count == 2

def test_extract_text_storage_missing_params():
    response = client.post(
        "/extract_text",
        data={"source": "object_storage"}
    )
    assert response.status_code == 400
    assert "client_id and object_keys are required" in response.json()["detail"]

def test_extract_pdf_invalid_pdf_header(tmp_path):
    # Mock download returning a non-PDF file
    p = tmp_path / "not_pdf.txt"
    p.write_bytes(b"Not a PDF")

    with patch("app.services.storage.download_file_from_storage") as mock_download:
        mock_download.return_value = str(p)

        response = client.post(
            "/extract_pdf",
            data={
                "source": "object_storage",
                "client_id": "client_a",
                "object_key": "bad.pdf"
            }
        )

        assert response.status_code == 400
        assert "not a valid PDF" in response.json()["detail"]

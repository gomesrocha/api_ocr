import pytest
from unittest.mock import patch, AsyncMock, MagicMock
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

@pytest.fixture
def mock_ocr_read_image():
    with patch("app.domain.ocr.read_image", new_callable=AsyncMock) as mock:
        mock.return_value = "PDF Page Text"
        yield mock

@pytest.fixture
def mock_pdf_tools():
    # Mock both convert_from_path and pdfinfo_from_path
    with patch("app.domain.pdf_ocr.convert_from_path") as mock_convert, \
         patch("app.domain.pdf_ocr.pdfinfo_from_path") as mock_info:

        # Mock convert_from_path to return a list of dummy images
        mock_image = MagicMock()
        mock_convert.return_value = [mock_image, mock_image] # 2 pages

        # Mock pdfinfo to return page count
        mock_info.return_value = {"Pages": 2}

        yield mock_convert, mock_info

def test_extract_pdf_success(mock_ocr_read_image, mock_pdf_tools):
    mock_convert, mock_info = mock_pdf_tools

    # Valid PDF header
    pdf_content = b'%PDF-1.4\n'
    files = {"input_file": ("test.pdf", pdf_content, "application/pdf")}

    response = client.post("/extract_pdf", files=files)

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert "--- Page 1 ---" in data[0]["text"]
    assert "--- Page 2 ---" in data[0]["text"]
    assert "PDF Page Text" in data[0]["text"]

def test_extract_pdf_page_limit_exceeded(mock_ocr_read_image, mock_pdf_tools):
    mock_convert, mock_info = mock_pdf_tools

    # Simulate 15 pages
    mock_info.return_value = {"Pages": 15}

    pdf_content = b'%PDF-1.4\n'
    files = {"input_file": ("large.pdf", pdf_content, "application/pdf")}

    response = client.post("/extract_pdf", files=files)

    assert response.status_code == 400
    assert "Limit is 10" in response.json()["detail"]

def test_extract_pdf_force_processing(mock_ocr_read_image, mock_pdf_tools):
    mock_convert, mock_info = mock_pdf_tools

    # Simulate 15 pages
    mock_info.return_value = {"Pages": 15}
    # Mock convert to return 15 images (dummy)
    mock_convert.return_value = [MagicMock()] * 15

    pdf_content = b'%PDF-1.4\n'
    files = {"input_file": ("large.pdf", pdf_content, "application/pdf")}
    data = {"force_processing": "true"}

    response = client.post("/extract_pdf", files=files, data=data)

    assert response.status_code == 200
    # Should process successfully
    assert len(response.json()) == 1

def test_extract_pdf_invalid_file(mock_ocr_read_image, mock_pdf_tools):
    # Text file content
    txt_content = b"Not a PDF"
    files = {"input_file": ("fake.pdf", txt_content, "application/pdf")}

    response = client.post("/extract_pdf", files=files)

    assert response.status_code == 400
    assert "Invalid file type" in response.json()["detail"] or "Could not determine" in response.json()["detail"]

def test_extract_pdf_with_ner(mock_ocr_read_image, mock_pdf_tools):
    mock_convert, mock_info = mock_pdf_tools

    # Valid PDF header
    pdf_content = b'%PDF-1.4\n'
    files = {"input_file": ("test.pdf", pdf_content, "application/pdf")}

    # Mock NER
    with patch("app.api.pdf_extract.ner.extract_entities") as mock_ner:
        mock_ner.return_value = [{"text": "Entity", "label": "LOC", "start": 0, "end": 6}]

        response = client.post("/extract_pdf", files=files)

        assert response.status_code == 200
        data = response.json()
        assert "entities" in data[0]
        assert len(data[0]["entities"]) == 1
        assert data[0]["entities"][0]["text"] == "Entity"

        mock_ner.assert_called_once()

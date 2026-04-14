from fastapi.testclient import TestClient
from app.main import app
from unittest.mock import patch, AsyncMock, MagicMock
from app.model.StructuredSchema import StructuredDocumentData, DocumentEntity
import pytest

client = TestClient(app)

@pytest.fixture
def mock_ocr():
    with patch("app.domain.ocr.read_image", new_callable=AsyncMock) as mock:
        mock.return_value = "Raw text from image"
        yield mock

@pytest.fixture
def mock_pdf_ocr():
    with patch("app.domain.pdf_ocr.process_pdf", new_callable=AsyncMock) as mock:
        mock.return_value = "Raw text from pdf"
        yield mock

@pytest.fixture
def mock_ner():
    with patch("app.domain.ner.extract_entities") as mock:
        mock.return_value = [{"text": "Apple", "label": "ORG"}]
        yield mock

@pytest.fixture
def mock_file_validate():
    with patch("app.domain.fileUpload.validate_image_file") as mock:
        yield mock

def test_extract_structured_local(mock_ocr, mock_ner, mock_file_validate):
    img_content = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15\xc4\x89'
    files = {"input_files": ("test.png", img_content, "image/png")}
    data = {
        "model_provider": "local_tesseract"
    }

    response = client.post("/extract_structured", files=files, data=data)

    print(response.json() if response.status_code != 200 else "OK")

    assert response.status_code == 200
    res_data = response.json()
    assert isinstance(res_data, list)
    assert len(res_data) == 1
    assert res_data[0]["file_name"] == "test.png"
    assert res_data[0]["provider_used"] == "local_tesseract"
    assert res_data[0]["data"]["document_type"] == "unknown"
    assert len(res_data[0]["data"]["entities"]) == 1
    assert res_data[0]["data"]["entities"][0]["text"] == "Apple"

    mock_ocr.assert_called_once()
    mock_ner.assert_called_once()

def test_extract_structured_llm(mock_ocr, mock_file_validate):
    img_content = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15\xc4\x89'
    files = {"input_files": ("test.png", img_content, "image/png")}
    data = {
        "model_provider": "openai",
        "model_name": "gpt-4o-mini"
    }

    with patch("app.domain.structured_extraction.instructor.from_litellm") as mock_instructor:
        mock_client = MagicMock()
        mock_client.chat.completions.create.return_value = StructuredDocumentData(
            document_type="receipt",
            key_values=[],
            tables=[],
            entities=[DocumentEntity(text="Google", label="ORG")],
            text_summary="A receipt from Google."
        )
        mock_instructor.return_value = mock_client

        response = client.post("/extract_structured", files=files, data=data)

        assert response.status_code == 200
        res_data = response.json()
        assert res_data[0]["provider_used"] == "openai"
        assert res_data[0]["model_used"] == "gpt-4o-mini"
        assert res_data[0]["data"]["document_type"] == "receipt"
        assert res_data[0]["data"]["entities"][0]["text"] == "Google"

        mock_ocr.assert_called_once()

def test_extract_structured_pdf(mock_pdf_ocr, mock_ner):
    pdf_content = b'%PDF-1.4\n1 0 obj\n<<\n/Type /Catalog\n/Outlines 2 0 R\n/Pages 3 0 R\n>>\nendobj\n'
    files = {"input_files": ("test.pdf", pdf_content, "application/pdf")}
    data = {
        "model_provider": "local_tesseract"
    }

    response = client.post("/extract_structured", files=files, data=data)

    assert response.status_code == 200
    res_data = response.json()
    assert res_data[0]["file_name"] == "test.pdf"

    mock_pdf_ocr.assert_called_once()

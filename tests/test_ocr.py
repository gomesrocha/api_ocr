import pytest
from unittest.mock import patch, MagicMock
from app.domain.ocr import read_image

@pytest.mark.asyncio
async def test_read_image():
    # Arrange
    img_path = "tests/testeapi.png"
    lang = 'eng'
    expected_text = "API OCR a way to extract text from images"

    # Mock pytesseract.image_to_string
    with patch("app.domain.ocr.pytesseract.image_to_string") as mock_tesseract:
        mock_tesseract.return_value = expected_text

        # Act
        actual_text = await read_image(img_path, lang=lang)

        # Assert
        assert actual_text == expected_text
        mock_tesseract.assert_called_once_with(img_path, lang=lang)

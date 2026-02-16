import pytest
from unittest.mock import patch
from app.domain.ocr import read_image

@pytest.mark.asyncio
async def test_read_image():
    # Arrange
    img_path = "./testeapi.png"
    expected_text = "API OCR a way to extract text from images"

    # Mock pytesseract.image_to_string
    with patch("pytesseract.image_to_string") as mock_tesseract:
        mock_tesseract.return_value = expected_text

        # Act
        actual_text = await read_image(img_path)

        # Assert
        assert actual_text == expected_text
        mock_tesseract.assert_called_once_with(img_path, lang='eng')

@pytest.mark.asyncio
async def test_read_image_error():
    # Arrange
    img_path = "./invalid.png"

    # Mock pytesseract to raise an exception
    with patch("pytesseract.image_to_string") as mock_tesseract:
        mock_tesseract.side_effect = Exception("Test Error")

        # Act
        actual_text = await read_image(img_path)

        # Assert
        assert "[ERROR]" in actual_text

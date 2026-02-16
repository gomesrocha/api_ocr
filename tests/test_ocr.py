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
        # Mock Image.open to avoid actual file I/O and return a mock image
        with patch("app.domain.ocr.Image.open") as mock_open:
            mock_image = MagicMock()
            mock_open.return_value = mock_image

            mock_tesseract.return_value = expected_text

            # Act
            actual_text = await read_image(img_path, lang=lang)

            # Assert
            assert actual_text == expected_text
            # Verify call args: image object, lang, and default config
            mock_tesseract.assert_called_once_with(mock_image, lang=lang, config=' --psm 3')

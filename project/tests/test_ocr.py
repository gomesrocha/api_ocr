import asyncio
import pytesseract
import pytest
from app.domain.ocr import read_image

def compare_texts(texto1, texto2):
  """
  Compara dois textos por aproximação.

  Args:
    texto1 (str): O primeiro texto.
    texto2 (str): O segundo texto.

  Returns:
    float: Um valor entre 0 e 1, onde 0 significa que os textos são completamente diferentes e 1 significa que os textos são idênticos.
  """

  # Converte os textos para minúsculas.
  texto1 = texto1.lower()
  texto2 = texto2.lower()

  # Remove os espaços em branco dos textos.
  texto1 = texto1.strip()
  texto2 = texto2.strip()

  # Conta o número de caracteres comuns nos textos.
  caracteres_comuns = len(set(texto1) & set(texto2))

  # Calcula o comprimento total dos textos.
  comprimento_total = len(texto1) + len(texto2)

  # Calcula o índice de similaridade.
  indice_de_similaridade = caracteres_comuns / comprimento_total

  return indice_de_similaridade

@pytest.mark.asyncio
async def test_read_image():
    # Arrange
    img_path = "./testeapi.png"
    lang = 'eng'

    # Act
    actual_text = await read_image(img_path, lang=lang)
    expected_text = "API OCR a way to extract text from images"

    # Assert
    relevancia = compare_texts(actual_text, expected_text)   
    assert relevancia > 0.0


import pytesseract
from PIL import Image
import os

# Configurar o Tesseract com suporte a múltiplos idiomas
# Suporte a inglês e português
tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
op.add_argument('--oem', type=int, default=3)
op.add_argument('--psm', type=int, default=6)
pytesseract.pytesseract.tesseract_cmd = tesseract_cmd

# Função para extrair texto de uma imagem com suporte a múltiplos idiomas
def extract_text_from_image(image_path):
    try:
        img = Image.open(image_path)
        custom_config = '--oem 3 --psm 6 -l eng+por'
        text = pytesseract.image_to_string(img, config=custom_config)
        return text
    except Exception as e:
        return str(e)

# Exemplo de uso da função
if __name__ == '__main__':
    image_path = 'images/example.png'
    extracted_text = extract_text_from_image(image_path)
    print('Texto extraído: ' + extracted_text)
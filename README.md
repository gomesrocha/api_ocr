# API_OCR

<p align="center">
 <img width="100px" src="https://images-na.ssl-images-amazon.com/images/I/610oV8UUi2L.png" align="center" alt="API_OCR" />
 <h2 align="center">API_OCR</h2>
 <p align="center">High-performance OCR API using FastAPI and Tesseract / API de OCR de alta performance usando FastAPI e Tesseract</p>
</p>

---

## 🇺🇸 English

### Overview
This project provides a robust API for Optical Character Recognition (OCR) capable of extracting text from images. It supports multiple languages (English and Portuguese), mixed-language documents, and offers configurable processing modes for speed or accuracy.

### Features
- **Multi-language Support**: English (`eng`), Portuguese (`por`), and mixed (`eng+por`).
- **Processing Modes**:
  - `fast`: Quick extraction for clear documents.
  - `accurate`: Enhanced preprocessing (rescaling, contrast adjustment) for better results on difficult images.
- **Auto-Detection**: Orientation and Script Detection (OSD) to handle rotated images or unknown scripts.
- **Strict Validation**: Validates file types via magic bytes (MIME type verification) to ensure security.
- **Dockerized**: Optimized multi-stage Docker build for easy deployment.

### Installation & Running

#### Using Docker (Recommended)
```bash
# Build the image
docker build -t api_ocr .

# Run the container
docker run -p 8080:8080 api_ocr
```
The API will be available at `http://localhost:8080`.

#### Local Development
Prerequisites: Python 3.12+, `uv` (dependency manager), and Tesseract OCR installed on your system.

```bash
# Install dependencies
uv sync

# Run the server
uv run uvicorn app.main:app --reload --port 8080
```

### API Usage

#### Extract Text
**Endpoint**: `POST /extract_text`

**Parameters (Form Data):**
- `input_images`: List of image files (JPEG, PNG, WEBP, etc.).
- `lang`: Language code. Options: `eng`, `por`, `eng+por` (default), or `auto`.
- `mode`: Processing mode. Options: `fast` (default), `accurate`.
- `auto_detect`: Boolean (`true`/`false`). Explicitly enable OSD.

**Example (cURL):**
```bash
curl -X 'POST' \
  'http://localhost:8080/extract_text' \
  -H 'accept: application/json' \
  -H 'Content-Type: multipart/form-data' \
  -F 'input_images=@document.jpg;type=image/jpeg' \
  -F 'lang=por' \
  -F 'mode=accurate'
```

### Development Guide

#### Architecture
- **FastAPI**: Handles HTTP requests and validation.
- **Tesseract OCR**: The core OCR engine.
- **Pillow (PIL)**: Used for image preprocessing in `accurate` mode.
- **Filetype**: Validates image magic bytes securely.
- **AsyncIO**: OCR tasks run in thread pools to prevent blocking the event loop.

#### Testing
Run tests using `pytest`:
```bash
uv run pytest
```

---

## 🇧🇷 Português

### Visão Geral
Este projeto fornece uma API robusta para Reconhecimento Óptico de Caracteres (OCR) capaz de extrair texto de imagens. Suporta múltiplos idiomas (Inglês e Português), documentos com idiomas mistos e oferece modos de processamento configuráveis para velocidade ou precisão.

### Funcionalidades
- **Suporte Multi-idioma**: Inglês (`eng`), Português (`por`) e misto (`eng+por`).
- **Modos de Processamento**:
  - `fast` (Rápido): Extração veloz para documentos nítidos.
  - `accurate` (Preciso): Pré-processamento aprimorado (redimensionamento, ajuste de contraste) para melhores resultados em imagens difíceis.
- **Detecção Automática**: Detecção de Orientação e Script (OSD) para lidar com imagens rotacionadas ou scripts desconhecidos.
- **Validação Rigorosa**: Valida tipos de arquivos via *magic bytes* (verificação de tipo MIME) para garantir segurança.
- **Dockerizado**: Build Docker multi-estágio otimizado para fácil implantação.

### Instalação e Execução

#### Usando Docker (Recomendado)
```bash
# Construir a imagem
docker build -t api_ocr .

# Rodar o container
docker run -p 8080:8080 api_ocr
```
A API estará disponível em `http://localhost:8080`.

#### Desenvolvimento Local
Pré-requisitos: Python 3.12+, `uv` (gerenciador de dependências) e Tesseract OCR instalado no sistema.

```bash
# Instalar dependências
uv sync

# Rodar o servidor
uv run uvicorn app.main:app --reload --port 8080
```

### Uso da API

#### Extrair Texto
**Endpoint**: `POST /extract_text`

**Parâmetros (Form Data):**
- `input_images`: Lista de arquivos de imagem (JPEG, PNG, WEBP, etc.).
- `lang`: Código do idioma. Opções: `eng`, `por`, `eng+por` (padrão) ou `auto`.
- `mode`: Modo de processamento. Opções: `fast` (padrão), `accurate`.
- `auto_detect`: Booleano (`true`/`false`). Habilita explicitamente o OSD.

**Exemplo (cURL):**
```bash
curl -X 'POST' \
  'http://localhost:8080/extract_text' \
  -H 'accept: application/json' \
  -H 'Content-Type: multipart/form-data' \
  -F 'input_images=@documento.jpg;type=image/jpeg' \
  -F 'lang=por' \
  -F 'mode=accurate'
```

### Guia de Desenvolvimento

#### Arquitetura
- **FastAPI**: Gerencia requisições HTTP e validação.
- **Tesseract OCR**: O motor principal de OCR.
- **Pillow (PIL)**: Usado para pré-processamento de imagens no modo `accurate`.
- **Filetype**: Valida *magic bytes* de imagens de forma segura.
- **AsyncIO**: Tarefas de OCR rodam em *thread pools* para não bloquear o *event loop*.

#### Testes
Execute os testes usando `pytest`:
```bash
uv run pytest
```

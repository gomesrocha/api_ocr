from fastapi import FastAPI
from app.api import text_extract, pdf_extract, structured_extract

app = FastAPI(title="API_OCR")

app.include_router(text_extract.router)
app.include_router(pdf_extract.router)
app.include_router(structured_extract.router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)

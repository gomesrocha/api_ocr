from pydantic import BaseModel
from typing import List

class TextExtractDocument(BaseModel):
    file_name: str
    text: str

class TextExtractResponse(BaseModel):
    documents: List[TextExtractDocument]
    total_time_taken: str

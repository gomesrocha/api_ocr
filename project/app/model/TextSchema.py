from pydantic import BaseModel


class TextExtractDocument(BaseModel):
    file_name: str
    text: str
    time_taken: str
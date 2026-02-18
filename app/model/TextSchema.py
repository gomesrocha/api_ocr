from pydantic import BaseModel
from typing import List, Optional

class Entity(BaseModel):
    text: str
    label: str
    start: int
    end: int

class TextExtractDocument(BaseModel):
    file_name: str
    text: str
    entities: Optional[List[Entity]] = None
    time_taken: str

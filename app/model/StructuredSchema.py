from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any

class KeyValue(BaseModel):
    key: str = Field(description="The field name or key")
    value: str | float | int | bool | None = Field(description="The extracted value")

class TableRow(BaseModel):
    cells: List[str] = Field(description="The cells in this row")

class Table(BaseModel):
    title: Optional[str] = Field(None, description="Optional title or caption of the table")
    columns: List[str] = Field(description="Column headers")
    rows: List[TableRow] = Field(description="Rows of the table")

class DocumentEntity(BaseModel):
    text: str = Field(description="The text of the entity")
    label: str = Field(description="The type of the entity (e.g., PER, ORG, LOC, DATE, MONEY)")

class StructuredDocumentData(BaseModel):
    document_type: str = Field(description="Inferred type of the document (e.g., 'invoice', 'scientific_paper', 'receipt', 'contract', 'unknown')")
    key_values: List[KeyValue] = Field(default_factory=list, description="Extracted key-value pairs from the document")
    tables: List[Table] = Field(default_factory=list, description="Extracted tables from the document")
    entities: List[DocumentEntity] = Field(default_factory=list, description="Named entities found in the document")
    text_summary: Optional[str] = Field(None, description="A brief summary of the document's content")

class StructuredExtractionResult(BaseModel):
    file_name: str
    provider_used: str
    model_used: Optional[str] = None
    data: StructuredDocumentData
    time_taken: str

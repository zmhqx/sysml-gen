from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class DocumentGenerate(BaseModel):
    project_id: int
    model_id: int
    template_id: int


class DocumentOut(BaseModel):
    id: int
    project_id: int
    model_id: int
    template_id: int
    document_name: str
    content: str
    file_path: str
    export_format: str
    status: str
    generate_message: str
    operator_id: int
    generate_time: Optional[datetime] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class DocumentListResponse(BaseModel):
    items: List[DocumentOut]
    total: int
    page: int
    page_size: int

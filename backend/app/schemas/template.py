from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class TemplateCreate(BaseModel):
    name: str
    template_type: str
    content: str = ""


class TemplateUpdate(BaseModel):
    name: Optional[str] = None
    template_type: Optional[str] = None
    content: Optional[str] = None
    status: Optional[str] = None


class TemplateOut(BaseModel):
    id: int
    name: str
    template_type: str
    content: str
    file_path: str
    status: str
    creator_id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

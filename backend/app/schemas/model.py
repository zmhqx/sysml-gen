from pydantic import BaseModel, Field
from typing import Optional, Any
from datetime import datetime
from enum import Enum


class ImportMode(str, Enum):
    """与概要 4.4.3 一致：覆盖 / 合并 / 新建（新建与覆盖在首版解析中均先清空再写入）。"""

    replace = "replace"
    merge = "merge"
    new = "new"


class ModelParseRequest(BaseModel):
    import_mode: ImportMode = ImportMode.replace
    run_async: bool = Field(default=True, description="为 True 时后台解析，接口立即返回")


class UploadInitBody(BaseModel):
    project_id: int
    filename: str
    total_chunks: int = Field(..., ge=1, le=5000)
    total_size: int = Field(..., ge=1)
    name: str = ""
    version_tag: str = "v1.0"


class ModelOut(BaseModel):
    id: int
    project_id: int
    name: str
    version_tag: str
    file_path: str
    file_size: int
    file_type: str
    uploader_id: int
    upload_time: Optional[datetime] = None
    parse_status: str
    parse_message: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class ElementOut(BaseModel):
    id: int
    model_id: int
    element_id: str
    element_name: str
    element_type: str
    parent_element_id: str
    description: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class ElementTreeItem(BaseModel):
    id: int
    element_id: str
    element_name: str
    element_type: str
    parent_element_id: str
    children: list["ElementTreeItem"] = []


class ElementUpdate(BaseModel):
    element_name: Optional[str] = None
    description: Optional[str] = None


class RelationshipOut(BaseModel):
    id: int
    model_id: int
    source_element_id: str
    target_element_id: str
    relationship_type: str
    relationship_name: str
    description: str

    class Config:
        from_attributes = True

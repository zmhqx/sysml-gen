from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class LogOut(BaseModel):
    id: int
    log_type: str
    operator_id: Optional[int] = None
    module_name: str
    operation_content: str
    result_status: str
    ip_address: str
    record_time: Optional[datetime] = None

    class Config:
        from_attributes = True


class LogQuery(BaseModel):
    log_type: Optional[str] = None
    module_name: Optional[str] = None
    result_status: Optional[str] = None
    page: int = 1
    page_size: int = 20

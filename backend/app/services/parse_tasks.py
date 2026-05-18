"""后台解析任务（独立 DB 会话，避免与请求内 Session 冲突）。"""
from __future__ import annotations

from app.database import SessionLocal
from app.models.model import SysModel
from app.services.model_import_service import import_model_from_disk, import_model_file


def run_parse_from_disk(model_id: int, import_mode: str) -> None:
    db = SessionLocal()
    try:
        model = db.query(SysModel).filter(SysModel.id == model_id).first()
        if model:
            import_model_from_disk(db, model, import_mode=import_mode)
    finally:
        db.close()


def run_parse_from_bytes(model_id: int, content: bytes, original_filename: str, import_mode: str) -> None:
    """用于刚写入磁盘的单文件上传：内容与磁盘一致。"""
    db = SessionLocal()
    try:
        model = db.query(SysModel).filter(SysModel.id == model_id).first()
        if model:
            import_model_file(db, model, content, original_filename, import_mode=import_mode)
    finally:
        db.close()

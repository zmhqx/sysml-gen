"""模型导入：校验 → 解析 → 按 import_mode 写入数据库。"""
from __future__ import annotations

import os
from typing import Literal

from sqlalchemy.orm import Session

from app.models.model import SysModel, ModelElement, ModelRelationship, ParseStatus
from app.services.format_validator import FormatValidationError, validate_and_load_payload
from app.services.model_parser import parse_model_bytes

ImportMode = Literal["replace", "merge", "new"]


def _inner_ext_from_logical(logical_name: str, payload_ext: str) -> str:
    if payload_ext == ".zip":
        return os.path.splitext(logical_name)[1].lower()
    return payload_ext


def import_model_file(
    db: Session,
    model: SysModel,
    file_content: bytes,
    original_filename: str,
    import_mode: ImportMode = "replace",
) -> tuple[bool, str]:
    """
    对给定字节流执行完整导入（用于上传直传或分片合并后的缓冲区）。
    返回 (success, message)。
    """
    model.parse_status = ParseStatus.PARSING.value
    model.parse_message = ""
    db.commit()

    try:
        payload = validate_and_load_payload(original_filename, file_content)
        inner_ext = _inner_ext_from_logical(payload.logical_name, payload.original_ext)
        if inner_ext not in (".xmi", ".xml", ".json"):
            raise FormatValidationError(f"内层文件类型无效：{inner_ext}")

        parsed = parse_model_bytes(payload.content, inner_ext)
        if not parsed.success:
            msg = "; ".join(parsed.errors) if parsed.errors else "解析失败"
            model.parse_status = ParseStatus.FAILED.value
            model.parse_message = msg[:2000]
            db.commit()
            return False, msg

        if import_mode in ("replace", "new"):
            db.query(ModelRelationship).filter(ModelRelationship.model_id == model.id).delete(
                synchronize_session=False
            )
            db.query(ModelElement).filter(ModelElement.model_id == model.id).delete(
                synchronize_session=False
            )
            for row in parsed.elements:
                db.add(
                    ModelElement(
                        model_id=model.id,
                        element_id=row["element_id"],
                        element_name=row.get("element_name") or "",
                        element_type=row.get("element_type") or "Element",
                        parent_element_id=row.get("parent_element_id") or "",
                        description=row.get("description") or "",
                        attributes=row.get("attributes") or {},
                    )
                )
            for row in parsed.relationships:
                db.add(
                    ModelRelationship(
                        model_id=model.id,
                        source_element_id=row["source_element_id"],
                        target_element_id=row["target_element_id"],
                        relationship_type=row.get("relationship_type") or "",
                        relationship_name=row.get("relationship_name") or "",
                        description=row.get("description") or "",
                    )
                )

        elif import_mode == "merge":
            existing = {
                e.element_id: e
                for e in db.query(ModelElement).filter(ModelElement.model_id == model.id).all()
            }
            for row in parsed.elements:
                eid = row["element_id"]
                if eid in existing:
                    el = existing[eid]
                    el.element_name = row.get("element_name") or el.element_name
                    el.element_type = row.get("element_type") or el.element_type
                    el.parent_element_id = row.get("parent_element_id") or el.parent_element_id or ""
                    el.description = row.get("description") or el.description
                    if row.get("attributes") is not None:
                        el.attributes = row.get("attributes") or {}
                else:
                    db.add(
                        ModelElement(
                            model_id=model.id,
                            element_id=eid,
                            element_name=row.get("element_name") or "",
                            element_type=row.get("element_type") or "Element",
                            parent_element_id=row.get("parent_element_id") or "",
                            description=row.get("description") or "",
                            attributes=row.get("attributes") or {},
                        )
                    )
            db.query(ModelRelationship).filter(ModelRelationship.model_id == model.id).delete(
                synchronize_session=False
            )
            for row in parsed.relationships:
                db.add(
                    ModelRelationship(
                        model_id=model.id,
                        source_element_id=row["source_element_id"],
                        target_element_id=row["target_element_id"],
                        relationship_type=row.get("relationship_type") or "",
                        relationship_name=row.get("relationship_name") or "",
                        description=row.get("description") or "",
                    )
                )
        else:
            raise FormatValidationError(f"未知 import_mode：{import_mode}")

        model.parse_status = ParseStatus.SUCCESS.value
        model.parse_message = f"已导入 {parsed.element_count} 个元素，{len(parsed.relationships)} 条关系"
        db.commit()
        return True, model.parse_message

    except FormatValidationError as e:
        model.parse_status = ParseStatus.FAILED.value
        model.parse_message = e.message[:2000]
        db.commit()
        return False, e.message
    except Exception as e:  # noqa: BLE001
        model.parse_status = ParseStatus.FAILED.value
        model.parse_message = str(e)[:2000]
        db.commit()
        return False, str(e)


def import_model_from_disk(
    db: Session,
    model: SysModel,
    import_mode: ImportMode = "replace",
) -> tuple[bool, str]:
    """从 model.file_path 读取并导入。"""
    if not model.file_path or not os.path.isfile(model.file_path):
        model.parse_status = ParseStatus.FAILED.value
        model.parse_message = "模型文件不存在"
        db.commit()
        return False, "模型文件不存在"
    with open(model.file_path, "rb") as f:
        content = f.read()
    base_name = os.path.basename(model.file_path)
    return import_model_file(db, model, content, base_name, import_mode=import_mode)

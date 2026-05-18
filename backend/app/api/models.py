import json
import os
import shutil
import uuid

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Optional

from app.database import get_db
from app.core.deps import get_current_user
from app.core.config import settings
from app.core.project_access import require_project_write, require_project_read, require_model_access
from app.models.user import User, UserRole
from app.models.project import Project
from app.models.model import SysModel, ModelElement, ModelRelationship, ParseStatus
from app.schemas.model import (
    ModelOut,
    ElementOut,
    ElementTreeItem,
    ElementUpdate,
    RelationshipOut,
    ModelParseRequest,
    UploadInitBody,
    ImportMode,
)
from app.services.log_service import create_log
from app.models.log import LogType
from app.services.format_validator import (
    FormatValidationError,
    validate_extension,
    validate_size,
    MAX_UPLOAD_BYTES,
)
from app.services.model_import_service import import_model_from_disk, import_model_file
from app.services.parse_tasks import run_parse_from_disk, run_parse_from_bytes

router = APIRouter(prefix="/api/v1/models", tags=["models"])


@router.post("/upload/init")
def upload_init(
    body: UploadInitBody,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """分片上传：创建会话目录并写入元数据。"""
    require_project_write(db, current_user, body.project_id)
    try:
        validate_extension(body.filename)
        if body.total_size > MAX_UPLOAD_BYTES:
            raise FormatValidationError(
                f"文件过大，上限 {MAX_UPLOAD_BYTES // (1024 * 1024)} MB"
            )
    except FormatValidationError as e:
        raise HTTPException(status_code=400, detail=e.message) from e

    upload_id = uuid.uuid4().hex
    base = os.path.join(settings.storage_model_dir, "_uploads", upload_id)
    os.makedirs(base, exist_ok=True)
    meta = {
        "project_id": body.project_id,
        "filename": body.filename,
        "total_chunks": body.total_chunks,
        "total_size": body.total_size,
        "name": body.name,
        "version_tag": body.version_tag,
        "user_id": current_user.id,
    }
    with open(os.path.join(base, "meta.json"), "w", encoding="utf-8") as f:
        json.dump(meta, f, ensure_ascii=False)
    return {"upload_id": upload_id, "max_chunk_bytes": 5 * 1024 * 1024}


@router.post("/upload/chunk")
def upload_chunk(
    upload_id: str = Form(...),
    chunk_index: int = Form(...),
    total_chunks: int = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """分片上传：写入单分片（建议每片不超过 5MB）。"""
    base = os.path.join(settings.storage_model_dir, "_uploads", upload_id)
    meta_path = os.path.join(base, "meta.json")
    if not os.path.isfile(meta_path):
        raise HTTPException(status_code=404, detail="上传会话不存在或已过期")
    with open(meta_path, encoding="utf-8") as f:
        meta = json.load(f)
    if meta.get("user_id") != current_user.id:
        raise HTTPException(status_code=403, detail="无权写入该上传会话")
    if meta.get("total_chunks") != total_chunks:
        raise HTTPException(status_code=400, detail="total_chunks 与 init 不一致")
    if chunk_index < 0 or chunk_index >= total_chunks:
        raise HTTPException(status_code=400, detail="chunk_index 越界")
    data = file.file.read()
    part_path = os.path.join(base, f"part_{chunk_index:05d}")
    with open(part_path, "wb") as out:
        out.write(data)
    return {"upload_id": upload_id, "chunk_index": chunk_index, "received_bytes": len(data)}


@router.post("/upload/complete", response_model=ModelOut)
def upload_complete(
    background_tasks: BackgroundTasks,
    upload_id: str = Form(...),
    import_mode: ImportMode = Form(ImportMode.replace),
    auto_parse: bool = Form(True),
    run_async: bool = Form(True),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """分片上传：合并分片、落盘、创建模型记录并可触发解析。"""
    base = os.path.join(settings.storage_model_dir, "_uploads", upload_id)
    meta_path = os.path.join(base, "meta.json")
    if not os.path.isfile(meta_path):
        raise HTTPException(status_code=404, detail="上传会话不存在")
    with open(meta_path, encoding="utf-8") as f:
        meta = json.load(f)
    if meta.get("user_id") != current_user.id:
        raise HTTPException(status_code=403, detail="无权完成该上传会话")

    project_id = int(meta["project_id"])
    require_project_write(db, current_user, project_id)
    total_chunks = int(meta["total_chunks"])
    filename = meta["filename"]
    total_size = int(meta["total_size"])

    buf = bytearray()
    for i in range(total_chunks):
        part_path = os.path.join(base, f"part_{i:05d}")
        if not os.path.isfile(part_path):
            raise HTTPException(status_code=400, detail=f"缺少分片 part_{i:05d}")
        with open(part_path, "rb") as pf:
            buf.extend(pf.read())
    content = bytes(buf)
    if len(content) != total_size:
        raise HTTPException(
            status_code=400,
            detail=f"合并大小不一致：期望 {total_size}，实际 {len(content)}",
        )
    try:
        validate_size(content)
        validate_extension(filename)
    except FormatValidationError as e:
        raise HTTPException(status_code=400, detail=e.message) from e

    file_ext = os.path.splitext(filename)[1].lower()
    saved_name = f"{uuid.uuid4().hex}{file_ext}"
    saved_path = os.path.join(settings.storage_model_dir, saved_name)
    os.makedirs(settings.storage_model_dir, exist_ok=True)
    with open(saved_path, "wb") as f:
        f.write(content)

    model = SysModel(
        project_id=project_id,
        name=meta.get("name") or filename,
        version_tag=meta.get("version_tag") or "v1.0",
        file_path=saved_path,
        file_size=len(content),
        file_type=file_ext,
        uploader_id=current_user.id,
        parse_status=ParseStatus.PENDING.value,
    )
    db.add(model)
    db.commit()
    db.refresh(model)
    create_log(db, LogType.OPERATION, current_user.id, "model",
               f"分片上传完成 {model.name} ({filename})")

    try:
        shutil.rmtree(base, ignore_errors=True)
    except OSError:
        pass

    if auto_parse:
        if run_async:
            model.parse_message = "解析任务已提交，请稍后刷新查看状态"
            db.commit()
            background_tasks.add_task(run_parse_from_disk, model.id, import_mode.value)
        else:
            import_model_from_disk(db, model, import_mode=import_mode.value)
        db.refresh(model)

    return model


@router.get("", response_model=List[ModelOut])
def list_models(
    project_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = db.query(SysModel)
    if current_user.role == UserRole.MEMBER.value:
        query = query.join(Project, Project.id == SysModel.project_id).filter(
            Project.owner_id == current_user.id
        )
    if project_id is not None:
        require_project_read(db, current_user, project_id)
        query = query.filter(SysModel.project_id == project_id)
    return query.order_by(SysModel.created_at.desc()).all()


@router.post("/upload", response_model=ModelOut)
def upload_model(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    project_id: int = Form(...),
    name: str = Form(""),
    version_tag: str = Form("v1.0"),
    import_mode: ImportMode = Form(ImportMode.replace),
    auto_parse: bool = Form(True),
    run_async: bool = Form(True),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    require_project_write(db, current_user, project_id)
    try:
        validate_extension(file.filename or "")
    except FormatValidationError as e:
        raise HTTPException(status_code=400, detail=e.message) from e

    content = file.file.read()
    try:
        validate_size(content)
    except FormatValidationError as e:
        raise HTTPException(status_code=400, detail=e.message) from e

    file_ext = os.path.splitext(file.filename or "")[1].lower()
    saved_name = f"{uuid.uuid4().hex}{file_ext}"
    saved_path = os.path.join(settings.storage_model_dir, saved_name)
    os.makedirs(settings.storage_model_dir, exist_ok=True)
    with open(saved_path, "wb") as f:
        f.write(content)
    model = SysModel(
        project_id=project_id,
        name=name or (file.filename or "model"),
        version_tag=version_tag,
        file_path=saved_path,
        file_size=len(content),
        file_type=file_ext,
        uploader_id=current_user.id,
        parse_status=ParseStatus.PENDING.value,
    )
    db.add(model)
    db.commit()
    db.refresh(model)
    create_log(db, LogType.OPERATION, current_user.id, "model",
               f"Uploaded model {model.name} ({file.filename})")

    if auto_parse:
        mode = import_mode.value
        if run_async:
            model.parse_message = "解析任务已提交，请稍后刷新查看状态"
            db.commit()
            background_tasks.add_task(
                run_parse_from_bytes,
                model.id,
                content,
                file.filename or saved_name,
                mode,
            )
        else:
            import_model_file(db, model, content, file.filename or saved_name, import_mode=mode)  # type: ignore[arg-type]
        db.refresh(model)

    return model


@router.post("/{model_id}/parse", response_model=ModelOut)
def parse_model(
    model_id: int,
    background_tasks: BackgroundTasks,
    body: ModelParseRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """对已上传文件重新执行解析导入。"""
    model = db.query(SysModel).filter(SysModel.id == model_id).first()
    if not model:
        raise HTTPException(status_code=404, detail="Model not found")
    require_model_access(db, current_user, model, write=True)
    if body.run_async:
        model.parse_message = "解析任务已提交，请稍后刷新查看状态"
        model.parse_status = ParseStatus.PENDING.value
        db.commit()
        background_tasks.add_task(run_parse_from_disk, model_id, body.import_mode.value)
        db.refresh(model)
        create_log(db, LogType.OPERATION, current_user.id, "model", f"已提交异步解析 id={model_id}")
        return model
    ok, msg = import_model_from_disk(db, model, import_mode=body.import_mode.value)
    db.refresh(model)
    if not ok:
        raise HTTPException(status_code=400, detail=msg)
    create_log(db, LogType.OPERATION, current_user.id, "model", f"解析模型成功 id={model_id}")
    return model


@router.get("/{model_id}", response_model=ModelOut)
def get_model(
    model_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    model = db.query(SysModel).filter(SysModel.id == model_id).first()
    if not model:
        raise HTTPException(status_code=404, detail="Model not found")
    require_model_access(db, current_user, model, write=False)
    return model


@router.delete("/{model_id}")
def delete_model(
    model_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    model = db.query(SysModel).filter(SysModel.id == model_id).first()
    if not model:
        raise HTTPException(status_code=404, detail="Model not found")
    require_model_access(db, current_user, model, write=True)
    if os.path.exists(model.file_path):
        os.remove(model.file_path)
    db.delete(model)
    db.commit()
    return {"detail": "Model deleted"}


@router.get("/{model_id}/elements", response_model=List[ElementOut])
def list_elements(
    model_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    model = db.query(SysModel).filter(SysModel.id == model_id).first()
    if not model:
        raise HTTPException(status_code=404, detail="Model not found")
    require_model_access(db, current_user, model, write=False)
    return db.query(ModelElement).filter(ModelElement.model_id == model_id).all()


@router.get("/{model_id}/elements/tree", response_model=List[ElementTreeItem])
def get_element_tree(
    model_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    model = db.query(SysModel).filter(SysModel.id == model_id).first()
    if not model:
        raise HTTPException(status_code=404, detail="Model not found")
    require_model_access(db, current_user, model, write=False)
    elements = db.query(ModelElement).filter(ModelElement.model_id == model_id).all()
    elem_map: dict[str, ElementTreeItem] = {}
    roots: list[ElementTreeItem] = []
    for e in elements:
        item = ElementTreeItem(
            id=e.id,
            element_id=e.element_id,
            element_name=e.element_name,
            element_type=e.element_type,
            parent_element_id=e.parent_element_id or "",
        )
        elem_map[e.element_id] = item
    for eid, item in elem_map.items():
        if item.parent_element_id and item.parent_element_id in elem_map:
            elem_map[item.parent_element_id].children.append(item)
        else:
            roots.append(item)
    return roots


@router.get("/{model_id}/elements/search", response_model=List[ElementOut])
def search_elements(
    model_id: int,
    q: str = "",
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    model = db.query(SysModel).filter(SysModel.id == model_id).first()
    if not model:
        raise HTTPException(status_code=404, detail="Model not found")
    require_model_access(db, current_user, model, write=False)
    if not q:
        return []
    return (
        db.query(ModelElement)
        .filter(
            ModelElement.model_id == model_id,
            ModelElement.element_name.like(f"%{q}%"),
        )
        .all()
    )


@router.get("/{model_id}/elements/{element_id}", response_model=ElementOut)
def get_element(
    model_id: int,
    element_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    model = db.query(SysModel).filter(SysModel.id == model_id).first()
    if not model:
        raise HTTPException(status_code=404, detail="Model not found")
    require_model_access(db, current_user, model, write=False)
    elem = (
        db.query(ModelElement)
        .filter(
            ModelElement.model_id == model_id,
            ModelElement.element_id == element_id,
        )
        .first()
    )
    if not elem:
        raise HTTPException(status_code=404, detail="Element not found")
    return elem


@router.put("/{model_id}/elements/{element_id}", response_model=ElementOut)
def update_element(
    model_id: int,
    element_id: str,
    update_in: ElementUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    model = db.query(SysModel).filter(SysModel.id == model_id).first()
    if not model:
        raise HTTPException(status_code=404, detail="Model not found")
    require_model_access(db, current_user, model, write=True)
    elem = (
        db.query(ModelElement)
        .filter(
            ModelElement.model_id == model_id,
            ModelElement.element_id == element_id,
        )
        .first()
    )
    if not elem:
        raise HTTPException(status_code=404, detail="Element not found")
    if update_in.element_name is not None:
        elem.element_name = update_in.element_name
    if update_in.description is not None:
        elem.description = update_in.description
    db.commit()
    db.refresh(elem)
    return elem


@router.get("/{model_id}/relationships", response_model=List[RelationshipOut])
def list_relationships(
    model_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    model = db.query(SysModel).filter(SysModel.id == model_id).first()
    if not model:
        raise HTTPException(status_code=404, detail="Model not found")
    require_model_access(db, current_user, model, write=False)
    return db.query(ModelRelationship).filter(ModelRelationship.model_id == model_id).all()

import os
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from typing import Optional

from app.database import get_db
from app.core.deps import get_current_user
from app.core.config import settings
from app.core.project_access import require_project_write, require_project_read, require_model_access
from app.models.user import User, UserRole
from app.models.project import Project
from app.models.document import Document, DocumentStatus
from app.models.model import SysModel, ModelElement
from app.models.template import Template
from app.schemas.document import DocumentGenerate, DocumentOut, DocumentListResponse
from app.services.log_service import create_log
from app.models.log import LogType, ResultStatus
from jinja2.sandbox import SandboxedEnvironment

router = APIRouter(prefix="/api/v1/documents", tags=["documents"])

try:
    from docx import Document as DocxDocument
    from docx.shared import Pt, Inches
    HAS_DOCX = True
except ImportError:
    HAS_DOCX = False

try:
    from weasyprint import HTML
    HAS_WEASYPRINT = True
except Exception:
    HAS_WEASYPRINT = False


@router.get("", response_model=DocumentListResponse)
def list_documents(
    project_id: Optional[int] = Query(None, description="按项目筛选"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    q = db.query(Document)
    if project_id is not None:
        require_project_read(db, current_user, project_id)
        q = q.filter(Document.project_id == project_id)
    elif current_user.role == UserRole.MEMBER.value:
        q = q.join(Project, Project.id == Document.project_id).filter(Project.owner_id == current_user.id)
    total = q.count()
    rows = (
        q.order_by(Document.created_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )
    return DocumentListResponse(items=rows, total=total, page=page, page_size=page_size)


@router.post("/generate", response_model=DocumentOut)
def generate_document(doc_in: DocumentGenerate, db: Session = Depends(get_db),
                      current_user: User = Depends(get_current_user)):
    require_project_write(db, current_user, doc_in.project_id)
    model = db.query(SysModel).filter(SysModel.id == doc_in.model_id).first()
    if not model:
        raise HTTPException(status_code=404, detail="Model not found")
    if model.project_id != doc_in.project_id:
        raise HTTPException(status_code=400, detail="模型不属于所选项目")
    require_model_access(db, current_user, model, write=False)
    template = db.query(Template).filter(Template.id == doc_in.template_id).first()
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    elements = db.query(ModelElement).filter(ModelElement.model_id == model.id).all()

    def get_element_by_id(element_id: str):
        row = (
            db.query(ModelElement)
            .filter(ModelElement.model_id == model.id, ModelElement.element_id == element_id)
            .first()
        )
        if not row:
            return None
        return {
            "element_id": row.element_id,
            "name": row.element_name,
            "type": row.element_type,
            "description": row.description,
        }

    def get_requirements_by_module(module_name: str):
        return [
            {"name": e.element_name, "type": e.element_type, "description": e.description}
            for e in elements
            if e.element_type == "Requirement" and module_name in (e.element_name or "")
        ]

    def get_blocks_by_package(package_name: str):
        return [
            {"name": e.element_name, "type": e.element_type, "description": e.description}
            for e in elements
            if e.element_type == "Block" and package_name in (e.element_name or "")
        ]

    # Build context
    context = {
        "project_id": doc_in.project_id,
        "model_name": model.name,
        "model_version": model.version_tag,
        "template_name": template.name,
        "generate_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "elements": [{
            "name": e.element_name,
            "type": e.element_type,
            "description": e.description,
        } for e in elements],
        "get_element_by_id": get_element_by_id,
        "get_requirements_by_module": get_requirements_by_module,
        "get_blocks_by_package": get_blocks_by_package,
    }

    # Render（沙箱环境，防止模板执行危险代码）
    try:
        env = SandboxedEnvironment(autoescape=True)
        jinja_tpl = env.from_string(template.content)
        rendered = jinja_tpl.render(**context)
    except Exception as e:
        doc = Document(
            project_id=doc_in.project_id, model_id=doc_in.model_id,
            template_id=doc_in.template_id,
            document_name=f"{model.name}_{template.name}",
            status=DocumentStatus.FAILED.value,
            generate_message=str(e),
            operator_id=current_user.id,
        )
        db.add(doc)
        db.commit()
        db.refresh(doc)
        create_log(db, LogType.OPERATION, current_user.id, "document",
                   f"Generate document failed: {e}", ResultStatus.FAILED)
        return doc

    doc = Document(
        project_id=doc_in.project_id, model_id=doc_in.model_id,
        template_id=doc_in.template_id,
        document_name=f"{model.name}_{template.name}",
        content=rendered,
        status=DocumentStatus.SUCCESS.value,
        operator_id=current_user.id,
    )
    db.add(doc)
    db.commit()
    db.refresh(doc)
    create_log(db, LogType.OPERATION, current_user.id, "document",
               f"Generated document {doc.document_name}")
    return doc


@router.get("/{doc_id}", response_model=DocumentOut)
def get_document(doc_id: int, db: Session = Depends(get_db),
                 current_user: User = Depends(get_current_user)):
    doc = db.query(Document).filter(Document.id == doc_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    require_project_read(db, current_user, doc.project_id)
    return doc


@router.get("/{doc_id}/preview")
def preview_document(doc_id: int, db: Session = Depends(get_db),
                     current_user: User = Depends(get_current_user)):
    doc = db.query(Document).filter(Document.id == doc_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    require_project_read(db, current_user, doc.project_id)
    return {"content": doc.content, "document_name": doc.document_name}


@router.get("/{doc_id}/download")
def download_document(doc_id: int, fmt: str = "docx",
                      db: Session = Depends(get_db),
                      current_user: User = Depends(get_current_user)):
    doc = db.query(Document).filter(Document.id == doc_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    require_project_write(db, current_user, doc.project_id)
    if fmt == "docx" and HAS_DOCX:
        os.makedirs(settings.document_dir, exist_ok=True)
        filepath = os.path.join(settings.document_dir, f"{doc.document_name}_{doc.id}.docx")
        d = DocxDocument()
        d.add_heading(doc.document_name, 0)
        for line in doc.content.split("\n"):
            d.add_paragraph(line)
        d.save(filepath)
        doc.file_path = filepath
        doc.export_format = "docx"
        db.commit()
        return FileResponse(filepath, filename=f"{doc.document_name}.docx")
    elif fmt == "pdf" and HAS_WEASYPRINT:
        os.makedirs(settings.document_dir, exist_ok=True)
        filepath = os.path.join(settings.document_dir, f"{doc.document_name}_{doc.id}.pdf")
        HTML(string=doc.content).write_pdf(filepath)
        doc.file_path = filepath
        doc.export_format = "pdf"
        db.commit()
        return FileResponse(filepath, filename=f"{doc.document_name}.pdf", media_type="application/pdf")
    elif fmt == "html":
        return {"content": doc.content}
    else:
        if fmt == "pdf" and not HAS_WEASYPRINT:
            raise HTTPException(status_code=503, detail="PDF 导出需要 WeasyPrint，当前环境未安装或加载失败")
        raise HTTPException(status_code=400, detail=f"Unsupported format: {fmt}")


@router.delete("/{doc_id}")
def delete_document(doc_id: int, db: Session = Depends(get_db),
                    current_user: User = Depends(get_current_user)):
    doc = db.query(Document).filter(Document.id == doc_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    require_project_write(db, current_user, doc.project_id)
    if doc.file_path and os.path.exists(doc.file_path):
        os.remove(doc.file_path)
    db.delete(doc)
    db.commit()
    return {"detail": "Document deleted"}

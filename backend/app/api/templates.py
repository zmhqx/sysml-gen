from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.core.deps import get_current_user
from app.models.user import User
from app.models.template import Template, TemplateStatus
from app.schemas.template import TemplateCreate, TemplateUpdate, TemplateOut
from app.services.log_service import create_log
from app.models.log import LogType

router = APIRouter(prefix="/api/v1/templates", tags=["templates"])


@router.get("", response_model=List[TemplateOut])
def list_templates(db: Session = Depends(get_db),
                   current_user: User = Depends(get_current_user)):
    return db.query(Template).order_by(Template.created_at.desc()).all()


@router.post("", response_model=TemplateOut)
def create_template(template_in: TemplateCreate, db: Session = Depends(get_db),
                    current_user: User = Depends(get_current_user)):
    template = Template(
        name=template_in.name,
        template_type=template_in.template_type,
        content=template_in.content,
        creator_id=current_user.id,
    )
    db.add(template)
    db.commit()
    db.refresh(template)
    create_log(db, LogType.OPERATION, current_user.id, "template",
               f"Created template {template.name}")
    return template


@router.get("/{template_id}", response_model=TemplateOut)
def get_template(template_id: int, db: Session = Depends(get_db),
                 current_user: User = Depends(get_current_user)):
    template = db.query(Template).filter(Template.id == template_id).first()
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    return template


@router.put("/{template_id}", response_model=TemplateOut)
def update_template(template_id: int, template_in: TemplateUpdate,
                    db: Session = Depends(get_db),
                    current_user: User = Depends(get_current_user)):
    template = db.query(Template).filter(Template.id == template_id).first()
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    if template_in.name is not None:
        template.name = template_in.name
    if template_in.template_type is not None:
        template.template_type = template_in.template_type
    if template_in.content is not None:
        template.content = template_in.content
    if template_in.status is not None:
        template.status = template_in.status
    db.commit()
    db.refresh(template)
    return template


@router.delete("/{template_id}")
def delete_template(template_id: int, db: Session = Depends(get_db),
                    current_user: User = Depends(get_current_user)):
    template = db.query(Template).filter(Template.id == template_id).first()
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    db.delete(template)
    db.commit()
    return {"detail": "Template deleted"}

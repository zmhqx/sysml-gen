from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.core.deps import get_current_user, require_role
from app.core.project_access import can_view_project
from app.models.user import UserRole
from app.models.user import User
from app.models.project import Project
from app.schemas.project import ProjectCreate, ProjectUpdate, ProjectOut
from app.services.log_service import create_log
from app.models.log import LogType

router = APIRouter(prefix="/api/v1/projects", tags=["projects"])


@router.get("", response_model=List[ProjectOut])
def list_projects(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    q = db.query(Project)
    if current_user.role == UserRole.MEMBER.value:
        q = q.filter(Project.owner_id == current_user.id)
    return q.order_by(Project.created_at.desc()).all()


@router.post("", response_model=ProjectOut)
def create_project(project_in: ProjectCreate, db: Session = Depends(get_db),
                   current_user: User = Depends(require_role(UserRole.ADMIN.value, UserRole.MANAGER.value))):
    project = Project(name=project_in.name, description=project_in.description, owner_id=current_user.id)
    db.add(project)
    db.commit()
    db.refresh(project)
    create_log(db, LogType.OPERATION, current_user.id, "project",
               f"Created project {project.name}")
    return project


@router.get("/{project_id}", response_model=ProjectOut)
def get_project(project_id: int, db: Session = Depends(get_db),
                current_user: User = Depends(get_current_user)):
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    if not can_view_project(current_user, project):
        raise HTTPException(status_code=403, detail="无权查看该项目")
    return project


@router.put("/{project_id}", response_model=ProjectOut)
def update_project(project_id: int, project_in: ProjectUpdate,
                   db: Session = Depends(get_db), current_user: User = Depends(require_role(UserRole.ADMIN.value, UserRole.MANAGER.value))):
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    if project_in.name is not None:
        project.name = project_in.name
    if project_in.description is not None:
        project.description = project_in.description
    db.commit()
    db.refresh(project)
    return project


@router.delete("/{project_id}")
def delete_project(project_id: int, db: Session = Depends(get_db),
                   current_user: User = Depends(require_role(UserRole.ADMIN.value, UserRole.MANAGER.value))):
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    db.delete(project)
    db.commit()
    return {"detail": "Project deleted"}

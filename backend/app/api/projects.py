from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.core.deps import get_current_user, require_role
from app.core.project_access import can_view_project
from app.models.user import UserRole
from app.models.user import User
from app.models.project import Project
from app.models.project_member import ProjectMember
from app.schemas.project import ProjectCreate, ProjectUpdate, ProjectOut, ProjectMemberOut, AddMemberBody
from app.services.log_service import create_log
from app.models.log import LogType

router = APIRouter(prefix="/api/v1/projects", tags=["projects"])


@router.get("", response_model=List[ProjectOut])
def list_projects(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    q = db.query(Project)
    if current_user.role == UserRole.MEMBER.value:
        q = q.outerjoin(ProjectMember, ProjectMember.project_id == Project.id).filter(
            (Project.owner_id == current_user.id) | (ProjectMember.user_id == current_user.id)
        ).distinct()
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
    if not can_view_project(db, current_user, project):
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


@router.get("/{project_id}/members", response_model=List[ProjectMemberOut])
def list_members(project_id: int, db: Session = Depends(get_db),
                 current_user: User = Depends(get_current_user)):
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    if not can_view_project(db, current_user, project):
        raise HTTPException(status_code=403, detail="无权查看该项目")
    rows = (
        db.query(ProjectMember)
        .filter(ProjectMember.project_id == project_id)
        .order_by(ProjectMember.created_at.asc())
        .all()
    )
    return [
        ProjectMemberOut(
            id=row.id,
            project_id=row.project_id,
            user_id=row.user_id,
            username=row.user.username,
            full_name=row.user.full_name,
            created_at=row.created_at,
        )
        for row in rows
    ]


@router.post("/{project_id}/members", response_model=ProjectMemberOut)
def add_member(project_id: int, body: AddMemberBody,
               db: Session = Depends(get_db),
               current_user: User = Depends(require_role(UserRole.ADMIN.value, UserRole.MANAGER.value))):
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    user = db.query(User).filter(User.id == body.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if user.role != UserRole.MEMBER.value:
        raise HTTPException(status_code=400, detail="只能添加 member 角色用户为项目成员")
    existing = db.query(ProjectMember).filter(
        ProjectMember.project_id == project_id,
        ProjectMember.user_id == body.user_id,
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="该用户已是项目成员")
    if project.owner_id == body.user_id:
        raise HTTPException(status_code=400, detail="项目所有者无需添加为成员")
    pm = ProjectMember(project_id=project_id, user_id=body.user_id)
    db.add(pm)
    db.commit()
    db.refresh(pm)
    create_log(db, LogType.OPERATION, current_user.id, "project",
               f"Added member {user.username} to project {project.name}")
    return ProjectMemberOut(
        id=pm.id, project_id=pm.project_id, user_id=pm.user_id,
        username=user.username, full_name=user.full_name,
        created_at=pm.created_at,
    )


@router.delete("/{project_id}/members/{user_id}")
def remove_member(project_id: int, user_id: int,
                  db: Session = Depends(get_db),
                  current_user: User = Depends(require_role(UserRole.ADMIN.value, UserRole.MANAGER.value))):
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    pm = db.query(ProjectMember).filter(
        ProjectMember.project_id == project_id,
        ProjectMember.user_id == user_id,
    ).first()
    if not pm:
        raise HTTPException(status_code=404, detail="该用户不是项目成员")
    db.delete(pm)
    db.commit()
    create_log(db, LogType.OPERATION, current_user.id, "project",
               f"Removed member (user_id={user_id}) from project {project.name}")
    return {"detail": "Member removed"}

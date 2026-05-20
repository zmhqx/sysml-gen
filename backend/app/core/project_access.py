"""项目与模型访问控制：管理员/经理可访问全部；成员可访问自己创建或被添加为成员的项目。"""
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.user import User, UserRole
from app.models.project import Project
from app.models.project_member import ProjectMember
from app.models.model import SysModel


def get_project(db: Session, project_id: int) -> Project | None:
    return db.query(Project).filter(Project.id == project_id).first()


def _is_project_member(db: Session, user: User, project_id: int) -> bool:
    return db.query(ProjectMember).filter(
        ProjectMember.project_id == project_id,
        ProjectMember.user_id == user.id,
    ).first() is not None


def can_write_project(user: User, project: Project) -> bool:
    if user.role in (UserRole.ADMIN.value, UserRole.MANAGER.value):
        return True
    return project.owner_id == user.id


def can_view_project(db: Session, user: User, project: Project) -> bool:
    """读权限：管理员/经理可看全部；成员可看自己拥有或被授权的项目。"""
    if user.role in (UserRole.ADMIN.value, UserRole.MANAGER.value):
        return True
    return project.owner_id == user.id or _is_project_member(db, user, project.id)


def can_read_project(db: Session, user: User, project: Project) -> bool:
    """与 can_view_project 一致（供文档/模型读接口使用）。"""
    return can_view_project(db, user, project)


def require_project_write(db: Session, user: User, project_id: int) -> Project:
    project = get_project(db, project_id)
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
    if not can_write_project(user, project):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权在该项目下执行此操作",
        )
    return project


def require_project_read(db: Session, user: User, project_id: int) -> Project:
    project = get_project(db, project_id)
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
    if not can_read_project(db, user, project):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权查看该项目",
        )
    return project


def require_model_access(db: Session, user: User, model: SysModel, *, write: bool) -> None:
    project = get_project(db, model.project_id)
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
    if write:
        if not can_write_project(user, project):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="无权修改该模型")
    else:
        if not can_read_project(db, user, project):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="无权查看该模型")

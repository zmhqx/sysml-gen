from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session
from typing import List, Optional

from app.database import get_db
from app.core.deps import get_current_user, require_role
from app.models.user import User, UserRole
from app.core.security import get_password_hash
from app.schemas.user import UserOut, UserUpdate, AdminUserCreate
from app.services.log_service import get_logs
from app.schemas.log import LogOut
from app.models.project import Project
from app.models.model import SysModel
from app.models.document import Document
from app.models.template import Template

router = APIRouter(prefix="/api/v1/admin", tags=["admin"])


@router.get("/users", response_model=List[UserOut])
def list_users(db: Session = Depends(get_db),
               current_user: User = Depends(get_current_user)):
    return db.query(User).all()


@router.post("/users", response_model=UserOut)
def create_user(user_in: AdminUserCreate,
                db: Session = Depends(get_db),
                current_user: User = Depends(require_role(UserRole.ADMIN.value))):
    if user_in.role not in ("admin", "manager", "member"):
        raise HTTPException(status_code=400, detail="无效角色")
    existing = db.query(User).filter(User.username == user_in.username).first()
    if existing:
        raise HTTPException(status_code=400, detail="用户名已存在")
    user = User(
        username=user_in.username,
        password_hash=get_password_hash(user_in.password),
        full_name=user_in.full_name or "",
        email=user_in.email or "",
        role=user_in.role,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@router.put("/users/{user_id}", response_model=UserOut)
def update_user(user_id: int, user_in: UserUpdate,
                db: Session = Depends(get_db),
                current_user: User = Depends(require_role(UserRole.ADMIN.value))):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if user_in.full_name is not None:
        user.full_name = user_in.full_name
    if user_in.email is not None:
        user.email = user_in.email
    if user_in.role is not None:
        user.role = user_in.role
    if user_in.status is not None:
        user.status = user_in.status
    db.commit()
    db.refresh(user)
    return user


@router.delete("/users/{user_id}")
def delete_user(user_id: int, db: Session = Depends(get_db),
                current_user: User = Depends(require_role(UserRole.ADMIN.value))):
    if user_id == current_user.id:
        raise HTTPException(status_code=400, detail="Cannot delete yourself")
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user.status = 0
    db.commit()
    return {"detail": "User disabled"}


class LogListResponse(BaseModel):
    items: List[LogOut]
    total: int
    page: int
    page_size: int


@router.get("/logs", response_model=LogListResponse)
def list_logs(
    log_type: Optional[str] = Query(None),
    module_name: Optional[str] = Query(None),
    result_status: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.ADMIN.value)),
):
    rows, total = get_logs(db, log_type, module_name, result_status, page, page_size)
    items = [LogOut.model_validate(row) for row in rows]
    return LogListResponse(items=items, total=total, page=page, page_size=page_size)


@router.get("/stats")
def get_stats(db: Session = Depends(get_db),
              current_user: User = Depends(get_current_user)):
    return {
        "user_count": db.query(User).count(),
        "project_count": db.query(Project).count(),
        "model_count": db.query(SysModel).count(),
        "template_count": db.query(Template).count(),
        "document_count": db.query(Document).count(),
    }

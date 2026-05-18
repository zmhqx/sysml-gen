from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from app.database import get_db
from app.core.deps import get_current_user, require_role
from app.models.user import User, UserRole
from app.schemas.user import UserOut, UserUpdate
from app.services.log_service import get_logs
from app.schemas.log import LogOut
from app.models.project import Project
from app.models.model import SysModel
from app.models.document import Document

router = APIRouter(prefix="/api/v1/admin", tags=["admin"])


@router.get("/users", response_model=List[UserOut])
def list_users(db: Session = Depends(get_db),
               current_user: User = Depends(require_role(UserRole.ADMIN.value))):
    return db.query(User).all()


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


@router.get("/logs", response_model=dict)
def list_logs(
    log_type: Optional[str] = Query(None),
    module_name: Optional[str] = Query(None),
    result_status: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.ADMIN.value)),
):
    items, total = get_logs(db, log_type, module_name, result_status, page, page_size)
    return {"items": items, "total": total, "page": page, "page_size": page_size}


@router.get("/stats")
def get_stats(db: Session = Depends(get_db),
              current_user: User = Depends(get_current_user)):
    return {
        "user_count": db.query(User).count(),
        "project_count": db.query(Project).count(),
        "model_count": db.query(SysModel).count(),
        "document_count": db.query(Document).count(),
    }

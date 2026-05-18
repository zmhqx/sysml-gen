from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.database import get_db
from app.core.security import (
    get_password_hash,
    verify_password,
    create_access_token,
    create_refresh_token,
    decode_refresh_token,
)
from app.core.deps import get_current_user
from app.models.user import User, UserRole
from app.schemas.user import UserCreate, Token, UserOut, RefreshTokenBody
from app.services.log_service import create_log
from app.models.log import LogType, ResultStatus

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])


@router.post("/register", response_model=UserOut)
def register(user_in: UserCreate, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.username == user_in.username).first()
    if existing:
        raise HTTPException(status_code=400, detail="Username already exists")
    user = User(
        username=user_in.username,
        password_hash=get_password_hash(user_in.password),
        full_name=user_in.full_name or "",
        email=user_in.email or "",
        role=UserRole.MEMBER.value,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def _login_with_credentials(username: str, password: str, db: Session) -> Token:
    """校验用户名密码并签发令牌。"""
    user = db.query(User).filter(User.username == username).first()
    if not user or not verify_password(password, user.password_hash):
        create_log(
            db,
            LogType.LOGIN,
            module_name="auth",
            operation_content=f"Login failed: {username}",
            result_status=ResultStatus.FAILED,
        )
        raise HTTPException(status_code=401, detail="Incorrect username or password")
    if user.status == 0:
        raise HTTPException(status_code=401, detail="User is disabled")
    token = create_access_token(data={"sub": str(user.id)})
    refresh = create_refresh_token(str(user.id))
    create_log(
        db,
        LogType.LOGIN,
        operator_id=user.id,
        module_name="auth",
        operation_content=f"User {user.username} logged in",
    )
    return Token(access_token=token, refresh_token=refresh)


@router.post("/login", response_model=Token)
async def login(request: Request, db: Session = Depends(get_db)):
    """
    登录：JSON（Try it out）或表单（Authorize 弹窗，含 grant_type=password）。
    勿在参数里使用 UserLogin，否则 Authorize 发表单会 422。
    """
    content_type = (request.headers.get("content-type") or "").lower()
    if "application/json" in content_type:
        body = await request.json()
        username = body.get("username")
        password = body.get("password")
    else:
        form = await request.form()
        username = form.get("username")
        password = form.get("password")
    if not username or not password:
        raise HTTPException(status_code=422, detail="username and password are required")
    return _login_with_credentials(str(username), str(password), db)


@router.post("/token", response_model=Token)
def login_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    """OAuth2 标准表单登录（与 /login 表单等价）。"""
    return _login_with_credentials(form_data.username, form_data.password, db)


@router.post("/refresh", response_model=Token)
def refresh_tokens(body: RefreshTokenBody, db: Session = Depends(get_db)):
    payload = decode_refresh_token(body.refresh_token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid or expired refresh token")
    try:
        user_id = int(payload.get("sub"))
    except (TypeError, ValueError):
        raise HTTPException(status_code=401, detail="Invalid refresh token payload")
    user = db.query(User).filter(User.id == user_id).first()
    if user is None or user.status == 0:
        raise HTTPException(status_code=401, detail="User not found or disabled")
    return Token(
        access_token=create_access_token(data={"sub": str(user.id)}),
        refresh_token=create_refresh_token(str(user.id)),
    )


@router.get("/me", response_model=UserOut)
def get_me(current_user: User = Depends(get_current_user)):
    return current_user

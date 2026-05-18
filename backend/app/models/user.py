from sqlalchemy import Column, Integer, String, DateTime, func
from app.database import Base
import enum


class UserRole(str, enum.Enum):
    ADMIN = "admin"
    MANAGER = "manager"
    MEMBER = "member"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    full_name = Column(String(100), default="")
    email = Column(String(100), default="")
    role = Column(String(20), default=UserRole.MEMBER.value)
    status = Column(Integer, default=1)  # 1=active, 0=disabled
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

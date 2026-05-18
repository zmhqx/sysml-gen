from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship
from app.database import Base
import enum


class TemplateStatus(str, enum.Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"


class Template(Base):
    __tablename__ = "templates"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(128), nullable=False)
    template_type = Column(String(50), nullable=False)
    content = Column(Text, default="")
    file_path = Column(String(255), default="")
    status = Column(String(20), default=TemplateStatus.ACTIVE.value)
    creator_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    creator = relationship("User", backref="templates")

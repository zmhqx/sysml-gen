from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, func, JSON, Index
from sqlalchemy.orm import relationship
from app.database import Base
import enum


class ParseStatus(str, enum.Enum):
    PENDING = "pending"
    PARSING = "parsing"
    SUCCESS = "success"
    FAILED = "failed"


class SysModel(Base):
    __tablename__ = "models"

    id = Column(Integer, primary_key=True, autoincrement=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False, index=True)
    name = Column(String(128), nullable=False)
    version_tag = Column(String(32), default="v1.0")
    file_path = Column(String(255), nullable=False)
    file_size = Column(Integer, default=0)
    file_type = Column(String(32), default="")
    uploader_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    upload_time = Column(DateTime, server_default=func.now())
    parse_status = Column(String(20), default=ParseStatus.PENDING.value)
    parse_message = Column(Text, default="")
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    project = relationship("Project", backref="models")
    uploader = relationship("User", backref="uploaded_models")


class ModelElement(Base):
    __tablename__ = "model_elements"

    id = Column(Integer, primary_key=True, autoincrement=True)
    model_id = Column(Integer, ForeignKey("models.id"), nullable=False, index=True)
    element_id = Column(String(100), nullable=False)
    element_name = Column(String(255), default="")
    element_type = Column(String(50), nullable=False)
    parent_element_id = Column(String(100), default="")
    description = Column(Text, default="")
    attributes = Column(JSON, default=dict)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    model = relationship("SysModel", backref="elements")

    __table_args__ = (
        Index("uk_model_element", "model_id", "element_id", unique=True),
    )


class ModelRelationship(Base):
    __tablename__ = "model_relationships"

    id = Column(Integer, primary_key=True, autoincrement=True)
    model_id = Column(Integer, ForeignKey("models.id"), nullable=False, index=True)
    source_element_id = Column(String(100), nullable=False)
    target_element_id = Column(String(100), nullable=False)
    relationship_type = Column(String(50), default="")
    relationship_name = Column(String(255), default="")
    description = Column(Text, default="")
    created_at = Column(DateTime, server_default=func.now())

    model = relationship("SysModel", backref="relationships")

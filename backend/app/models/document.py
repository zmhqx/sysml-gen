from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship
from app.database import Base
import enum


class DocumentStatus(str, enum.Enum):
    GENERATING = "generating"
    SUCCESS = "success"
    FAILED = "failed"


class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, autoincrement=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    model_id = Column(Integer, ForeignKey("models.id"), nullable=False)
    template_id = Column(Integer, ForeignKey("templates.id"), nullable=False)
    document_name = Column(String(255), nullable=False)
    content = Column(Text, default="")
    file_path = Column(String(255), default="")
    export_format = Column(String(20), default="docx")
    status = Column(String(20), default=DocumentStatus.GENERATING.value)
    generate_message = Column(Text, default="")
    operator_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    generate_time = Column(DateTime, server_default=func.now())
    created_at = Column(DateTime, server_default=func.now())

    project = relationship("Project", backref="documents")
    model = relationship("SysModel", backref="documents")
    template = relationship("Template", backref="documents")
    operator = relationship("User", backref="generated_documents")

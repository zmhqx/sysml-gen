from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship
from app.database import Base
import enum


class LogType(str, enum.Enum):
    LOGIN = "login"
    OPERATION = "operation"
    ERROR = "error"
    SYSTEM = "system"


class ResultStatus(str, enum.Enum):
    SUCCESS = "success"
    FAILED = "failed"
    WARNING = "warning"


class Log(Base):
    __tablename__ = "logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    log_type = Column(String(20), nullable=False)
    operator_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    module_name = Column(String(64), default="")
    operation_content = Column(Text, default="")
    result_status = Column(String(20), default=ResultStatus.SUCCESS.value)
    ip_address = Column(String(45), default="")
    record_time = Column(DateTime, server_default=func.now())

    operator = relationship("User", backref="logs")

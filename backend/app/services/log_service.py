from sqlalchemy.orm import Session
from app.models.log import Log, LogType, ResultStatus
from typing import Optional


def create_log(
    db: Session,
    log_type: LogType,
    operator_id: Optional[int] = None,
    module_name: str = "",
    operation_content: str = "",
    result_status: ResultStatus = ResultStatus.SUCCESS,
    ip_address: str = "",
) -> Log:
    log = Log(
        log_type=log_type.value,
        operator_id=operator_id,
        module_name=module_name,
        operation_content=operation_content,
        result_status=result_status.value,
        ip_address=ip_address,
    )
    db.add(log)
    db.commit()
    return log


def get_logs(
    db: Session,
    log_type: Optional[str] = None,
    module_name: Optional[str] = None,
    result_status: Optional[str] = None,
    page: int = 1,
    page_size: int = 20,
):
    query = db.query(Log)
    if log_type:
        query = query.filter(Log.log_type == log_type)
    if module_name:
        query = query.filter(Log.module_name == module_name)
    if result_status:
        query = query.filter(Log.result_status == result_status)
    total = query.count()
    items = query.order_by(Log.record_time.desc()).offset((page - 1) * page_size).limit(page_size).all()
    return items, total

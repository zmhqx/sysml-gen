class AuthError(Exception):
    """认证失败（用户名/密码错误或 token 过期）。"""
    pass


class ApiError(Exception):
    """API 调用返回错误响应。"""

    def __init__(self, status_code: int, detail: str):
        self.status_code = status_code
        self.detail = detail
        super().__init__(f"[{status_code}] {detail}")


class NotFoundError(ApiError):
    """请求的资源不存在。"""
    pass


class ConnectionError_(Exception):
    """无法连接到服务端。"""
    pass

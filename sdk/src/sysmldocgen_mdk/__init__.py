"""sysmldocgen-mdk — 基于SysML模型的文档自动生成系统 Jupyter MDK 开发工具包。

提供完整的 Jupyter 集成，包括:
- Client: 基础 API 封装
- SyncSession: 模型双向同步引擎
- DocGenTemplate: DocGen 文档生成语言工具
- IPython 魔法命令: %connect, %load_model, %pull, %sync_push, %render_doc
"""

__version__ = "0.2.0"

from .client import Client
from .exceptions import AuthError, ApiError, NotFoundError, ConnectionError_
from .sync import SyncSession, SyncSnapshot, SyncDiff, PushResult
from .docgen import DocGenTemplate

# 自动注册 IPython 魔法命令（如果在 Jupyter/IPython 环境中）
try:
    from .jupyter import register_magics
    register_magics()
except Exception:
    pass

__all__ = [
    "Client",
    "SyncSession",
    "SyncSnapshot",
    "SyncDiff",
    "PushResult",
    "DocGenTemplate",
    "AuthError",
    "ApiError",
    "NotFoundError",
    "ConnectionError_",
]

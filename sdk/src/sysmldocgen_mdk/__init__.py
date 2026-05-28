"""sysmldocgen-mdk — 基于SysML模型的文档自动生成系统 Jupyter MDK 开发工具包。

提供完整的 Jupyter 集成，包括:
- Client: 基础 API 封装
- SyncSession: 模型双向同步引擎
- DocGenTemplate: DocGen 文档生成语言工具
- IPython 魔法命令: %connect, %load_model, %pull, %sync_push, %render_doc

在 Jupyter 中加载魔法命令:
    %load_ext sysmldocgen_mdk
    或
    from sysmldocgen_mdk import register_magics
    register_magics()
"""

__version__ = "0.2.0"

from .client import Client
from .exceptions import AuthError, ApiError, NotFoundError, ConnectionError_
from .sync import SyncSession, SyncSnapshot, SyncDiff, PushResult
from .docgen import DocGenTemplate


def register_magics():
    """注册 IPython 魔法命令（在 Jupyter 中手动调用）。"""
    from .jupyter import register_magics as _rm
    _rm()


def load_ipython_extension(ipython):
    """IPython 扩展入口 — 支持 %load_ext sysmldocgen_mdk。"""
    from .jupyter import SysMLDocGenMagics
    ipython.register_magics(SysMLDocGenMagics)


__all__ = [
    "Client",
    "SyncSession",
    "SyncSnapshot",
    "SyncDiff",
    "PushResult",
    "DocGenTemplate",
    "register_magics",
    "AuthError",
    "ApiError",
    "NotFoundError",
    "ConnectionError_",
]

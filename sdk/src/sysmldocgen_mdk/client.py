"""sysmldocgen MDK — 核心客户端，封装全部 REST API 调用。"""

from __future__ import annotations

import requests as _requests
import pandas as pd
from typing import Optional

from .exceptions import AuthError, ApiError, NotFoundError, ConnectionError_


class Client:
    """SysMLDocGen API 客户端。

    用法:
        from sysmldocgen_mdk import Client
        client = Client("http://localhost:8000", "admin", "admin123")
        client.list_projects()
    """

    def __init__(self, base_url: str = "http://localhost:8000",
                 username: str = "", password: str = ""):
        self.base_url = base_url.rstrip("/")
        self._session = _requests.Session()
        self._session.headers.update({"Content-Type": "application/json"})
        if username and password:
            self.login(username, password)

    # ── 认证 ─────────────────────────────────────────────

    def login(self, username: str, password: str) -> "Client":
        """登录并保存 token，后续请求自动带认证头。"""
        try:
            resp = self._session.post(
                f"{self.base_url}/api/v1/auth/login",
                json={"username": username, "password": password},
            )
        except _requests.ConnectionError:
            raise ConnectionError_(f"无法连接到 {self.base_url}")
        if resp.status_code != 200:
            raise AuthError(resp.json().get("detail", "登录失败"))
        token = resp.json()["access_token"]
        self._session.headers.update({"Authorization": f"Bearer {token}"})
        return self

    # ── 内部辅助 ───────────────────────────────────────

    def _request(self, method: str, path: str, **kwargs):
        url = f"{self.base_url}/api/v1{path}"
        try:
            resp = self._session.request(method, url, **kwargs)
        except _requests.ConnectionError:
            raise ConnectionError_(f"无法连接到 {self.base_url}")
        if resp.status_code == 401:
            raise AuthError(resp.json().get("detail", "认证失败"))
        if resp.status_code == 404:
            detail = resp.json().get("detail", "资源不存在")
            raise NotFoundError(resp.status_code, detail)
        if not resp.ok:
            detail = resp.json().get("detail", "请求失败")
            raise ApiError(resp.status_code, detail)
        return resp.json()

    def _get(self, path: str, **kwargs):
        return self._request("GET", path, **kwargs)

    def _post(self, path: str, **kwargs):
        return self._request("POST", path, **kwargs)

    def _put(self, path: str, **kwargs):
        return self._request("PUT", path, **kwargs)

    def _delete(self, path: str, **kwargs):
        return self._request("DELETE", path, **kwargs)

    # ── 项目 ──────────────────────────────────────────

    def list_projects(self) -> list[dict]:
        """获取当前用户可见的项目列表。"""
        return self._get("/projects")

    def get_project(self, project_id: int) -> dict:
        """获取单个项目详情。"""
        return self._get(f"/projects/{project_id}")

    def create_project(self, name: str, description: str = "") -> dict:
        """创建项目（需 admin/manager 权限）。"""
        return self._post("/projects", json={"name": name, "description": description})

    def get_members(self, project_id: int) -> list[dict]:
        """获取项目成员列表。"""
        return self._get(f"/projects/{project_id}/members")

    # ── 模型 ──────────────────────────────────────────

    def list_models(self, project_id: Optional[int] = None) -> list[dict]:
        """获取模型列表，可按项目筛选。"""
        params = {}
        if project_id is not None:
            params["project_id"] = project_id
        return self._get("/models", params=params)

    def get_model(self, model_id: int) -> dict:
        """获取单个模型详情。"""
        return self._get(f"/models/{model_id}")

    # ── 模型元素 ───────────────────────────────────────

    def get_elements(self, model_id: int) -> pd.DataFrame:
        """获取模型全部元素，返回 pandas DataFrame。

        返回的 DataFrame 包含列：element_id, element_name, element_type, description 等。
        """
        data = self._get(f"/models/{model_id}/elements")
        return pd.DataFrame(data)

    def get_element(self, model_id: int, element_id: str) -> dict:
        """获取单个元素详情。"""
        return self._get(f"/models/{model_id}/elements/{element_id}")

    def update_element(self, model_id: int, element_id: str,
                       **kwargs) -> dict:
        """更新元素的字段（如名称、描述）。

        用法:
            client.update_element(2, "req_1", element_name="新名称")
            client.update_element(2, "req_1", description="新描述")
        """
        return self._put(f"/models/{model_id}/elements/{element_id}", json=kwargs)

    def search_elements(self, model_id: int, q: str) -> list[dict]:
        """搜索元素（按名称/描述模糊匹配）。"""
        return self._get(f"/models/{model_id}/elements/search", params={"q": q})

    def get_relationships(self, model_id: int) -> list[dict]:
        """获取模型全部关系（元素间连线）。"""
        return self._get(f"/models/{model_id}/relationships")

    def get_element_tree(self, model_id: int) -> list[dict]:
        """获取元素树形结构（按 parent 关系组织）。"""
        return self._get(f"/models/{model_id}/elements/tree")

    # ── 模板 ──────────────────────────────────────────

    def list_templates(self) -> list[dict]:
        """获取模板列表。"""
        return self._get("/templates")

    def get_template(self, template_id: int) -> dict:
        """获取单个模板详情（含 content）。"""
        return self._get(f"/templates/{template_id}")

    def create_template(self, name: str, template_type: str,
                        content: str = "") -> dict:
        """创建新模板。"""
        return self._post("/templates", json={
            "name": name,
            "template_type": template_type,
            "content": content,
        })

    def update_template(self, template_id: int, **kwargs) -> dict:
        """更新模板字段（name, template_type, content, status）。"""
        return self._put(f"/templates/{template_id}", json=kwargs)

    def delete_template(self, template_id: int) -> dict:
        """删除模板。"""
        return self._delete(f"/templates/{template_id}")

    # ── 文档 ──────────────────────────────────────────

    def generate_document(self, project_id: int, model_id: int,
                          template_id: int) -> dict:
        """生成文档。"""
        return self._post("/documents/generate", json={
            "project_id": project_id,
            "model_id": model_id,
            "template_id": template_id,
        })

    def list_documents(self, project_id: Optional[int] = None,
                       page: int = 1, page_size: int = 20) -> dict:
        """获取文档列表。

        返回 {"items": [...], "total": N, "page": P, "page_size": S}。
        """
        params = {"page": page, "page_size": page_size}
        if project_id is not None:
            params["project_id"] = project_id
        return self._get("/documents", params=params)

    # ── 管理 ──────────────────────────────────────────

    def list_users(self) -> list[dict]:
        """获取所有用户列表。"""
        return self._get("/admin/users")

    def get_stats(self) -> dict:
        """获取系统统计信息（用户/项目/模型/模板/文档数量）。"""
        return self._get("/admin/stats")

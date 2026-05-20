"""SysMLDocGen MDK — DocGen 文档生成语言工具。

在 Jupyter 端提供完整的 DocGen 模板创作、渲染、推送工具链。

用法:
    from sysmldocgen_mdk import DocGenTemplate

    tpl = DocGenTemplate(content, name="需求规格")
    html = tpl.render(elements_df, relationships_df, model_info)
    display(HTML(html))

    # 推送到服务端
    tpl.to_server(client)
"""

from __future__ import annotations

import json
from datetime import datetime
from typing import Any, Optional

import pandas as pd
from jinja2 import Environment, BaseLoader
from jinja2.sandbox import SandboxedEnvironment
from markupsafe import Markup

from .client import Client


# ── Jinja2 过滤器 ─────────────────────────────────────


def _ensure_list(value):
    """确保返回列表。"""
    if isinstance(value, pd.DataFrame):
        return value.to_dict("records")
    if isinstance(value, list):
        return value
    if hasattr(value, "__iter__"):
        return list(value)
    return [value]


def _req_table(elements, title: str = "需求列表") -> str:
    """将元素列表渲染为需求表格（HTML）。"""
    rows = _ensure_list(elements)
    if not rows:
        return f"<p><em>{title}：无</em></p>"
    lines = [f"<h3>{title}</h3>", '<table border="1" cellpadding="6" style="border-collapse:collapse;width:100%">']
    lines.append("<tr><th>编号</th><th>名称</th><th>描述</th></tr>")
    for r in rows:
        eid = r.get("element_id", r.get("id", ""))
        name = r.get("element_name", r.get("name", ""))
        desc = r.get("description", "")
        lines.append(f"<tr><td>{eid}</td><td>{name}</td><td>{desc}</td></tr>")
    lines.append("</table>")
    return Markup("\n".join(lines))


def _block_hierarchy(elements) -> str:
    """按 parent_element_id 渲染 Block 层级树（HTML）。"""
    rows = _ensure_list(elements)
    blocks = [r for r in rows if r.get("element_type") == "Block"
              or r.get("type") == "Block"]
    if not blocks:
        return "<p><em>无 Block 元素</em></p>"

    # 构建树
    children_of: dict[str, list] = {}
    block_map: dict[str, dict] = {}
    for b in blocks:
        eid = b.get("element_id", b.get("id", ""))
        block_map[eid] = b
        parent = b.get("parent_element_id", "")
        if parent not in children_of:
            children_of[parent] = []
        children_of[parent].append(b)

    def _render_tree(parent_id: str, level: int = 0) -> str:
        items = children_of.get(parent_id, [])
        if not items:
            return ""
        lines = []
        indent = "  " * level
        for item in items:
            eid = item.get("element_id", item.get("id", ""))
            name = item.get("element_name", item.get("name", ""))
            desc = item.get("description", "")
            lines.append(f'{indent}<li><strong>{name}</strong> ({eid})'
                         f'<br/><span style="color:#666">{desc}</span>')
            child_html = _render_tree(eid, level + 1)
            if child_html:
                lines.append(f"{indent}<ul>{child_html}{indent}</ul>")
            lines.append(f"{indent}</li>")
        return "\n".join(lines)

    tree = _render_tree("")
    return Markup(f"<ul style='list-style-type:none;padding-left:0'>{tree}</ul>")


def _iface_matrix(elements) -> str:
    """生成接口连接矩阵（HTML 表格）。"""
    rows = _ensure_list(elements)
    ifaces = [r for r in rows if r.get("element_type") == "Interface"
              or r.get("type") == "Interface"]
    if not ifaces:
        return "<p><em>无接口元素</em></p>"

    lines = [
        "<h3>接口矩阵</h3>",
        '<table border="1" cellpadding="6" style="border-collapse:collapse;width:100%">',
        "<tr><th>接口名称</th><th>编号</th><th>描述</th></tr>",
    ]
    for iface in ifaces:
        name = iface.get("element_name", iface.get("name", ""))
        eid = iface.get("element_id", iface.get("id", ""))
        desc = iface.get("description", "")
        lines.append(f"<tr><td>{name}</td><td>{eid}</td><td>{desc}</td></tr>")
    lines.append("</table>")
    return Markup("\n".join(lines))


def _element_link(element_id: str, text: Optional[str] = None) -> str:
    """生成指向模型元素的交叉引用链接（HTML 锚点）。"""
    label = text or element_id
    return Markup(f'<a href="#{element_id}" class="element-ref">{label}</a>')


def _format_attrs(attributes) -> str:
    """格式化 attributes JSON 为可读 HTML。"""
    if not attributes:
        return "<span style='color:#999'>无</span>"
    if isinstance(attributes, str):
        try:
            attributes = json.loads(attributes)
        except json.JSONDecodeError:
            return attributes
    if not isinstance(attributes, dict):
        return str(attributes)
    items = "".join(
        f"<li><strong>{k}</strong>: {v}</li>"
        for k, v in attributes.items()
    )
    return Markup(f"<ul style='margin:0;padding-left:16px'>{items}</ul>")


# ── DocGen 模板类 ────────────────────────────────────


class DocGenTemplate:
    """DocGen 模板对象。

    封装 Jinja2 渲染引擎 + SysML 专用过滤器，支持本地预览和推送到服务端。

    用法:
        tpl = DocGenTemplate(content, name="需求规格")
        html = tpl.render(elements_df, relationships_df, model_info)
    """

    def __init__(self, content: str, name: str = "untitled"):
        self.content = content
        self.name = name
        self._env = self._build_env()

    def _build_env(self) -> SandboxedEnvironment:
        """构建 Jinja2 沙箱环境，注册 SysML 专用过滤器。"""
        env = SandboxedEnvironment(autoescape=True)
        env.filters["req_table"] = _req_table
        env.filters["block_hierarchy"] = _block_hierarchy
        env.filters["iface_matrix"] = _iface_matrix
        env.filters["element_link"] = _element_link
        env.filters["format_attrs"] = _format_attrs
        return env

    def render(self,
               elements: pd.DataFrame,
               relationships: Optional[pd.DataFrame] = None,
               model_info: Optional[dict] = None) -> str:
        """渲染模板，返回 HTML 字符串。

        参数:
            elements: get_elements() 返回的元素 DataFrame
            relationships: get_relationships() 返回的关系 DataFrame
            model_info: get_model() 返回的模型信息 dict
        """
        model_info = model_info or {}
        rels = relationships if relationships is not None else pd.DataFrame()

        context = {
            "model_name": model_info.get("name", "未命名模型"),
            "model_version": model_info.get("version_tag", ""),
            "model_description": model_info.get("description", ""),
            "generate_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "elements": elements.to_dict("records") if not elements.empty else [],
            "relationships": rels.to_dict("records") if not rels.empty else [],
            "element_count": len(elements),
            "relationship_count": len(rels),
        }

        # 添加类型筛选快捷方式
        if not elements.empty:
            for type_name in elements["element_type"].unique():
                type_rows = elements[elements["element_type"] == type_name]
                context[f"{type_name.lower()}_list"] = type_rows.to_dict("records")

        tpl = self._env.from_string(self.content)
        return tpl.render(**context)

    def preview(self, elements: pd.DataFrame,
                relationships: Optional[pd.DataFrame] = None,
                model_info: Optional[dict] = None) -> str:
        """渲染模板并返回，是 render() 的别名。"""
        return self.render(elements, relationships, model_info)

    def to_server(self, client: Client,
                  template_type: str = "docgen",
                  name: Optional[str] = None) -> dict:
        """将模板推送到服务端保存。

        参数:
            client: 已认证的 Client 实例
            template_type: 模板类型（默认 docgen）
            name: 模板名称（默认 self.name）
        """
        tpl_name = name or self.name
        return client.create_template(
            name=tpl_name,
            template_type=template_type,
            content=self.content,
        )

    def to_server_update(self, client: Client,
                         template_id: int) -> dict:
        """更新服务端已存在的模板内容。"""
        return client.update_template(
            template_id=template_id,
            content=self.content,
        )

    @classmethod
    def from_server(cls, client: Client,
                    template_id: int) -> "DocGenTemplate":
        """从服务端拉取模板创建本地 DocGenTemplate 实例。"""
        data = client.get_template(template_id)
        return cls(content=data.get("content", ""),
                   name=data.get("name", "untitled"))

    def __repr__(self) -> str:
        preview = self.content[:60].replace("\n", " ")
        return f"<DocGenTemplate '{self.name}': {preview}...>"

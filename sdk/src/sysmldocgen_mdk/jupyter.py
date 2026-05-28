"""SysMLDocGen MDK — Jupyter 集成增强。

提供 IPython 魔法命令和 Widget 交互，使模型同步和文档生成在 Jupyter 中
像本地工具一样流畅操作。

用法:
    %load_model 2          # 拉取模型 2 数据到本地变量
    %sync_diff             # 显示本地与服务端差异
    %sync_push             # 推送本地变更到服务端
    %%render_doc           # 在单元格中编写模板并预览
"""

from __future__ import annotations

import json
from typing import Optional

import matplotlib.pyplot as plt
import pandas as pd
from IPython import get_ipython
from IPython.core.magic import Magics, magics_class, line_magic, cell_magic
from IPython.display import display, HTML, Markdown

from .client import Client
from .docgen import DocGenTemplate
from .sync import SyncSession


# ── 基础显示函数 ────────────────────────────────────


def display_md(text: str):
    """在 Jupyter 中渲染 Markdown。"""
    display(Markdown(text))


def display_table(df: pd.DataFrame, max_rows: int = 20):
    """显示元素表格（限制行数避免卡顿）。

    参数:
        df: 元素 DataFrame
        max_rows: 最多显示行数（默认 20）
    """
    cols = [c for c in ["element_id", "element_name", "element_type", "description"]
            if c in df.columns]
    view = df[cols]
    if len(view) > max_rows:
        display_md(f"*共 {len(view)} 行，仅显示前 {max_rows} 行*")
        display(view.head(max_rows))
    else:
        display(view)


def display_stats(elements_df: pd.DataFrame):
    """统计模型元素类型分布并以图表展示。

    参数:
        elements_df: get_elements() 返回的 DataFrame
    """
    counts = elements_df["element_type"].value_counts()
    total = len(elements_df)

    display_md(f"### 元素统计 — 共 {total} 个元素\n")
    display(counts.to_frame("数量"))

    fig, ax = plt.subplots(figsize=(8, 4))
    counts.plot(kind="bar", ax=ax, title="元素类型分布")
    ax.set_xlabel("元素类型")
    ax.set_ylabel("数量")
    plt.tight_layout()
    plt.show()


def display_sync_diff(diff) -> None:
    """在 Jupyter 中美化显示同步差异。"""
    summary = diff.summary
    parts = [f"### 同步差异对比\n"]
    parts.append(f"- **服务端独有的元素**: {summary['server_only']} 个")
    parts.append(f"- **本地新增的元素**: {summary['local_only']} 个")
    parts.append(f"- **冲突**: {summary['conflicts']} 处")

    display_md("\n".join(parts))

    if diff.conflicts:
        rows = []
        for c in diff.conflicts:
            rows.append({
                "元素 ID": c.element_id,
                "字段": c.field,
                "本地值": str(c.local_value)[:80],
                "服务端值": str(c.server_value)[:80],
            })
        display_md("**冲突明细：**")
        display(pd.DataFrame(rows))

    if diff.server_only:
        display_md("**服务端独有的元素：**")
        display(pd.DataFrame(diff.server_only))


def display_push_result(result) -> None:
    """显示推送结果。"""
    s = result.summary
    if result.success:
        display_md(f"✅ 同步完成：推送 {s['pushed']} 条，失败 {s['failed']} 条")
    else:
        display_md(f"❌ 同步失败：{len(result.conflicts)} 处冲突，请解决后重试")
    if result.errors:
        for err in result.errors[:5]:
            display_md(f"- ⚠️ {err}")


def display_sync_dashboard(session: SyncSession):
    """同步状态仪表盘。

    显示当前模型的同步状态、待推送变更、冲突数量。

    参数:
        session: SyncSession 实例
    """
    model_info = session.client.get_model(session.model_id)
    display_md(f"## 📊 同步仪表盘 — {model_info.get('name', '未命名')}")

    try:
        elements = session.client.get_elements(session.model_id)
        total = len(elements)
        types = elements["element_type"].value_counts().to_dict()
        type_summary = " | ".join(f"{k}: {v}" for k, v in types.items())
        display_md(f"**模型**: {model_info.get('name', '')} v{model_info.get('version_tag', '')}  \n"
                   f"**元素总数**: {total}  \n"
                   f"**类型分布**: {type_summary}")
    except Exception:
        display_md("⚠️ 无法连接到服务端获取模型数据")


# ── IPython 魔法命令 ─────────────────────────────────


@magics_class
class SysMLDocGenMagics(Magics):
    """SysMLDocGen 的 IPython 魔法命令。"""

    _client: Optional[Client] = None
    _sessions: dict[int, SyncSession] = {}

    def _get_client(self) -> Client:
        if self._client is None:
            raise ValueError(
                "未连接。请先运行 %connect <url> <username> <password>"
            )
        return self._client

    @line_magic
    def connect(self, line: str):
        """连接到 SysMLDocGen 服务端。

        用法:
            %connect http://localhost:8000 admin admin123
        """
        parts = line.strip().split()
        if len(parts) < 3:
            print("用法: %connect <url> <username> <password>")
            return
        url, username, password = parts[0], parts[1], parts[2]
        self._client = Client(url, username, password)
        display_md(f"✅ 已连接到 {url}（用户: {username}）")

    @line_magic
    def load_model(self, line: str):
        """拉取模型元素+关系到本地变量。

        用法:
            %load_model 2
        """
        parts = line.strip().split()
        if not parts:
            print("用法: %load_model <model_id>")
            return
        model_id = int(parts[0])
        client = self._get_client()

        model_info = client.get_model(model_id)
        elements = client.get_elements(model_id)
        rels = client.get_relationships(model_id)

        # 注入到用户命名空间
        self.shell.user_ns[f"model_{model_id}_info"] = model_info
        self.shell.user_ns[f"model_{model_id}_elements"] = elements
        self.shell.user_ns[f"model_{model_id}_relationships"] = pd.DataFrame(rels)

        # 创建同步会话
        session = SyncSession(client, model_id)
        self._sessions[model_id] = session
        self.shell.user_ns[f"session_{model_id}"] = session

        type_counts = elements["element_type"].value_counts().to_dict()
        summary = " | ".join(f"{k}: {v}" for k, v in type_counts.items())
        display_md(f"✅ 已加载模型 **{model_info.get('name')}** (id={model_id})  \n"
                   f"元素: {len(elements)} 个 | 关系: {len(rels)} 条  \n"
                   f"类型分布: {summary}  \n"
                   f"变量: `model_{model_id}_elements`, `model_{model_id}_relationships`, "
                   f"`session_{model_id}`")

    @line_magic
    def sync_diff(self, line: str):
        """显示本地快照与服务端的差异。

        用法:
            %sync_diff 2
        """
        parts = line.strip().split()
        if not parts:
            print("用法: %sync_diff <model_id>")
            return
        model_id = int(parts[0])
        session = self._sessions.get(model_id)
        if not session:
            print(f"模型 {model_id} 未加载。先运行 %load_model {model_id}")
            return
        snap_var = f"snapshot_{model_id}"
        snapshot = self.shell.user_ns.get(snap_var)
        if snapshot is None:
            print(f"未找到快照。先运行 %pull {model_id}")
            return
        diff = session.diff(snapshot)
        display_sync_diff(diff)

    @line_magic
    def pull(self, line: str):
        """拉取模型完整快照到本地（含变更跟踪能力）。

        用法:
            %pull 2
        """
        parts = line.strip().split()
        if not parts:
            print("用法: %pull <model_id>")
            return
        model_id = int(parts[0])
        session = self._sessions.get(model_id)
        if not session:
            client = self._get_client()
            session = SyncSession(client, model_id)
            self._sessions[model_id] = session

        snapshot = session.pull()
        var_name = f"snapshot_{model_id}"
        self.shell.user_ns[var_name] = snapshot
        self.shell.user_ns[f"session_{model_id}"] = session

        display_md(f"✅ 已拉取快照 `{var_name}`  \n"
                   f"元素: {len(snapshot.elements)} 个 | 关系: {len(snapshot.relationships)} 条  \n"
                   f"拉取时间: {snapshot.pulled_at.strftime('%H:%M:%S')}")

    @line_magic
    def sync_push(self, line: str):
        """将本地快照变更推回服务端。

        用法:
            %sync_push 2
            %sync_push 2 --skip-conflicts
        """
        parts = line.strip().split()
        if not parts:
            print("用法: %sync_push <model_id> [--skip-conflicts]")
            return
        model_id = int(parts[0])
        skip = "--skip-conflicts" in parts
        resolution = "skip" if skip else "keep_local"

        session = self._sessions.get(model_id)
        if not session:
            print(f"模型 {model_id} 未加载。先运行 %load_model {model_id}")
            return

        snap_var = f"snapshot_{model_id}"
        snapshot = self.shell.user_ns.get(snap_var)
        if snapshot is None:
            print(f"未找到快照。先运行 %pull {model_id}")
            return

        if not snapshot.local_changes:
            display_md("ℹ️ 没有待推送的本地变更")
            return

        display_md(f"🔄 正在推送 {len(snapshot.local_changes)} 条变更...")
        result = session.push(snapshot, conflict_resolution=resolution)
        display_push_result(result)

    @line_magic
    def list_models(self, line: str):
        """列出所有模型。

        用法:
            %list_models
            %list_models --project 1
        """
        client = self._get_client()
        parts = line.strip().split()
        project_id = None
        if "--project" in parts:
            idx = parts.index("--project")
            if idx + 1 < len(parts):
                project_id = int(parts[idx + 1])

        models = client.list_models(project_id=project_id)
        if not models:
            display_md("暂无模型")
            return
        rows = [{"ID": m["id"], "名称": m["name"],
                 "版本": m.get("version_tag", ""),
                 "项目ID": m.get("project_id", "")}
                for m in models]
        display(pd.DataFrame(rows))

    @line_magic
    def list_projects(self, line: str):
        """列出所有项目。

        用法:
            %list_projects
        """
        client = self._get_client()
        projects = client.list_projects()
        if not projects:
            display_md("暂无项目")
            return
        rows = [{"ID": p["id"], "名称": p["name"],
                 "描述": p.get("description", "")[:60]}
                for p in projects]
        display(pd.DataFrame(rows))

    @cell_magic
    def render_doc(self, line: str, cell: str):
        """在单元格中编写 DocGen 模板并预览渲染结果。

        用法:
            %%render_doc 模型名称
            # {{ model_name }} 文档
            {% for req in requirement_list %}
            - {{ req.element_name }}: {{ req.description }}
            {% endfor %}
        """
        client = self._get_client()

        # 查找最近的模型数据
        model_id = None
        for key, val in self.shell.user_ns.items():
            if key.startswith("model_") and key.endswith("_elements"):
                try:
                    mid = int(key.split("_")[1])
                    model_id = mid
                except (IndexError, ValueError):
                    continue

        if model_id is None:
            display_md("⚠️ 未找到模型数据。请先运行 `%load_model <id>`")
            return

        elements = self.shell.user_ns.get(f"model_{model_id}_elements",
                                          pd.DataFrame())
        rels = self.shell.user_ns.get(f"model_{model_id}_relationships",
                                      pd.DataFrame())
        model_info = self.shell.user_ns.get(f"model_{model_id}_info", {})

        tpl_name = line.strip() or "即时模板"
        tpl = DocGenTemplate(content=cell, name=tpl_name)

        try:
            html = tpl.render(elements, rels if not rels.empty else None, model_info)
            display_md("---")
            display_md(f"**预览: {tpl_name}**")
            display(HTML(html))
        except Exception as e:
            display_md(f"❌ 渲染失败: {e}")
            import traceback
            traceback.print_exc()


# ── 注册魔法命令 ─────────────────────────────────────


def register_magics():
    """注册 SysMLDocGen 魔法命令到当前 IPython 内核。"""
    ip = get_ipython()
    if ip is not None:
        ip.register_magics(SysMLDocGenMagics)


def load_ipython_extension(ip):
    """IPython 扩展入口 — 支持 %load_ext sysmldocgen_mdk 加载。"""
    ip.register_magics(SysMLDocGenMagics)

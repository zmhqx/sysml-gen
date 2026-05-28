"""SysMLDocGen MDK — 双向同步引擎。

在 Jupyter 本地维护模型副本，跟踪变更，推回服务端。

用法:
    from sysmldocgen_mdk import Client, SyncSession

    client = Client("http://localhost:8000", "admin", "admin123")
    session = SyncSession(client, model_id=2)

    # 拉取
    snapshot = session.pull()

    # 查看差异（如果 pull 后别人改过服务端）
    diff = session.diff(snapshot)

    # 在本地 DataFrame 上修改
    snapshot.elements.loc[0, "description"] = "新描述"

    # 推回
    result = session.push(snapshot)
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Optional

import pandas as pd

from .client import Client
from .exceptions import ApiError


# ── 数据类 ─────────────────────────────────────────────


@dataclass
class Change:
    """单次本地修改记录。"""
    change_id: str
    element_id: str
    field: str
    old_value: Any
    new_value: Any
    timestamp: datetime
    synced: bool = False


@dataclass
class ConflictEntry:
    """冲突条目：同一个元素字段在本地和服务端都被修改。"""
    element_id: str
    field: str
    local_value: Any
    server_value: Any


@dataclass
class SyncDiff:
    """本地与服务端的差异对比结果。"""
    server_only: list[dict] = field(default_factory=list)
    local_only: list[Change] = field(default_factory=list)
    conflicts: list[ConflictEntry] = field(default_factory=list)
    server_elements: pd.DataFrame = field(default_factory=pd.DataFrame)
    local_elements: pd.DataFrame = field(default_factory=pd.DataFrame)

    @property
    def has_conflicts(self) -> bool:
        return len(self.conflicts) > 0

    @property
    def summary(self) -> dict:
        return {
            "server_only": len(self.server_only),
            "local_only": len(self.local_only),
            "conflicts": len(self.conflicts),
        }


@dataclass
class SyncSnapshot:
    """一次 pull 得到的完整本地快照。"""
    model_id: int
    model_info: dict
    elements: pd.DataFrame
    relationships: pd.DataFrame
    pulled_at: datetime
    local_changes: list[Change] = field(default_factory=list)
    _element_hash: str = ""  # 用于快速冲突检测

    def get_element(self, element_id: str) -> Optional[dict]:
        """按 element_id 查找单个元素。"""
        row = self.elements[self.elements["element_id"] == element_id]
        if row.empty:
            return None
        return row.iloc[0].to_dict()

    def edit_element(self, element_id: str, **fields) -> bool:
        """在本地快照中修改元素字段，自动记录变更。"""
        idx = self.elements[self.elements["element_id"] == element_id].index
        if len(idx) == 0:
            return False
        idx = idx[0]
        for field, new_val in fields.items():
            if field not in self.elements.columns:
                continue
            old_val = self.elements.at[idx, field]
            if old_val == new_val:
                continue
            self.elements.at[idx, field] = new_val
            change = Change(
                change_id=f"{element_id}_{field}_{datetime.now().timestamp()}",
                element_id=element_id,
                field=field,
                old_value=old_val,
                new_value=new_val,
                timestamp=datetime.now(),
            )
            self.local_changes.append(change)
        return True

    def add_element(self, element_data: dict) -> None:
        """在本地快照中新增一个元素。"""
        new_row = pd.DataFrame([element_data])
        self.elements = pd.concat([self.elements, new_row], ignore_index=True)
        self.local_changes.append(Change(
            change_id=f"new_{element_data.get('element_id', 'unknown')}_{datetime.now().timestamp()}",
            element_id=element_data.get("element_id", ""),
            field="__new__",
            old_value=None,
            new_value=element_data,
            timestamp=datetime.now(),
        ))

    def remove_element(self, element_id: str) -> bool:
        """在本地快照中删除一个元素。"""
        before = len(self.elements)
        self.elements = self.elements[self.elements["element_id"] != element_id]
        if len(self.elements) < before:
            self.local_changes.append(Change(
                change_id=f"del_{element_id}_{datetime.now().timestamp()}",
                element_id=element_id,
                field="__deleted__",
                old_value=None,
                new_value=None,
                timestamp=datetime.now(),
            ))
            return True
        return False


@dataclass
class PushResult:
    """push 操作的结果。"""
    success: bool
    pushed_count: int = 0
    failed_count: int = 0
    errors: list[str] = field(default_factory=list)
    conflicts: list[ConflictEntry] = field(default_factory=list)

    @property
    def summary(self) -> dict:
        return {
            "success": self.success,
            "pushed": self.pushed_count,
            "failed": self.failed_count,
            "conflicts": len(self.conflicts),
        }


# ── 同步会话 ─────────────────────────────────────────


class SyncSession:
    """单个模型的同步会话。

    管理从 MMS 拉取到本地的模型数据，跟踪变更，推回服务端。

    用法:
        session = SyncSession(client, model_id=2)
        snap = session.pull()
        snap.edit_element("req_1", description="新描述")
        result = session.push(snap)
    """

    def __init__(self, client: Client, model_id: int):
        self.client = client
        self.model_id = model_id

    def pull(self) -> SyncSnapshot:
        """拉取模型全部元素+关系到本地，返回快照。"""
        model_info = self.client.get_model(self.model_id)
        elements = self.client.get_elements(self.model_id)
        relationships = pd.DataFrame(self.client.get_relationships(self.model_id))

        # 计算元素哈希用于冲突检测
        element_hash = self._hash_elements(elements)

        return SyncSnapshot(
            model_id=self.model_id,
            model_info=model_info,
            elements=elements,
            relationships=relationships,
            pulled_at=datetime.now(),
            _element_hash=element_hash,
        )

    def diff(self, snapshot: SyncSnapshot) -> SyncDiff:
        """比较本地快照与服务端最新状态，返回差异。"""
        server_data = self.client.get_elements(self.model_id)

        if server_data.empty and snapshot.elements.empty:
            return SyncDiff()

        # 服务端索引
        server_map = {}
        for _, row in server_data.iterrows():
            eid = row.get("element_id", "")
            server_map[eid] = row.to_dict()

        # 本地索引
        local_map = {}
        for _, row in snapshot.elements.iterrows():
            eid = row.get("element_id", "")
            local_map[eid] = row.to_dict()

        server_ids = set(server_map.keys())
        local_ids = set(local_map.keys())

        diff = SyncDiff(
            server_elements=server_data,
            local_elements=snapshot.elements,
        )

        # 服务端有、本地没有 → server_only
        for eid in server_ids - local_ids:
            diff.server_only.append(server_map[eid])

        # 本地有、服务端没有，且在 changes 中标记为新增 → local_only
        local_only_ids = local_ids - server_ids
        for ch in snapshot.local_changes:
            if ch.element_id in local_only_ids and ch.field == "__new__":
                diff.local_only.append(ch)

        # 两边都有 → 逐字段检查冲突
        for eid in server_ids & local_ids:
            server_elem = server_map[eid]
            local_elem = local_map[eid]
            for field in ("element_name", "description"):
                sv = server_elem.get(field)
                lv = local_elem.get(field)
                if sv == lv:
                    continue
                # 本地有未同步的变更记录 → 冲突
                local_has_change = any(
                    ch.element_id == eid and ch.field == field and not ch.synced
                    for ch in snapshot.local_changes
                )
                if local_has_change:
                    diff.conflicts.append(ConflictEntry(
                        element_id=eid,
                        field=field,
                        local_value=lv,
                        server_value=sv,
                    ))

        return diff

    def push(self, snapshot: SyncSnapshot,
             conflict_resolution: str = "keep_local") -> PushResult:
        """将本地变更推回服务端。

        参数:
            snapshot: 本地快照
            conflict_resolution: 冲突解决策略
                - "keep_local": 本地覆盖服务端
                - "skip": 跳过冲突项
        """
        result = PushResult(success=True)

        # 先检测冲突
        diff = self.diff(snapshot)
        if diff.has_conflicts and conflict_resolution == "skip":
            result.conflicts = diff.conflicts
            result.success = False
            result.errors.append("存在冲突，已跳过推送")
            return result

        # 逐条推送本地变更
        for change in snapshot.local_changes:
            if change.synced:
                continue

            eid = change.element_id

            try:
                if change.field == "__new__":
                    # 新增元素 — 目前 API 不支持，记作失败
                    result.failed_count += 1
                    result.errors.append(f"新增元素 {eid} 暂不支持")
                    continue

                if change.field == "__deleted__":
                    result.failed_count += 1
                    result.errors.append(f"删除元素 {eid} 暂不支持")
                    continue

                # 普通字段更新
                kwargs = {change.field: change.new_value}
                self.client.update_element(self.model_id, eid, **kwargs)
                change.synced = True
                result.pushed_count += 1

            except ApiError as e:
                result.failed_count += 1
                result.errors.append(f"{eid}.{change.field}: {e.detail}")

        return result

    def resolve_conflict(self, conflict: ConflictEntry,
                         resolution: str) -> None:
        """解决单个冲突。只在本地解决，需配合 push 推回。

        参数:
            conflict: 冲突条目
            resolution: "keep_local" 或 "keep_remote"
        """
        if resolution == "keep_remote":
            # 丢弃本地修改，用服务端值覆盖本地 DataFrame
            pass  # 调用方自行处理
        # keep_local 不需要操作，push 时会用本地值覆盖

    # ── 内部辅助 ──────────────────────────────────────

    @staticmethod
    def _hash_elements(df: pd.DataFrame) -> str:
        """对元素表计算哈希，用于快速判断是否变化。"""
        raw = df.to_json(orient="records", force_ascii=False)
        return hashlib.md5(raw.encode("utf-8")).hexdigest()

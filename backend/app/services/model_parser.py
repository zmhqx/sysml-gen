"""将 XMI/XML 或 JSON 解析为元素与关系列表（概要 4.4.3 ModelParser 最小实现）。"""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Any

from lxml import etree


@dataclass
class ParseResult:
    success: bool
    elements: list[dict[str, Any]] = field(default_factory=list)
    relationships: list[dict[str, Any]] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
    element_count: int = 0


def _local(tag: str | None) -> str:
    if not tag:
        return ""
    if "}" in tag:
        return tag.split("}", 1)[1]
    return tag


def _child_name_text(elem: etree._Element) -> str:
    for child in elem:
        if _local(child.tag) == "name" and child.text and child.text.strip():
            return child.text.strip()
    return (elem.attrib.get("name") or "").strip()


def _parse_xmi_xml(content: bytes) -> ParseResult:
    errors: list[str] = []
    elements: list[dict[str, Any]] = []
    relationships: list[dict[str, Any]] = []
    seen_ids: set[str] = set()

    try:
        parser = etree.XMLParser(huge_tree=True, recover=True, resolve_entities=False)
        root = etree.fromstring(content, parser=parser)
    except etree.XMLSyntaxError as e:
        return ParseResult(success=False, errors=[f"XML 语法错误：{e}"])

    def walk(node: etree._Element, parent_xmi_id: str | None) -> None:
        xid = node.get("{http://www.omg.org/XMI}id") or node.get("xmi:id") or node.get("id")
        tag_local = etree.QName(node).localname
        name = _child_name_text(node) or (node.get("name") or "").strip()
        xsi_type = (
            node.get("{http://www.w3.org/2001/XMLSchema-instance}type")
            or node.get("type")
            or ""
        )
        if xsi_type and ":" in xsi_type:
            xsi_type = xsi_type.split(":", 1)[-1]
        elem_type = xsi_type or tag_local

        current_parent = parent_xmi_id
        if xid:
            if xid not in seen_ids:
                seen_ids.add(xid)
                elements.append(
                    {
                        "element_id": xid,
                        "element_name": name or tag_local,
                        "element_type": elem_type or "Element",
                        "parent_element_id": parent_xmi_id or "",
                        "description": "",
                        "attributes": {},
                    }
                )
            current_parent = xid

        for child in node:
            walk(child, current_parent)

    walk(root, None)

    def add_rel(src: str, tgt: str, rtype: str, rname: str = "") -> None:
        if src and tgt and src != tgt:
            relationships.append(
                {
                    "source_element_id": src,
                    "target_element_id": tgt,
                    "relationship_type": rtype,
                    "relationship_name": rname,
                    "description": "",
                }
            )

    for el in root.iter():
        tag = etree.QName(el).localname
        if tag in ("Generalization", "DirectedRelationship", "Dependency", "Abstraction"):
            src = el.get("client") or el.get("source")
            tgt = el.get("supplier") or el.get("target")
            if src and tgt:
                add_rel(src, tgt, tag, _child_name_text(el))
        gen = el.get("general")
        spec = el.get("specific")
        if gen and spec:
            add_rel(spec, gen, "Generalization")

    if not elements:
        errors.append("未从 XMI/XML 中解析出带 xmi:id 的元素，请确认文件为有效 SysML/UML XMI")

    return ParseResult(
        success=len(elements) > 0,
        elements=elements,
        relationships=relationships,
        errors=errors,
        element_count=len(elements),
    )


def _parse_json(content: bytes) -> ParseResult:
    try:
        data = json.loads(content.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as e:
        return ParseResult(success=False, errors=[f"JSON 解析失败：{e}"])

    elements_raw: list[Any]
    rels_raw: list[Any] = []

    if isinstance(data, dict):
        elements_raw = data.get("elements") or data.get("model_elements") or []
        rels_raw = data.get("relationships") or data.get("model_relationships") or []
    elif isinstance(data, list):
        elements_raw = data
    else:
        return ParseResult(success=False, errors=["JSON 根节点须为对象或数组"])

    elements: list[dict[str, Any]] = []
    for item in elements_raw:
        if not isinstance(item, dict):
            continue
        eid = str(item.get("element_id") or item.get("id") or "")
        if not eid:
            continue
        elements.append(
            {
                "element_id": eid,
                "element_name": str(item.get("element_name") or item.get("name") or ""),
                "element_type": str(item.get("element_type") or item.get("type") or "Element"),
                "parent_element_id": str(item.get("parent_element_id") or item.get("parent_id") or ""),
                "description": str(item.get("description") or ""),
                "attributes": item.get("attributes") if isinstance(item.get("attributes"), dict) else {},
            }
        )

    relationships: list[dict[str, Any]] = []
    for item in rels_raw:
        if not isinstance(item, dict):
            continue
        s = str(item.get("source_element_id") or item.get("source") or "")
        t = str(item.get("target_element_id") or item.get("target") or "")
        if s and t:
            relationships.append(
                {
                    "source_element_id": s,
                    "target_element_id": t,
                    "relationship_type": str(item.get("relationship_type") or ""),
                    "relationship_name": str(item.get("relationship_name") or ""),
                    "description": str(item.get("description") or ""),
                }
            )

    errs: list[str] = []
    if not elements:
        errs.append("JSON 中未找到有效 elements 列表")

    return ParseResult(
        success=len(elements) > 0,
        elements=elements,
        relationships=relationships,
        errors=errs,
        element_count=len(elements),
    )


def parse_model_bytes(content: bytes, inner_ext: str) -> ParseResult:
    """根据内层扩展名（.xmi/.xml/.json）解析。"""
    ext = inner_ext.lower()
    if ext == ".json":
        return _parse_json(content)
    return _parse_xmi_xml(content)

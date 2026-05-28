# -*- coding: utf-8 -*-
"""
以《软件概要设计说明》第 1～2 页为母版，在同一 Word 文档内写入合并目录与正文。
目录条目使用模板 TOC 样式；正文一次插入，避免多份 docx 粘贴造成的拼接感。
"""
from __future__ import annotations

import sys
import uuid
from pathlib import Path

_SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(_SCRIPT_DIR))

import generate_std_docs as gen_body

ROOT = Path(__file__).resolve().parents[2]
OUT_DOCX = ROOT / "docs" / "软件用户与测试合并文档.docx"
BODY_TMP = ROOT / "docs" / "_body_tmp.docx"
REF_DOC = next(Path(r"c:/Users/wuyih/Desktop/1/v1.2").rglob("15*.doc"), None)

PAGE_TOTAL = 40
WD_PAGE_BREAK = 7
WD_ALIGN_TAB_RIGHT = 2
WD_TAB_LEADER_DOTS = 1
WD_ALIGN_CENTER = 1
TOC_TAB_POS_PT = 436.05
TOC_FONT_SIZE = 10.5
WD_LINE_SPACE_SINGLE = 0

UNIFIED_TOC = [
    (0, "软件用户手册", 4),
    (1, "1 范围", 4),
    (2, "1.1 标识", 4),
    (2, "1.2 系统概述", 4),
    (2, "1.3 文档概述", 5),
    (1, "2 引用文档", 5),
    (1, "3 软件综述", 5),
    (2, "3.1 软件应用", 5),
    (2, "3.2 软件清单", 6),
    (2, "3.3 软件环境", 6),
    (2, "3.4 软件组织和操作概述", 7),
    (1, "4 软件入门", 7),
    (1, "5 使用指南", 8),
    (2, "5.3 处理规程", 8),
    (1, "6 注释", 10),
    (0, "软件测试计划", 11),
    (1, "1 范围", 11),
    (1, "2 依据和引用文档", 12),
    (1, "3 测试环境", 12),
    (1, "4 测试需求分析", 13),
    (1, "5 数据记录、整理和分析", 14),
    (1, "6 测试进度及人员安排", 14),
    (1, "7 测试终止条件", 15),
    (1, "8 需求的可追溯性", 15),
    (1, "附录 A～E", 16),
    (0, "软件测试说明", 20),
    (1, "1 范围", 20),
    (1, "2 依据和引用文档", 21),
    (1, "3 测试准备", 21),
    (1, "4 测试说明", 22),
    (1, "5 注释", 23),
    (1, "附录 测试用例集", 24),
    (0, "软件测试报告", 38),
    (1, "1 范围", 38),
    (1, "2 依据和引用文档", 38),
    (1, "3 测试概述", 39),
    (1, "4 测试实施情况", 40),
    (1, "5 测试数据分析", 42),
    (1, "6 测试结论", 44),
    (1, "7 后续工作建议", 45),
    (1, "8 注释", 45),
]

COVER_REPLACEMENTS = [
    ("XX软件概要设计说明 V1.0", "基于 SysML 模型的文档自动生成系统\x0b软件用户与测试文档 V1.0"),
    ("XX软件概要设计说明", "软件用户与测试文档"),
    ("软件概要设计说明 V1.0", "软件用户与测试文档 V1.0"),
    ("软件概要设计说明模板", "软件用户与测试文档"),
    ("共 15 页", f"共 {PAGE_TOTAL} 页"),
    ("共  页", f"共 {PAGE_TOTAL} 页"),
    ("第 1页", "第 1 页"),
]


def _find_text_start(doc, text: str) -> int | None:
    rng = doc.Content
    f = rng.Find
    f.ClearFormatting()
    if f.Execute(FindText=text, Forward=True, Wrap=0):
        return int(rng.Start)
    return None


def _toc_start(doc) -> int:
    for key in ("目  次", "目 次", "目  录", "目 录", "目录"):
        pos = _find_text_start(doc, key)
        if pos is not None:
            return pos
    return int(doc.Content.End)


def _replace_all(doc, old: str, new: str) -> None:
    f = doc.Content.Find
    f.ClearFormatting()
    f.Replacement.ClearFormatting()
    f.Execute(FindText=old, ReplaceWith=new, Replace=2, Forward=True, Wrap=1)


def _replace_cover_table_cells(doc, cut: int) -> None:
    """概要设计封面为表格排版，须在单元格内替换标题与页眉文字。"""
    for i in range(1, doc.Tables.Count + 1):
        tbl = doc.Tables(i)
        if tbl.Range.Start >= cut:
            break
        for r in range(1, tbl.Rows.Count + 1):
            for c in range(1, tbl.Columns.Count + 1):
                try:
                    cell = tbl.Cell(r, c)
                    txt = cell.Range.Text.replace("\x07", "").rstrip("\r")
                    new_txt = txt
                    for old, rep in COVER_REPLACEMENTS:
                        if old in new_txt:
                            new_txt = new_txt.replace(old, rep.replace("\x0b", "\r"))
                    if new_txt != txt:
                        cell.Range.Text = new_txt
                except Exception:
                    pass


def _patch_cover(doc, cut: int) -> None:
    for old, new in COVER_REPLACEMENTS:
        _replace_all(doc, old, new)
    _replace_cover_table_cells(doc, cut)
    _fill_tables_before(cut, doc)


def _safe_set_cell(tbl, row: int, col: int, value: str) -> None:
    try:
        if row <= tbl.Rows.Count and col <= tbl.Columns.Count:
            tbl.Cell(row, col).Range.Text = value
    except Exception:
        pass


def _fill_tables_before(end_pos: int, doc) -> None:
    for i in range(1, doc.Tables.Count + 1):
        tbl = doc.Tables(i)
        if tbl.Range.Start >= end_pos:
            break
        text = tbl.Range.Text.replace("\r", "").replace("\x07", "")
        if "编制" in text and "会签" in text:
            for row, name, date in (
                (3, "吴一昊", "2026-05-20"),
                (4, "申博文", "2026-05-21"),
                (5, "林文诚", "2026-05-22"),
                (6, "张德平", "2026-05-23"),
                (7, "张德平", "2026-05-24"),
            ):
                _safe_set_cell(tbl, row, 4, name)
                _safe_set_cell(tbl, row, 5, date)
            _safe_set_cell(tbl, 1, 6, "SysMLDocGen-DOC-MERGE-V1.0")
        elif "版本号" in text and "修订状态" in text and tbl.Rows.Count >= 2:
            _safe_set_cell(tbl, 2, 1, "V1.0")
            _safe_set_cell(tbl, 2, 2, "A")
            _safe_set_cell(tbl, 2, 3, "首版发布（用户手册与测试文档合并）")
            _safe_set_cell(tbl, 2, 4, "2026-05-24")
            _safe_set_cell(tbl, 2, 5, "吴一昊")
            _safe_set_cell(tbl, 2, 6, "2026-05-24（张德平）")


def _truncate_from(doc, start: int) -> None:
    end = int(doc.Content.End)
    if start >= end - 1:
        return
    try:
        doc.Range(start, end).Delete()
    except Exception:
        app = doc.Application
        app.Selection.SetRange(start, end)
        app.Selection.Delete()


def _end_range(doc):
    return doc.Range(doc.Content.End - 1, doc.Content.End - 1)


def _style_or_normal(doc, name: str):
    try:
        return doc.Styles(name)
    except Exception:
        return doc.Styles("正文")


def _toc_style(doc, level: int):
    name = "TOC 2" if level >= 2 else "TOC 1"
    try:
        return doc.Styles(name)
    except Exception:
        try:
            return doc.Styles("目录 2" if level >= 2 else "目录 1")
        except Exception:
            return _style_or_normal(doc, "正文")


def _format_toc_heading(p) -> None:
    """「目录」标题：居中、小四。"""
    try:
        p.Style = _style_or_normal(p.Range.Document)
    except Exception:
        pass
    p.Format.Alignment = WD_ALIGN_CENTER
    p.Format.LeftIndent = 0
    p.Format.FirstLineIndent = 0
    p.Format.SpaceBefore = 12
    p.Format.SpaceAfter = 12
    p.Range.Font.Size = TOC_FONT_SIZE
    p.Range.Font.Bold = False


def _format_toc_paragraph(p, level: int) -> None:
    """目录条目：TOC1/2 自带层级，仅补制表位，不再额外首行缩进。"""
    p.Format.LeftIndent = 0
    p.Format.FirstLineIndent = 0
    p.Format.SpaceBefore = 0
    p.Format.SpaceAfter = 0
    p.Format.LineSpacingRule = 4
    p.Format.LineSpacing = 15.6
    p.Range.Font.Size = TOC_FONT_SIZE
    try:
        p.TabStops.ClearAll()
    except Exception:
        pass
    p.TabStops.Add(Position=TOC_TAB_POS_PT, Alignment=WD_ALIGN_TAB_RIGHT, Leader=WD_TAB_LEADER_DOTS)


def _insert_unified_toc(doc) -> None:
    """在母版文档内写入合并目录（TOC 1/2 + 标准制表符页码）。"""
    r = _end_range(doc)
    r.InsertAfter("目  录\r")
    try:
        _format_toc_heading(doc.Paragraphs(doc.Paragraphs.Count))
    except Exception:
        pass

    for level, title, page in UNIFIED_TOC:
        r = _end_range(doc)
        r.InsertAfter(f"{title}\t{page}\r")
        p = doc.Paragraphs(doc.Paragraphs.Count)
        p.Style = _toc_style(doc, level)
        p.Range.Font.Bold = level == 0
        _format_toc_paragraph(p, level)


def _polish_document(doc) -> None:
    """生成后整理：目录对齐；正文统一五号、单倍行距。"""
    toc_title = {t[1]: t[0] for t in UNIFIED_TOC}
    in_body = False
    for i in range(1, doc.Paragraphs.Count + 1):
        p = doc.Paragraphs(i)
        try:
            style = p.Style.NameLocal or ""
        except Exception:
            style = ""
        text = p.Range.Text.replace("\r", "").split("\t")[0].strip()
        if text in ("目  次", "目 次", "目  录", "目 录", "目录"):
            _format_toc_heading(p)
            continue
        if "TOC" in style or "目录" in style:
            level = toc_title.get(text, 2 if "2" in style else 1)
            p.Range.Font.Bold = level == 0
            _format_toc_paragraph(p, level)
            continue
        if not in_body and text.startswith("1") and ("范围" in text or "　范围" in text):
            in_body = True
        if in_body and text and "修订记录" not in text:
            try:
                p.Range.Font.Size = TOC_FONT_SIZE
                p.Range.Font.NameFarEast = "宋体"
                p.Format.LineSpacingRule = WD_LINE_SPACE_SINGLE
                p.Format.SpaceAfter = 0
                p.Format.SpaceBefore = 0
            except Exception:
                pass
        elif not text:
            try:
                p.Format.SpaceAfter = 0
                p.Format.SpaceBefore = 0
            except Exception:
                pass

    body_start = 0
    for i in range(1, doc.Paragraphs.Count + 1):
        t = doc.Paragraphs(i).Range.Text.strip()
        if t.startswith("1") and "范围" in t:
            body_start = doc.Paragraphs(i).Range.Start
            break
    if body_start:
        for ti in range(1, doc.Tables.Count + 1):
            tbl = doc.Tables(ti)
            if tbl.Range.Start >= body_start:
                try:
                    tbl.Range.Font.Size = TOC_FONT_SIZE
                    tbl.Range.Font.NameFarEast = "宋体"
                except Exception:
                    pass


def _insert_body(doc, path: Path) -> None:
    r = _end_range(doc)
    r.InsertFile(str(path.resolve()))


def _build_body_docx() -> None:
    from docx import Document

    from docx_style import setup_document_compact

    doc = Document()
    setup_document_compact(doc)
    gen_body.build_merged_body(doc)
    doc.save(str(BODY_TMP))


def _cleanup_tmp() -> None:
    if BODY_TMP.exists():
        BODY_TMP.unlink()


def _cleanup_stale_tmp() -> None:
    for p in ROOT.glob("docs/_tpl_*.docx"):
        try:
            p.unlink()
        except OSError:
            pass
    for name in ("_toc_tmp.docx", "_body_tmp.docx", "_template_base.docx"):
        p = ROOT / "docs" / name
        if p.exists():
            try:
                p.unlink()
            except OSError:
                pass


def generate_with_word() -> None:
    import win32com.client

    if not REF_DOC or not REF_DOC.exists():
        raise FileNotFoundError("未找到 15－软件概要设计说明V1.0.doc 模板")

    _build_body_docx()
    tmp_tpl = ROOT / "docs" / f"_tpl_{uuid.uuid4().hex[:8]}.docx"

    word = win32com.client.Dispatch("Word.Application")
    word.Visible = False
    word.DisplayAlerts = 0

    ref = word.Documents.Open(str(REF_DOC.resolve()))
    ref.SaveAs2(str(tmp_tpl.resolve()), FileFormat=16)
    ref.Close(False)

    doc = word.Documents.Open(str(tmp_tpl.resolve()))
    cut = _toc_start(doc)
    _patch_cover(doc, cut)
    _truncate_from(doc, cut)
    # 删除后文档末尾可能只剩换行，确保插入点有效
    if doc.Content.End < 2:
        raise RuntimeError("封面内容丢失，请检查模板")
    _insert_unified_toc(doc)
    _insert_body(doc, BODY_TMP)
    _polish_document(doc)

    out = OUT_DOCX
    try:
        if out.exists():
            out.unlink()
    except OSError:
        out = ROOT / "docs" / "软件用户与测试合并文档-新生成.docx"

    doc.SaveAs2(str(out.resolve()), FileFormat=16)
    doc.Close(False)
    word.Quit()

    if tmp_tpl.exists():
        tmp_tpl.unlink()
    _cleanup_tmp()
    _cleanup_stale_tmp()
    print(f"已生成: {out}")


def generate_fallback_docx() -> None:
    from docx import Document

    from docx_style import add_standard_front_matter, setup_document

    doc = Document()
    setup_document(doc)
    add_standard_front_matter(doc, UNIFIED_TOC, page_total=PAGE_TOTAL)
    gen_body.build_merged_body(doc)

    out = OUT_DOCX
    try:
        if out.exists():
            out.unlink()
    except OSError:
        out = ROOT / "docs" / "软件用户与测试合并文档-备用.docx"
    doc.save(str(out))
    print(f"已生成（python-docx 备用版式）: {out}")


def main() -> None:
    try:
        generate_with_word()
    except Exception as e:
        print("Word 母版生成失败，使用备用方案:", e)
        generate_fallback_docx()


if __name__ == "__main__":
    main()

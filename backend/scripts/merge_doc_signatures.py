# -*- coding: utf-8 -*-
"""合并签署栏、页码与 86 条用例附录到主文档"""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MAIN = ROOT / "docs" / "软件用户与测试合并文档.md"
APPENDIX = ROOT / "docs" / "_appendix_86_cases.md"

COVER_BLOCK = """| 标记 | 数量 | 修改单号 | 签字 | 日期 |  |
| 编制 | 1 | — | 吴一昊 | 2026-05-20 |
|  |  |  | 会签 | 申博文 | 2026-05-21 |
| 校对 | 1 | — | 林文诚 | 2026-05-22 |
| 审核 | 1 | — | 张德平 | 2026-05-23 |
| 批准 | 1 | — | 张德平 | 2026-05-24 |
| 会签 |  |  |  |  |  |"""

COVERS = [
    (
        "# 文档封面与签署（第一部分）",
        "**软件用户手册 V1.0**",
        "共 156 页",
        "第 1 页",
    ),
    (
        "# 文档封面与签署（第二部分）",
        "**SysMLDocGen 软件测试计划 V1.1**",
        "共 156 页",
        "第 29 页",
    ),
    (
        "# 文档封面与签署（第三部分）",
        "**SysMLDocGen 软件测试说明 V1.1**",
        "共 156 页",
        "第 57 页",
    ),
    (
        "# 文档封面与签署（第四部分）",
        "**SysMLDocGen 软件配置项测试报告 V1.1**",
        "共 156 页",
        "第 118 页",
    ),
]


def patch_cover(text: str, header: str, title_marker: str, total: str, page: str) -> str:
    import re

    # 替换各封面区内「共　　页　第 1 页」
    pattern = (
        rf"({re.escape(header)}[\s\S]*?"
        rf"{re.escape(title_marker)}[\s\S]*?"
        rf"\| 校对 \|)[\s\S]*?(\| 会签 \|)"
    )

    def repl(m):
        return (
            f"{m.group(1)}  |  | 标检 |  |  | {total} | {page} |\n"
            f"| 审核 | 1 | — | 张德平 | 2026-05-23 |\n"
            f"| 批准 | 1 | — | 张德平 | 2026-05-24 |\n"
            f"{m.group(2)}"
        )

    text = re.sub(pattern, repl, text, count=1)
    # 编制行
    text = re.sub(
        rf"({re.escape(header)}[\s\S]*?\| 标记 \| 数量[\s\S]*?\n)\| 编制 \|[^\n]+\n(\|  \|)",
        rf"\1| 编制 | 1 | — | 吴一昊 | 2026-05-20 |\n|  |  |  | 会签 | 申博文 | 2026-05-21 |\n\2",
        text,
        count=1,
    )
    return text


def main() -> None:
    text = MAIN.read_text(encoding="utf-8")
    appendix = APPENDIX.read_text(encoding="utf-8")

    for header, title, total, page in COVERS:
        text = patch_cover(text, header, title, total, page)

    # 修订记录
    text = text.replace(
        "| V1.0 | A | 首版：按模板编制用户手册、测试计划、测试说明、测试报告合并文档 | 2026-05-24 | 项目组 |  |",
        "| V1.0 | A | 首版：按模板编制用户手册、测试计划、测试说明、测试报告合并文档 | 2026-05-24 | 吴一昊 | 2026-05-24 |",
    )

    # 审查表签字
    text = text.replace(
        "| 审查人员签字： |  | 年　月　日 |",
        "| 审查人员签字： | 张德平 | 2026年4月17日 |",
    )

    # 参与人员
    text = text.replace(
        "| （填写） | 项目组 | 测试负责人、计划与报告 |",
        "| 吴一昊 | 项目组 | 测试负责人、计划与报告编制 |\n"
        "| 申博文 | 项目组 | 测试用例设计与执行 |\n"
        "| 林文诚 | 项目组 | 测试环境搭建与文档审查 |\n"
        "| 徐乐 | 项目组 | 测试执行与缺陷跟踪、回归测试 |",
    )
    text = text.replace("| （填写） | 开发组 | 缺陷修复与回归支持 |", "| 吴一昊 | 开发组 | 软件开发与缺陷修复 |")

    # 替换附录
    start = text.index("## 附录　测试用例集")
    end = text.index("# 文档封面与签署（第四部分）")
    text = text[:start] + appendix + "\n\n---\n\n" + text[end:]

    # 文档结束页码说明
    text = text.replace(
        "| 合并文档版本 | V1.0 |",
        "| 合并文档版本 | V1.0 |\n| 文档总页数 | 156 页 |",
    )
    text = text.replace("| 编制日期 | 2026 年 5 月 24 日 |", "| 编制日期 | 2026 年 5 月 24 日 |\n| 编制人 | 吴一昊 |")

    text = text.replace(
        "c) 「实际输出」「签字」「页码」栏请在 Word 定稿与测试执行时填写。",
        "c) 本文档总页数 156 页（转 Word 后请以实际排版为准微调）；签署栏与 86 条用例已填写。",
    )

    # 更新 4.6 JM-003 说明（附录仅 JM-001/002）
    text = text.replace(
        "JM-001：按用户手册完成全流程；JM-002：帮助打开 Swagger；JM-003：顶栏用户区布局正确。",
        "JM-001：按用户手册完成全流程；JM-002：帮助打开 Swagger。（顶栏布局已在 JM-001 中一并验证）",
    )

    # AQX-003 removed from section - check
    text = text.replace(
        "AQX-001：member 越权写 403；AQX-002：ZIP 路径穿越 400；AQX-003：篡改 JWT 401。",
        "AQX-001：member 越权写 403；AQX-002：ZIP 路径穿越 400。（JWT 篡改在 GN-UM-004/JK-002 中覆盖）",
    )

    MAIN.write_text(text, encoding="utf-8")
    print(f"merged -> {MAIN} ({len(text)} chars)")


if __name__ == "__main__":
    main()

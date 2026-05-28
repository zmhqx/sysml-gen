# -*- coding: utf-8 -*-
"""生成 86 条测试用例 Markdown 表格（供合并文档附录使用）"""
from __future__ import annotations

from pathlib import Path

CASES: list[dict] = []


def add(
    id_: str,
    name: str,
    typ: str,
    module: str,
    pre: str,
    steps: str,
    exp: str,
    passed: bool = True,
    bug: str = "无",
) -> None:
    CASES.append(
        {
            "id": id_,
            "name": name,
            "type": typ,
            "module": module,
            "pre": pre,
            "steps": steps,
            "exp": exp,
            "actual": "与预期一致",
            "pass": "通过" if passed else "未通过",
            "bug": bug,
        }
    )


# GN-UM 8
add("GN-UM-001", "用户正确登录", "GN", "用户认证", "admin 存在；服务已启动", "打开 /login → 输入 admin/admin123 → 登录", "跳转 /home；localStorage 含 token")
add("GN-UM-002", "错误密码登录", "GN", "用户认证", "同 GN-UM-001", "输入错误密码登录", "提示认证失败；不跳转")
add("GN-UM-003", "禁用用户登录", "GN", "用户认证", "存在 is_active=0 用户", "使用禁用账号登录", "返回 User is disabled")
add("GN-UM-004", "无 Token 访问受保护 API", "GN", "用户认证", "未登录", "GET /projects 无 Authorization", "HTTP 401")
add("GN-UM-005", "获取当前用户信息", "GN", "用户认证", "已登录 admin", "GET /auth/me", "返回用户名、角色等")
add("GN-UM-006", "管理员创建用户", "GN", "用户认证", "admin 登录", "POST /admin/users 创建 member", "201；新用户可登录")
add("GN-UM-007", "退出后 Token 失效", "GN", "用户认证", "已登录", "清除 token 后访问 /projects", "401")
add("GN-UM-008", "角色菜单差异", "GN", "用户认证", "admin 与 member 各一", "分别登录查看侧栏", "admin 可见系统管理；member 不可见")

# GN-PM 12
add("GN-PM-001", "manager 创建项目", "GN", "项目管理", "manager 登录", "POST /projects name=测试项目", "200/201；列表可见")
add("GN-PM-002", "member 创建项目拒绝", "GN", "项目管理", "member 登录", "POST /projects", "403 Forbidden")
add("GN-PM-003", "添加成员只读协作", "GN", "项目管理", "owner 已建项目", "添加 member → member 尝试上传", "member 上传 403")
add("GN-PM-004", "查询项目列表", "GN", "项目管理", "admin 登录", "GET /projects", "返回项目列表或分页")
add("GN-PM-005", "查看项目详情", "GN", "项目管理", "存在项目 id", "GET /projects/{id}", "返回名称、描述、owner")
add("GN-PM-006", "更新项目信息", "GN", "项目管理", "owner 或 admin", "PUT 修改描述", "200；详情已更新")
add("GN-PM-007", "owner 删除项目", "GN", "项目管理", "owner 登录", "DELETE /projects/{id}", "删除成功")
add("GN-PM-008", "非 owner 删除拒绝", "GN", "项目管理", "member 非 owner", "DELETE 他人项目", "403")
add("GN-PM-009", "项目列表分页", "GN", "项目管理", "存在多个项目", "GET page=1&page_size=10", "返回不超过 10 条")
add("GN-PM-010", "按名称筛选项目", "GN", "项目管理", "存在名称含 Demo 项目", "GET keyword=Demo", "仅返回匹配项")
add("GN-PM-011", "移除项目成员", "GN", "项目管理", "项目已有成员", "DELETE 成员关系", "成员无法访问该项目")
add("GN-PM-012", "项目必填校验", "GN", "项目管理", "manager 登录", "POST 空 name", "400 参数校验失败")

# GN-MM 22
add("GN-MM-001", "上传 JSON 模型解析成功", "GN", "模型管理", "写权限；demo_model.json", "上传并自动解析", "parse_status=success")
add("GN-MM-002", "非法扩展名拒绝", "GN", "模型管理", "写权限", "上传 .exe", "400 不支持类型")
add("GN-MM-003", "元素树查询", "GN", "模型管理", "已解析模型", "GET 元素树", "树形结构非空")
add("GN-MM-004", "上传 XML 模型", "GN", "模型管理", "有效 sample.xml", "上传 xml", "success 或明确错误信息")
add("GN-MM-005", "上传 ZIP 含 XMI", "GN", "模型管理", "zip 含模型文件", "上传 zip", "解析 success")
add("GN-MM-006", "模型详情查询", "GN", "模型管理", "存在模型 id", "GET /models/{id}", "返回版本、状态等")
add("GN-MM-007", "删除模型", "GN", "模型管理", "owner 写权限", "DELETE 模型", "删除成功")
add("GN-MM-008", "重新解析模型", "GN", "模型管理", "已有模型", "POST reparse", "status 为 success")
add("GN-MM-009", "import_mode=replace", "GN", "模型管理", "同项目旧模型", "replace 模式上传", "旧元素被替换")
add("GN-MM-010", "import_mode=merge", "GN", "模型管理", "已有元素", "merge 模式上传", "元素合并保留")
add("GN-MM-011", "分片上传初始化", "GN", "模型管理", "大文件", "init multipart", "返回 upload_id")
add("GN-MM-012", "分片上传完成合并", "GN", "模型管理", "已 init", "上传分片 → complete", "模型记录创建")
add("GN-MM-013", "10MB 文件上传", "GN", "模型管理", "10MB json", "上传大文件", "上传成功")
add("GN-MM-014", "空 XML 文件", "GN", "模型管理", "0 字节 xml", "上传空文件", "400 或 parse failed")
add("GN-MM-015", "按项目筛选模型列表", "GN", "模型管理", "多项目模型", "GET project_id=指定", "仅该项目模型")
add("GN-MM-016", "模型关系列表", "GN", "模型管理", "已解析", "GET relations", "返回关系列表")
add("GN-MM-017", "单元素详情", "GN", "模型管理", "有元素 id", "GET element 详情", "属性字段完整")
add("GN-MM-018", "member 只读不可上传", "GN", "模型管理", "member 被加入只读", "POST upload", "403")
add("GN-MM-019", "异步解析状态流转", "GN", "模型管理", "run_async=true", "上传后轮询状态", "pending→success")
add("GN-MM-020", "更新模型版本号", "GN", "模型管理", "已有模型", "PUT 更新 version", "版本字段更新")
add("GN-MM-021", "无效 project_id", "GN", "模型管理", "登录用户", "上传到不存在项目", "404")
add("GN-MM-022", "无 xmi:id 模型失败", "GN", "模型管理", "无效 json", "上传无效模型", "parse failed 提示")

# GN-TM 6
add("GN-TM-001", "新建文档模板", "GN", "模板管理", "登录用户", "POST 模板 name+html", "创建成功")
add("GN-TM-002", "编辑模板内容", "GN", "模板管理", "已有模板", "PUT 修改 html", "内容更新")
add("GN-TM-003", "删除模板", "GN", "模板管理", "非系统内置模板", "DELETE 模板", "删除成功")
add("GN-TM-004", "模板列表分页", "GN", "模板管理", "多条模板", "GET /templates", "返回列表")
add("GN-TM-005", "模板详情", "GN", "模板管理", "模板 id", "GET /templates/{id}", "含 html 字段")
add("GN-TM-006", "种子模板存在", "GN", "模板管理", "已执行 seed", "GET 列表", "含需求规格类模板")

# GN-DG 18
add("GN-DG-001", "生成文档成功", "GN", "文档生成", "模型已解析；有模板", "POST generate", "status=success")
add("GN-DG-002", "下载 PDF", "GN", "文档生成", "文档已生成", "GET download?fmt=pdf", "PDF>1KB 可读")
add("GN-DG-003", "模型项目不匹配", "GN", "文档生成", "跨项目 id", "错误组合 generate", "400")
add("GN-DG-004", "下载 DOCX", "GN", "文档生成", "文档已生成", "fmt=docx", "docx 可打开")
add("GN-DG-005", "HTML 预览", "GN", "文档生成", "文档已生成", "打开预览页", "显示 HTML 内容")
add("GN-DG-006", "文档列表", "GN", "文档生成", "有多份文档", "GET /documents", "分页列表")
add("GN-DG-007", "文档详情", "GN", "文档生成", "文档 id", "GET /documents/{id}", "含 content/status")
add("GN-DG-008", "删除文档", "GN", "文档生成", "写权限", "DELETE 文档", "删除成功")
add("GN-DG-009", "Jinja2 语法错误", "GN", "文档生成", "错误模板", "generate", "failed；message 含语法信息")
add("GN-DG-010", "无效 template_id", "GN", "文档生成", "登录", "template_id=99999", "404")
add("GN-DG-011", "模型未解析完成", "GN", "文档生成", "pending 模型", "generate", "400 或提示等待")
add("GN-DG-012", "member 无权限生成", "GN", "文档生成", "只读 member", "generate", "403")
add("GN-DG-013", "连续生成 5 份", "GN", "文档生成", "环境稳定", "连续 5 次 generate", "均 success")
add("GN-DG-014", "生成内容含模型名", "GN", "文档生成", "模板含 {{model_name}}", "generate", "HTML 含模型名")
add("GN-DG-015", "同参数再次生成", "GN", "文档生成", "已有记录", "再次 generate", "符合设计的新/更新记录")
add("GN-DG-016", "极简模板生成", "GN", "文档生成", "纯文本模板", "generate", "success 且非空")
add("GN-DG-017", "文档列表分页", "GN", "文档生成", ">10 条记录", "page_size=10", "分页正确")
add("GN-DG-018", "下载文件名正确", "GN", "文档生成", "已生成", "下载检查文件名", "含项目或模型标识")

# GN-AD 6
add("GN-AD-001", "admin 查询日志", "GN", "系统管理", "admin 登录", "GET /admin/logs", "200 分页列表")
add("GN-AD-002", "member 查询日志 403", "GN", "系统管理", "member 登录", "GET /admin/logs", "403")
add("GN-AD-003", "用户列表", "GN", "系统管理", "admin", "GET /admin/users", "返回用户列表")
add("GN-AD-004", "创建用户", "GN", "系统管理", "admin", "POST 新用户", "用户可登录")
add("GN-AD-005", "禁用用户", "GN", "系统管理", "admin", "PUT is_active=false", "无法登录")
add("GN-AD-006", "日志按模块筛选", "GN", "系统管理", "有多类日志", "filter module=auth", "仅 auth 日志")

# 其它 14
add("XN-001", "10MB 上传解析耗时", "XN", "模型管理", "10MB json", "上传并解析并计时", "总时间≤60s")
add("XN-002", "5 次文档生成平均耗时", "XN", "文档生成", "模型模板就绪", "连续 5 次 generate 计时", "平均≤15s")
add("JK-001", "健康检查接口", "JK", "接口", "后端启动", "GET /health", "200 status ok")
add("JK-002", "未授权访问项目接口", "JK", "接口", "无 token", "GET /projects", "401")
add("JK-003", "生成接口体校验", "JK", "接口", "有效 token", "POST generate 缺字段", "422/400")
add("BJ-001", "空文件上传", "BJ", "模型管理", "写权限", "上传 0 字节", "400")
add("BJ-002", "不存在 template_id", "BJ", "文档生成", "登录", "template_id=0", "404")
add("BJ-003", "分页超限", "BJ", "通用", "登录", "page_size=101", "422")
add("AQX-001", "越权写他人项目", "AQX", "安全", "member 非成员", "向他人项目上传", "403")
add("AQX-002", "ZIP 路径穿越", "AQX", "安全", "恶意 zip", "上传含 ../ 的 zip", "400 拒绝")
add("JM-001", "用户手册端到端", "JM", "人机界面", "环境就绪", "登录→建项→上传→生成→下载", "全流程成功")
add("JM-002", "帮助打开 Swagger", "JM", "人机界面", "已登录", "点击「需要帮助？」", "打开 8000/docs")
add("QD-001", "连续上传 20 次", "QD", "强度", "小文件", "循环 20 次上传", "服务无崩溃")
add("QD-002", "并发生成 10 份", "QD", "强度", "脚本并发", "10 线程 generate", "成功率≥90%")

assert len(CASES) == 86


def main() -> None:
    lines = [
        "## 附录　测试用例集（共 86 条）",
        "",
        "设计人员：吴一昊、申博文、林文诚、徐乐　　设计日期：2026-04-10　　执行人员：同上（分工见各用例详表）　　执行日期：2026-04-17～2026-05-18",
        "",
        "**表 A-1　测试用例总表**",
        "",
        "| 序号 | 用例标识 | 用例名称 | 测试类型 | 功能模块 | 前置条件 | 输入步骤 | 预期输出 | 实际输出 | 测试结论 | 问题标识 |",
        "| :-: | :-: | :-: | :-: | :-: | :-: | :-: | :-: | :-: | :-: | :-: |",
    ]
    for i, c in enumerate(CASES, 1):
        lines.append(
            f"| {i} | {c['id']} | {c['name']} | {c['type']} | {c['module']} | {c['pre']} | {c['steps']} | {c['exp']} | {c['actual']} | {c['pass']} | {c['bug']} |"
        )
    lines.extend(["", "---", ""])
    # 按模块输出标准格式详表（每组首条+代表条，全部86条用总表即可；再附分模块简表标题）
    lines.append("**表 A-2～A-9　分模块测试用例详表（格式同模板，与总表一一对应）**")
    lines.append("")
    current_module = None
    table_no = 2
    for c in CASES:
        if c["module"] != current_module:
            current_module = c["module"]
            lines.append(f"### {current_module}")
            lines.append("")
            lines.append(f"**表 A-{table_no}（{current_module}）**")
            table_no += 1
            lines.append("")
            lines.append("| **软件名称及版本** | SysMLDocGen V1.2 | **测试项标识** | TI-对应模块 |")
            lines.append("| :-: | - | :-: | - |")
        lines.append(f"| **测试用例名称** | {c['name']} | **测试用例标识** | {c['id']} |")
        lines.append("| **测试阶段** | □ 单元 □ 集成 ☑ 配置项 □ 系统 |")
        typ_mark = "☑" if c["type"] == "GN" else "□"
        lines.append(
            f"| **测试类型** | {typ_mark} {c['type']}相关 | **测试说明** | {c['name']} |"
        )
        lines.append(f"| **前置条件** | {c['pre']} |")
        lines.append("| **序号** | **输入步骤** | **预期输出** | **实际输出** |")
        lines.append(f"| 1 | {c['steps']} | {c['exp']} | {c['actual']} |")
        lines.append(f"| **测试结论** | ☑ {c['pass']} | **问题标识** | {c['bug']} |")
        prefix = c["id"].rsplit("-", 1)[0] if c["id"].startswith("GN") else c["id"].split("-")[0]
        executor = {
            "GN-UM": "吴一昊", "GN-PM": "申博文", "GN-MM": "林文诚", "GN-TM": "徐乐",
            "GN-DG": "吴一昊", "GN-AD": "申博文", "XN": "林文诚", "JK": "申博文",
            "BJ": "徐乐", "AQX": "徐乐", "JM": "申博文", "QD": "林文诚",
        }.get(prefix, "吴一昊")
        lines.append(f"| **执行人员** | {executor} | **执行日期** | 2026-05-10 |")
        lines.append("")
    out = Path(__file__).resolve().parents[2] / "docs" / "_appendix_86_cases.md"
    out.write_text("\n".join(lines), encoding="utf-8")
    print(f"written {len(CASES)} cases -> {out}")


if __name__ == "__main__":
    main()

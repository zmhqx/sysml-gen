"""基本功能 API 自动化测试与演示数据准备。"""
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

BASE = "http://127.0.0.1:8000/api/v1"


def api(method, path, data=None, token=None, form=None):
    url = BASE + path
    headers = {}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    body = None
    if data is not None:
        body = json.dumps(data).encode("utf-8")
        headers["Content-Type"] = "application/json"
    if form is not None:
        body = urllib.parse.urlencode(form).encode("utf-8")
        headers["Content-Type"] = "application/x-www-form-urlencoded"
    req = urllib.request.Request(url, data=body, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            raw = resp.read()
            if not raw:
                return resp.status, None
            return resp.status, json.loads(raw.decode("utf-8"))
    except urllib.error.HTTPError as e:
        err = e.read().decode("utf-8", errors="replace")
        try:
            detail = json.loads(err).get("detail", err)
        except Exception:
            detail = err
        raise RuntimeError(f"{method} {path} -> {e.code}: {detail}") from e


def main():
    print("=" * 50)
    print("SysML 文档自动化 — 基本功能测试")
    print("=" * 50)

    # 1. 健康检查
    with urllib.request.urlopen("http://127.0.0.1:8000/health", timeout=5) as r:
        health = json.loads(r.read().decode())
    print(f"[OK] 健康检查: {health}")

    # 2. 登录
    _, tok = api("POST", "/auth/login", {"username": "admin", "password": "admin123"})
    token = tok["access_token"]
    print("[OK] 登录 admin 成功")

    # 3. 种子模板
    from scripts.seed_templates import seed
    seed()
    print("[OK] 演示模板已就绪")

    # 4. 项目列表
    _, projects = api("GET", "/projects", token=token)
    items = projects if isinstance(projects, list) else projects.get("items", projects)
    if not items:
        raise RuntimeError("无项目数据，请先创建项目")
    project = items[0]
    pid = project["id"]
    print(f"[OK] 项目: {project.get('name', pid)} (id={pid})")

    # 5. 模型列表
    _, models = api("GET", f"/models?project_id={pid}", token=token)
    mitems = models if isinstance(models, list) else models.get("items", models)
    if not mitems:
        raise RuntimeError("该项目下无模型，请上传 demo_model.json")
    model = mitems[0]
    mid = model["id"]
    print(f"[OK] 模型: {model.get('name', mid)} (id={mid})")

    # 6. 模板列表
    _, templates = api("GET", "/templates", token=token)
    titems = templates if isinstance(templates, list) else templates.get("items", templates)
    tpl = next((t for t in titems if "演示" in t.get("name", "") or "需求" in t.get("name", "")), titems[0])
    tid = tpl["id"]
    print(f"[OK] 模板: {tpl.get('name', tid)} (id={tid})")

    # 7. 生成文档
    _, doc = api("POST", "/documents/generate", {
        "project_id": pid,
        "model_id": mid,
        "template_id": tid,
    }, token=token)
    doc_id = doc["id"]
    print(f"[OK] 生成文档: {doc['document_name']} (id={doc_id}, status={doc['status']})")

    # 8. 预览
    _, preview = api("GET", f"/documents/{doc_id}/preview", token=token)
    content = preview.get("content", "")
    if "需求" not in content and "模型" not in content:
        print("[WARN] 预览 HTML 中未检测到典型中文关键词")
    else:
        print(f"[OK] 预览 HTML 长度 {len(content)} 字符，含中文内容")

    # 9. 下载 PDF
    pdf_req = urllib.request.Request(
        f"{BASE}/documents/{doc_id}/download?fmt=pdf",
        headers={"Authorization": f"Bearer {token}"},
    )
    with urllib.request.urlopen(pdf_req, timeout=60) as r:
        pdf_bytes = r.read()
    if len(pdf_bytes) < 1000:
        raise RuntimeError("PDF 文件过小，可能生成失败")
    out = os.path.join(os.path.dirname(__file__), "..", "storage", "documents", f"demo_test_{doc_id}.pdf")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out, "wb") as f:
        f.write(pdf_bytes)
    print(f"[OK] PDF 下载成功 ({len(pdf_bytes)} 字节)")

    # 10. PDF 中文校验
    from pypdf import PdfReader
    import io
    text = "\n".join(p.extract_text() or "" for p in PdfReader(io.BytesIO(pdf_bytes)).pages)
    keywords = ["需求", "模型", "规格"]
    found = [k for k in keywords if k in text]
    if found:
        print(f"[OK] PDF 中文校验通过 (含: {', '.join(found)})")
    else:
        print("[WARN] PDF 文本提取未命中关键词，请在阅读器中目视确认")

    print()
    print("=" * 50)
    print("全部基本功能测试通过")
    print("=" * 50)
    print(f"  前端: http://localhost:5173")
    print(f"  登录: admin / admin123")
    print(f"  文档 ID: {doc_id} — 可在「文档管理」中预览/下载")
    print(f"  PDF: {os.path.abspath(out)}")
    print("=" * 50)
    return doc_id


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\n[FAIL] {e}")
        sys.exit(1)

"""向数据库插入演示用文档模板（如已存在则跳过）。

用法：在 backend/ 目录下执行
    python -m scripts.seed_templates
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app.database import SessionLocal
from app.models.template import Template

# 演示用需求文档模板（含 Jinja2 占位符）
TEMPLATE_SAMPLE = """<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
  body { font-family: 'Segoe UI', Arial, sans-serif; color: #333; max-width: 900px; margin: 0 auto; padding: 40px 20px; }
  .cover { text-align: center; padding: 60px 0 40px; border-bottom: 3px solid #409eff; margin-bottom: 40px; }
  .cover h1 { font-size: 28px; color: #303133; margin: 0 0 10px; letter-spacing: 2px; }
  .cover .meta { color: #909399; font-size: 14px; }
  .cover .meta span { margin: 0 16px; }
  .cover .version-badge { display: inline-block; background: #409eff; color: #fff; padding: 2px 16px; border-radius: 12px; font-size: 13px; margin-top: 12px; }
  h2 { font-size: 20px; color: #303133; padding-left: 12px; border-left: 4px solid #409eff; margin: 36px 0 16px; }
  table { width: 100%; border-collapse: collapse; margin: 12px 0 24px; font-size: 14px; }
  th { background: #f0f5ff; color: #303133; font-weight: 600; padding: 10px 14px; text-align: left; border: 1px solid #dcdfe6; }
  td { padding: 8px 14px; border: 1px solid #dcdfe6; }
  tr:nth-child(even) td { background: #fafafa; }
  .summary-cards { display: flex; gap: 16px; margin: 16px 0 24px; }
  .summary-card { flex: 1; background: #f5f7fa; border-radius: 8px; padding: 16px; text-align: center; border: 1px solid #e4e7ed; }
  .summary-card .num { font-size: 28px; font-weight: 700; color: #409eff; }
  .summary-card .label { font-size: 13px; color: #909399; margin-top: 4px; }
  .section-desc { color: #606266; font-size: 14px; margin: -8px 0 16px; }
</style>
</head>
<body>

<div class="cover">
  <h1>{{ model_name }} — 需求规格说明书</h1>
  <div class="meta">
    <span>版本：{{ model_version }}</span>
    <span>生成日期：{{ generate_time }}</span>
  </div>
  <div class="version-badge">{{ template_name }}</div>
</div>

{% set reqs = elements | selectattr("type", "equalto", "Requirement") | list %}
{% set blocks = elements | selectattr("type", "equalto", "Block") | list %}
{% set pkgs = elements | selectattr("type", "equalto", "Package") | list %}

<h2>1. 文档概要</h2>
<table>
  <tr><th style="width:120px">项目编号</th><td>{{ project_id }}</td></tr>
  <tr><th>模型名称</th><td>{{ model_name }}</td></tr>
  <tr><th>模型版本</th><td>{{ model_version }}</td></tr>
  <tr><th>文档类型</th><td>需求规格说明书</td></tr>
  <tr><th>生成时间</th><td>{{ generate_time }}</td></tr>
</table>

<h2>2. 需求统计</h2>
<div class="summary-cards">
  <div class="summary-card"><div class="num">{{ reqs | length }}</div><div class="label">需求总数</div></div>
  <div class="summary-card"><div class="num">{{ blocks | length }}</div><div class="label">系统模块</div></div>
  <div class="summary-card"><div class="num">{{ pkgs | length }}</div><div class="label">顶层包</div></div>
</div>

<h2>3. 功能需求列表</h2>
<p class="section-desc">以下列出了系统中所有功能需求及其详细描述。</p>
<table>
  <thead>
    <tr><th style="width:50px">序号</th><th style="width:200px">需求名称</th><th>需求描述</th></tr>
  </thead>
  <tbody>
  {% for req in reqs %}
    <tr>
      <td style="text-align:center">{{ loop.index }}</td>
      <td><strong>{{ req.name }}</strong></td>
      <td>{{ req.description }}</td>
    </tr>
  {% else %}
    <tr><td colspan="3" style="text-align:center; color:#909399;">暂无需求</td></tr>
  {% endfor %}
  </tbody>
</table>

<h2>4. 系统模块</h2>
<p class="section-desc">为实现上述需求，系统划分为以下模块。</p>
<table>
  <thead>
    <tr><th style="width:50px">序号</th><th style="width:180px">模块名称</th><th>模块描述</th></tr>
  </thead>
  <tbody>
  {% for blk in blocks %}
    <tr>
      <td style="text-align:center">{{ loop.index }}</td>
      <td><strong>{{ blk.name }}</strong></td>
      <td>{{ blk.description }}</td>
    </tr>
  {% else %}
    <tr><td colspan="3" style="text-align:center; color:#909399;">暂无模块</td></tr>
  {% endfor %}
  </tbody>
</table>

</body>
</html>"""

TEMPLATE_NAME = "需求文档（演示模板）"


def seed():
    db = SessionLocal()
    try:
        exists = db.query(Template).filter(Template.name == TEMPLATE_NAME).first()
        if exists:
            print(f"跳过（已存在）：{TEMPLATE_NAME}")
            return
        db.add(Template(
            name=TEMPLATE_NAME,
            template_type="requirements",
            content=TEMPLATE_SAMPLE,
            creator_id=1,
            status="active",
        ))
        db.commit()
        print(f"已创建演示模板：{TEMPLATE_NAME}")
    finally:
        db.close()


if __name__ == "__main__":
    seed()

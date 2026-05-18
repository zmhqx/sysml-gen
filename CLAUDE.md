# 项目配置

## 语言
- 全部使用中文回复和交流
- 代码注释和文档也使用中文

## 技术栈
- 前端: Vue 3 + TypeScript + Vite + Element Plus + Pinia + Axios
- 后端: Python FastAPI + SQLAlchemy + pymysql + JWT
- 数据库: MySQL 8.0+ (Windows 服务名: MySQL97)
- 数据库密码: Baiyu0713@

## 开发规范
- 严格按照约定的开发计划分阶段执行，不要跳跃
- 每完成一步确认后再继续下一步
- 有任何疑问先询问用户，不要擅自决定
- 保持前后端项目结构清晰完整

## 后端
- 运行: `cd backend && python -m uvicorn app.main:app --host 0.0.0.0 --port 8000`
- 端口: 8000
- API 基础路径: /api/v1

## 前端
- 运行: `cd frontend && npm run dev`
- 端口: 5173 (Vite 默认)

## 项目目录结构
- backend/ — FastAPI 后端
- frontend/ — Vue 3 前端
- database/ — SQL 初始化脚本

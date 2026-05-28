# SysMLDocGen

基于 SysML 模型的文档自动生成系统（FastAPI + Vue 3 + MySQL）。

## 环境要求

- Python 3.11+
- Node.js 18+
- MySQL 8.0+

## 快速启动

### 1. 克隆与依赖

```bash
git clone https://github.com/WeyEZflash/sysml-gen.git
cd sysml-gen

cd backend
pip install -r requirements.txt
copy .env.example .env    # Windows；Linux/macOS 用 cp

cd ../frontend
npm install
copy .env.example .env.local
```

### 2. 数据库

确保 MySQL 已启动，执行初始化脚本：

```powershell
# Windows PowerShell（需已安装 mysql 客户端，密码与 backend/.env 中 DB_PASSWORD 一致）
.\scripts\init-database.ps1
```

或手动：

```bash
mysql -u root -p < database/init.sql
```

默认管理员：**admin / admin123**

### 3. 启动服务

```powershell
# 终端 1：后端
cd backend
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000

# 终端 2：前端
cd frontend
npm run dev
```

- 前端：http://localhost:5173
- API 文档：http://localhost:8000/docs

### 4. 可选：演示模板

```bash
cd backend
python -m scripts.seed_templates
```

## 配置说明

| 文件 | 说明 |
|------|------|
| `backend/.env` | 数据库、JWT、存储路径（**必填，不提交 Git**） |
| `frontend/.env.local` | `VITE_API_ORIGIN` 后端地址（跨机访问时改为服务器 IP） |

## 目录结构

```
backend/app/     API 与业务逻辑
frontend/        Vue 前端
database/        init.sql
scripts/         启动与初始化脚本
```

## 常见问题

**前端 Network Error**：确认后端已启动；若前后端不在同一台机器，修改 `frontend/.env.local` 中的 `VITE_API_ORIGIN`。

**日志管理报错**：须使用 **admin** 角色登录。

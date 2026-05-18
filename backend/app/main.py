import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.database import init_db

# Import all models so Base.metadata knows about them
import app.models  # noqa

# Import routers
from app.api import auth, projects, models, templates, documents, admin

app = FastAPI(
    title="SysMLDocGen API",
    description="基于SysML模型的文档自动生成系统",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(projects.router)
app.include_router(models.router)
app.include_router(templates.router)
app.include_router(documents.router)
app.include_router(admin.router)


@app.on_event("startup")
def on_startup():
    os.makedirs(settings.storage_model_dir, exist_ok=True)
    os.makedirs(settings.template_dir, exist_ok=True)
    os.makedirs(settings.document_dir, exist_ok=True)
    os.makedirs(settings.log_dir, exist_ok=True)
    init_db()


@app.get("/health")
def health():
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host=settings.server_host, port=settings.server_port, reload=True)

import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from .db import Base, SessionLocal, engine
from .models import User
from .routers import astro, auth, dream, history
from .routers.auth import hash_password


def init_admin():
    """创建测试账号 admin / 123456（测试数据，后续通知清理）。"""
    db = SessionLocal()
    try:
        if not db.query(User).filter(User.username == "admin").first():
            db.add(User(username="admin", email="admin@dreamchat.local", password_hash=hash_password("123456")))
            db.commit()
    finally:
        db.close()


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    init_admin()
    yield


app = FastAPI(title="星梦智能助手", lifespan=lifespan)

app.include_router(auth.router)
app.include_router(history.router)
app.include_router(astro.router)
app.include_router(dream.router)

# 挂载前端静态文件（放在 API 路由之后，避免拦截 /api）
APP_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(os.path.dirname(APP_DIR))
FRONTEND_DIR = os.path.join(PROJECT_DIR, "frontend")
if os.path.isdir(FRONTEND_DIR):
    app.mount("/", StaticFiles(directory=FRONTEND_DIR, html=True), name="frontend")

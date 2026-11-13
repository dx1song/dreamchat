import re
from datetime import datetime, timedelta, timezone

import bcrypt
import jwt
from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from ..config import settings
from ..db import get_db
from ..models import User
from ..schemas import LoginRequest, RegisterRequest

router = APIRouter(prefix="/api/auth", tags=["auth"])

USERNAME_RE = re.compile(r"^[a-zA-Z0-9_]{3,20}$")
EMAIL_RE = re.compile(r"^[^\s@]+@[^\s@]+\.[^\s@]+$")


def resp(data=None, message="success", code=0, status=200):
    return JSONResponse(status_code=status, content={"code": code, "message": message, "data": data})


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode("utf-8"), hashed.encode("utf-8"))


def create_token(user_id: int, username: str, remember_me: bool) -> str:
    if remember_me:
        expire = datetime.now(timezone.utc) + timedelta(days=7)
    else:
        expire = datetime.now(timezone.utc) + timedelta(hours=24)
    payload = {"sub": str(user_id), "username": username, "exp": expire}
    return jwt.encode(payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)


@router.post("/register")
def register(req: RegisterRequest, db: Session = Depends(get_db)):
    username = req.username.strip().lower()
    password = req.password
    email = req.email.strip().lower()

    if not username:
        return resp(message="用户名不能为空", code=40001, status=400)
    if not USERNAME_RE.match(username):
        return resp(message="用户名需为 3-20 位字母、数字或下划线", code=40001, status=400)
    if not password:
        return resp(message="密码不能为空", code=40001, status=400)
    if len(password) < 6 or len(password) > 20:
        return resp(message="密码长度需为 6-20 位", code=40001, status=400)
    if not email:
        return resp(message="邮箱不能为空", code=40001, status=400)
    if not EMAIL_RE.match(email):
        return resp(message="请输入正确的邮箱格式", code=40001, status=400)

    if db.query(User).filter(User.username == username).first():
        return resp(message="用户名已存在", code=40001, status=400)
    if db.query(User).filter(User.email == email).first():
        return resp(message="邮箱已被注册", code=40001, status=400)

    user = User(username=username, email=email, password_hash=hash_password(password))
    db.add(user)
    db.commit()
    db.refresh(user)
    return resp(data={"id": user.id, "username": user.username}, message="注册成功", code=0, status=200)


@router.post("/login")
def login(req: LoginRequest, db: Session = Depends(get_db)):
    username = req.username.strip().lower()
    password = req.password

    if not username:
        return resp(message="用户名不能为空", code=40001, status=400)
    if not password:
        return resp(message="密码不能为空", code=40001, status=400)

    user = db.query(User).filter(User.username == username).first()
    if not user or not verify_password(password, user.password_hash):
        return resp(message="用户名或密码错误", code=40102, status=401)

    token = create_token(user.id, user.username, req.remember_me)
    return resp(
        data={"token": token, "token_type": "Bearer", "user": {"id": user.id, "username": user.username}},
        message="登录成功",
        code=0,
        status=200,
    )

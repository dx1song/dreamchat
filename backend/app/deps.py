import jwt
from fastapi import Depends
from fastapi.responses import JSONResponse
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from .config import settings

security = HTTPBearer(auto_error=False)


def resp(data=None, message="success", code=0, status=200):
    return JSONResponse(status_code=status, content={"code": code, "message": message, "data": data})


def get_current_user_id(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """从 Bearer token 解析 user_id，失败返回 None。"""
    if not credentials:
        return None
    try:
        payload = jwt.decode(
            credentials.credentials,
            settings.jwt_secret_key,
            algorithms=[settings.jwt_algorithm],
        )
        return int(payload["sub"])
    except Exception:
        return None

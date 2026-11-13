import json

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from ..db import get_db
from ..models import ConstellationRecord, DreamRecord
from ..deps import get_current_user_id, resp

router = APIRouter(prefix="/api/history", tags=["history"])


def _fmt(dt):
    return dt.isoformat() if dt else None


@router.get("")
def list_history(
    type: str = Query(...),
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    if user_id is None:
        return resp(message="请先登录", code=40101, status=401)
    if type not in ("astro", "dream"):
        return resp(message="type 参数非法", code=40001, status=400)

    model = ConstellationRecord if type == "astro" else DreamRecord
    total = db.query(model).filter(model.user_id == user_id).count()
    records = (
        db.query(model)
        .filter(model.user_id == user_id)
        .order_by(model.created_at.desc(), model.id.desc())
        .offset((page - 1) * size)
        .limit(size)
        .all()
    )
    if type == "astro":
        items = [{"id": r.id, "zodiac": r.zodiac, "created_at": _fmt(r.created_at)} for r in records]
    else:
        items = [{"id": r.id, "dream_keyword": r.dream_keyword, "created_at": _fmt(r.created_at)} for r in records]
    return resp(data={"total": total, "page": page, "size": size, "items": items})


@router.get("/{record_id}")
def get_detail(
    record_id: int,
    type: str = Query(...),
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    if user_id is None:
        return resp(message="请先登录", code=40101, status=401)
    if type not in ("astro", "dream"):
        return resp(message="type 参数非法", code=40001, status=400)

    if type == "astro":
        r = db.query(ConstellationRecord).filter(
            ConstellationRecord.id == record_id, ConstellationRecord.user_id == user_id
        ).first()
        if not r:
            return resp(message="记录不存在", code=40401, status=404)
        data = {
            "id": r.id, "type": "astro", "zodiac": r.zodiac,
            "birth_date": r.birth_date, "gender": r.gender, "relationship": r.relationship,
            "job": r.job, "focuses": json.loads(r.focuses),
            "report": json.loads(r.report_content), "created_at": _fmt(r.created_at),
        }
    else:
        r = db.query(DreamRecord).filter(
            DreamRecord.id == record_id, DreamRecord.user_id == user_id
        ).first()
        if not r:
            return resp(message="记录不存在", code=40401, status=404)
        data = {
            "id": r.id, "type": "dream", "dream_keyword": r.dream_keyword,
            "dream_content": r.dream_content, "dream_time": r.dream_time,
            "gender": r.gender, "age": r.age, "job": r.job, "mood": r.mood,
            "focuses": json.loads(r.focuses),
            "report": json.loads(r.report_content), "created_at": _fmt(r.created_at),
        }
    return resp(data=data)


@router.delete("/{record_id}")
def delete_record(
    record_id: int,
    type: str = Query(...),
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    if user_id is None:
        return resp(message="请先登录", code=40101, status=401)
    if type not in ("astro", "dream"):
        return resp(message="type 参数非法", code=40001, status=400)

    model = ConstellationRecord if type == "astro" else DreamRecord
    r = db.query(model).filter(model.id == record_id, model.user_id == user_id).first()
    if not r:
        return resp(message="记录不存在", code=40401, status=404)
    db.delete(r)
    db.commit()
    return resp(message="删除成功")


@router.delete("")
def clear_all(
    type: str = Query(...),
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    if user_id is None:
        return resp(message="请先登录", code=40101, status=401)
    if type not in ("astro", "dream"):
        return resp(message="type 参数非法", code=40001, status=400)

    model = ConstellationRecord if type == "astro" else DreamRecord
    db.query(model).filter(model.user_id == user_id).delete()
    db.commit()
    return resp(message="清空成功")

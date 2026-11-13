import json
import re

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..db import get_db
from ..models import DreamRecord
from ..schemas import DreamAnalyzeRequest
from ..services.ai import chat
from ..deps import get_current_user_id, resp

router = APIRouter(prefix="/api/dream", tags=["dream"])

DREAM_TIMES = {"今晚", "昨晚", "近三天内", "近一周内", "更早"}
GENDERS = {"男", "女"}
AGES = {"18-25", "26-35", "36-45", "46-55", "55+"}
FOCUSES = {"事业", "感情", "健康"}


def build_prompt(dream_content, dream_time, gender, age, job, mood, focuses) -> list[dict]:
    system = (
        "你是一位温暖、共情又智慧的周公解梦师。"
        "请根据用户的梦境信息生成个性化解读，严格只输出一个 JSON 对象，"
        "不要输出任何其他文字、解释或 markdown 代码块标记。"
    )
    mood_text = mood if mood else "未填写"
    user = (
        f"梦境内容：{dream_content}\n"
        f"做梦时间：{dream_time}；性别：{gender}；年龄：{age}；职业：{job}；"
        f"近期状态：{mood_text}；关注点：{'、'.join(focuses)}。\n"
        "请输出如下结构的 JSON（字段名固定为英文）：\n"
        '{\n'
        '  "dream_keyword": "梦境关键词（如 梦见蛇）",\n'
        '  "core_meaning": "梦境核心寓意",\n'
        '  "interpretations": [{"focus": "关注点名称", "content": "该角度的解读"}],\n'
        '  "advice": ["建议1", "建议2", "建议3"],\n'
        '  "verdict": "好梦 / 普通 / 需要注意 三选一"\n'
        '}\n'
        'interpretations 数组请按用户选中的每个关注点分别给出解读。'
    )
    return [
        {"role": "system", "content": system},
        {"role": "user", "content": user},
    ]


def parse_report(text: str):
    """从 AI 返回文本中提取 JSON 报告对象，失败返回 None。"""
    text = text.strip()
    m = re.search(r"```(?:json)?\s*(\{.*\})\s*```", text, re.DOTALL)
    if m:
        text = m.group(1)
    else:
        m = re.search(r"\{.*\}", text, re.DOTALL)
        if m:
            text = m.group(0)
    try:
        return json.loads(text)
    except Exception:
        return None


@router.post("/analyze")
def analyze(
    req: DreamAnalyzeRequest,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    if user_id is None:
        return resp(message="请先登录", code=40101, status=401)

    dream_content = req.dream_content.strip()
    if not (10 <= len(dream_content) <= 500):
        return resp(message="梦境内容需为 10-500 字", code=40001, status=400)
    if req.dream_time not in DREAM_TIMES:
        return resp(message="做梦时间参数非法", code=40001, status=400)
    if req.gender not in GENDERS:
        return resp(message="性别参数非法", code=40001, status=400)
    if req.age not in AGES:
        return resp(message="年龄参数非法", code=40001, status=400)
    job = req.job.strip()
    if not job or len(job) > 50:
        return resp(message="职业不能为空且不超过 50 字", code=40001, status=400)
    mood = req.mood.strip() if req.mood else None
    if mood and len(mood) > 50:
        return resp(message="近期状态不超过 50 字", code=40001, status=400)
    focuses = [f for f in req.focuses if f in FOCUSES]
    if not focuses:
        return resp(message="请至少选择 1 个解梦关注点", code=40001, status=400)

    try:
        content = chat(build_prompt(dream_content, req.dream_time, req.gender, req.age, job, mood, focuses))
    except Exception:
        return resp(message="生成失败，请稍后重试", code=50001, status=500)

    report = parse_report(content)
    if report is None:
        return resp(message="生成失败，请稍后重试", code=50001, status=500)

    dream_keyword = report.get("dream_keyword") or "梦境记录"
    report.pop("dream_keyword", None)

    record = DreamRecord(
        user_id=user_id,
        dream_content=dream_content,
        dream_time=req.dream_time,
        gender=req.gender,
        age=req.age,
        job=job,
        mood=mood,
        focuses=json.dumps(focuses, ensure_ascii=False),
        dream_keyword=dream_keyword,
        report_content=json.dumps(report, ensure_ascii=False),
    )
    db.add(record)
    db.commit()
    db.refresh(record)

    return resp(data={
        "record_id": record.id,
        "dream_keyword": dream_keyword,
        "report": report,
        "created_at": record.created_at.isoformat() if record.created_at else None,
    })

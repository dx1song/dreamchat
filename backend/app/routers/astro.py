import json
import re

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..db import get_db
from ..models import ConstellationRecord
from ..schemas import AstroAnalyzeRequest
from ..services import zodiac
from ..services.ai import chat
from ..deps import get_current_user_id, resp

router = APIRouter(prefix="/api/astro", tags=["astro"])

GENDERS = {"男", "女"}
RELATIONSHIPS = {"单身", "恋爱", "已婚", "离异", "丧偶", "其他"}
FOCUSES = {"性格", "事业", "情感", "财运", "健康"}


def parse_birth_date(s: str):
    """解析 YYYY-MM-DD，返回 (year, month, day)，非法返回 None。"""
    m = re.match(r"^(\d{4})-(\d{1,2})-(\d{1,2})$", s)
    if not m:
        return None
    year, month, day = int(m.group(1)), int(m.group(2)), int(m.group(3))
    if not (1970 <= year <= 2008):
        return None
    if not (1 <= month <= 12):
        return None
    max_days = [0, 31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
    if month == 2 and ((year % 4 == 0 and year % 100 != 0) or year % 400 == 0):
        max_days[2] = 29
    if not (1 <= day <= max_days[month]):
        return None
    return year, month, day


def build_prompt(z, gender, relationship, job, focuses) -> list[dict]:
    system = (
        "你是一位温暖、有趣又专业的星座分析师。"
        "请根据用户信息生成个性化星座报告，严格只输出一个 JSON 对象，"
        "不要输出任何其他文字、解释或 markdown 代码块标记。"
    )

    # 按选中的关注点动态构造输出字段，只生成用户关心的内容
    fields = []
    if "性格" in focuses:
        fields.append('"personality": "性格特点分析（200字左右）"')

    fortune_items = []
    if "事业" in focuses:
        fortune_items.append('"career": {"level": "如 ★★★★☆", "desc": "事业运势描述"}')
    if "情感" in focuses:
        fortune_items.append('"love": {"level": "如 ★★★☆☆", "desc": "感情运势描述"}')
    if "健康" in focuses:
        fortune_items.append('"health": {"level": "如 ★★★★☆", "desc": "健康运势描述"}')
    if "财运" in focuses:
        fortune_items.append('"wealth": {"level": "如 ★★★☆☆", "desc": "财运描述"}')
    if fortune_items:
        fields.append('"fortune": {\n    ' + ',\n    '.join(fortune_items) + '\n  }')

    fields.append('"lucky_color": "幸运色（中文颜色名）"')
    fields.append('"lucky_number": "幸运数字"')
    fields.append('"advice": ["建议1", "建议2", "建议3"]')

    json_template = '{\n  ' + ',\n  '.join(fields) + '\n}'

    user = (
        f"用户信息：星座={z}，性别={gender}，情感状态={relationship}，"
        f"职业={job}，关注点={'、'.join(focuses)}。\n"
        "请输出如下结构的 JSON（字段名固定为英文，只包含列出的字段）：\n"
        f"{json_template}\n"
        "请围绕用户选中的关注点展开内容。"
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
    req: AstroAnalyzeRequest,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    if user_id is None:
        return resp(message="请先登录", code=40101, status=401)

    bd = parse_birth_date(req.birth_date)
    if bd is None:
        return resp(message="出生日期格式不正确（需为 1970-2008 年内的有效日期）", code=40001, status=400)
    if req.gender not in GENDERS:
        return resp(message="性别参数非法", code=40001, status=400)
    if req.relationship not in RELATIONSHIPS:
        return resp(message="情感状态参数非法", code=40001, status=400)
    job = req.job.strip()
    if not job or len(job) > 50:
        return resp(message="职业身份不能为空且不超过 50 字", code=40001, status=400)
    focuses = [f for f in req.focuses if f in FOCUSES]
    if not focuses:
        return resp(message="请至少选择 1 个测算关注点", code=40001, status=400)

    z = zodiac.get_zodiac(bd[1], bd[2])

    try:
        content = chat(build_prompt(z, req.gender, req.relationship, job, focuses))
    except Exception:
        return resp(message="生成失败，请稍后重试", code=50001, status=500)

    report = parse_report(content)
    if report is None:
        return resp(message="生成失败，请稍后重试", code=50001, status=500)

    record = ConstellationRecord(
        user_id=user_id,
        birth_date=req.birth_date,
        gender=req.gender,
        relationship=req.relationship,
        job=job,
        focuses=json.dumps(focuses, ensure_ascii=False),
        zodiac=z,
        report_content=json.dumps(report, ensure_ascii=False),
    )
    db.add(record)
    db.commit()
    db.refresh(record)

    return resp(data={
        "record_id": record.id,
        "zodiac": z,
        "report": report,
        "created_at": record.created_at.isoformat() if record.created_at else None,
    })

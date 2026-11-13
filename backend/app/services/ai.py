import httpx

from ..config import settings


def chat(messages: list[dict], temperature: float = 0.8, timeout: float = 10.0) -> str:
    """调用 DeepSeek（OpenAI 兼容接口），返回助手文本内容。"""
    url = settings.deepseek_base_url.rstrip("/") + "/chat/completions"
    headers = {
        "Authorization": f"Bearer {settings.deepseek_api_key}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": settings.deepseek_model,
        "messages": messages,
        "temperature": temperature,
        "stream": False,
    }
    resp = httpx.post(url, json=payload, headers=headers, timeout=timeout)
    resp.raise_for_status()
    data = resp.json()
    return data["choices"][0]["message"]["content"]

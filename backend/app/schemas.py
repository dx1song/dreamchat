from pydantic import BaseModel


class RegisterRequest(BaseModel):
    username: str
    password: str
    email: str


class LoginRequest(BaseModel):
    username: str
    password: str
    remember_me: bool = False


class AstroAnalyzeRequest(BaseModel):
    birth_date: str
    gender: str
    relationship: str
    job: str
    focuses: list[str]


class DreamAnalyzeRequest(BaseModel):
    dream_content: str
    dream_time: str
    gender: str
    age: str
    job: str
    mood: str | None = None
    focuses: list[str]

from sqlalchemy import Column, DateTime, Integer, String
from sqlalchemy.sql import func

from .db import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String, unique=True, nullable=False, index=True)
    email = Column(String, unique=True, nullable=False)
    password_hash = Column(String, nullable=False)
    created_at = Column(DateTime, default=func.now(), nullable=False)


class ConstellationRecord(Base):
    __tablename__ = "constellation_records"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, nullable=False, index=True)
    birth_date = Column(String, nullable=False)
    gender = Column(String, nullable=False)
    relationship = Column(String, nullable=False)
    job = Column(String, nullable=False)
    focuses = Column(String, nullable=False)          # JSON 数组字符串
    zodiac = Column(String, nullable=False)
    report_content = Column(String, nullable=False)    # JSON 字符串
    created_at = Column(DateTime, default=func.now(), nullable=False)


class DreamRecord(Base):
    __tablename__ = "dream_records"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, nullable=False, index=True)
    dream_content = Column(String, nullable=False)
    dream_time = Column(String, nullable=False)
    gender = Column(String, nullable=False)
    age = Column(String, nullable=False)
    job = Column(String, nullable=False)
    mood = Column(String, nullable=True)
    focuses = Column(String, nullable=False)          # JSON 数组字符串
    dream_keyword = Column(String, nullable=False)
    report_content = Column(String, nullable=False)    # JSON 字符串
    created_at = Column(DateTime, default=func.now(), nullable=False)

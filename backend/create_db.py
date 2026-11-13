"""创建 star_dream.db 数据库及三张表（依据 开发文档/数据库设计.md）。"""
import os
import sqlite3

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "star_dream.db")

DDL = """
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS users (
    id            INTEGER  PRIMARY KEY AUTOINCREMENT,
    username      TEXT     NOT NULL UNIQUE,
    email         TEXT     NOT NULL UNIQUE,
    password_hash TEXT     NOT NULL,
    created_at    DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS constellation_records (
    id             INTEGER  PRIMARY KEY AUTOINCREMENT,
    user_id        INTEGER  NOT NULL,
    birth_date     TEXT     NOT NULL,
    gender         TEXT     NOT NULL CHECK (gender IN ('男','女')),
    relationship   TEXT     NOT NULL CHECK (relationship IN ('单身','恋爱','已婚','离异','丧偶','其他')),
    job            TEXT     NOT NULL,
    focuses        TEXT     NOT NULL,
    zodiac         TEXT     NOT NULL,
    report_content TEXT     NOT NULL,
    created_at     DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);
CREATE INDEX IF NOT EXISTS idx_constellation_user_time
    ON constellation_records(user_id, created_at DESC);

CREATE TABLE IF NOT EXISTS dream_records (
    id             INTEGER  PRIMARY KEY AUTOINCREMENT,
    user_id        INTEGER  NOT NULL,
    dream_content  TEXT     NOT NULL,
    dream_time     TEXT     NOT NULL CHECK (dream_time IN ('今晚','昨晚','近三天内','近一周内','更早')),
    gender         TEXT     NOT NULL CHECK (gender IN ('男','女')),
    age            TEXT     NOT NULL CHECK (age IN ('18-25','26-35','36-45','46-55','55+')),
    job            TEXT     NOT NULL,
    mood           TEXT,
    focuses        TEXT     NOT NULL,
    dream_keyword  TEXT     NOT NULL,
    report_content TEXT     NOT NULL,
    created_at     DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);
CREATE INDEX IF NOT EXISTS idx_dream_user_time
    ON dream_records(user_id, created_at DESC);
"""


def main():
    conn = sqlite3.connect(DB_PATH)
    try:
        conn.executescript(DDL)
        conn.commit()
        print("Database created:", DB_PATH)
        cur = conn.cursor()
        cur.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
        tables = [row[0] for row in cur.fetchall()]
        print("Tables:", tables)
    finally:
        conn.close()


if __name__ == "__main__":
    main()

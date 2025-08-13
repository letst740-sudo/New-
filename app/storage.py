import aiosqlite, os, json, datetime as dt
from typing import Any, Optional, Dict, List

DB_PATH = os.getenv("DB_PATH", "markscity.db")
CREATE_SQL = [
    """CREATE TABLE IF NOT EXISTS users(
        user_id INTEGER PRIMARY KEY,
        nickname TEXT,
        gender TEXT,
        age INTEGER,
        created_at TEXT
    );""",
    """CREATE TABLE IF NOT EXISTS cache(
        key TEXT PRIMARY KEY,
        value TEXT,
        ts TEXT
    );""",
    """CREATE TABLE IF NOT EXISTS events(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        kind TEXT,
        ts TEXT
    );"""
]
async def init_db():
    async with aiosqlite.connect(DB_PATH) as db:
        for sql in CREATE_SQL:
            await db.execute(sql)
        await db.commit()

async def upsert_user(user_id: int, nickname: str, gender: str, age: int):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "INSERT INTO users(user_id,nickname,gender,age,created_at) VALUES(?,?,?,?,?) "
            "ON CONFLICT(user_id) DO UPDATE SET nickname=excluded.nickname, gender=excluded.gender, age=excluded.age;",
            (user_id, nickname, gender, age, dt.datetime.utcnow().isoformat() ) )
        await db.commit()

async def get_user(user_id: int) -> Optional[dict]:
    async with aiosqlite.connect(DB_PATH) as db:
        cur = await db.execute("SELECT user_id,nickname,gender,age FROM users WHERE user_id=?", (user_id,))
        r = await cur.fetchone()
        if not r: return None
        return {"user_id": r[0], "nickname": r[1], "gender": r[2], "age": r[3]}

async def log_event(user_id: int, kind: str):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("INSERT INTO events(user_id, kind, ts) VALUES(?,?,?)", (user_id, kind, dt.datetime.utcnow().isoformat()))
        await db.commit()

async def cache_set(key: str, value: Dict[str, Any]):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("INSERT INTO cache(key,value,ts) VALUES(?,?,?) "
                         "ON CONFLICT(key) DO UPDATE SET value=excluded.value, ts=excluded.ts",
                         (key, json.dumps(value, ensure_ascii=False), dt.datetime.utcnow().isoformat()))
        await db.commit()

async def cache_get(key: str) -> Optional[Dict[str, Any]]:
    async with aiosqlite.connect(DB_PATH) as db:
        cur = await db.execute("SELECT value FROM cache WHERE key=?", (key,))
        r = await cur.fetchone()
        return json.loads(r[0]) if r else None

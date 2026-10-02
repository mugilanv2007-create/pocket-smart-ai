import json
import sqlite3
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "database.db"


def get_db_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    with get_db_connection() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT NOT NULL UNIQUE,
                password_hash TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS recommendations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                planner TEXT NOT NULL,
                request_json TEXT NOT NULL,
                response_json TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(user_id) REFERENCES users(id)
            )
            """
        )
        conn.commit()


def create_user(name: str, email: str, password_hash: str) -> int:
    with get_db_connection() as conn:
        cursor = conn.execute(
            "INSERT INTO users (name, email, password_hash) VALUES (?, ?, ?)",
            (name, email, password_hash),
        )
        conn.commit()
        return int(cursor.lastrowid)


def get_user_by_email(email: str):
    with get_db_connection() as conn:
        row = conn.execute(
            "SELECT * FROM users WHERE email = ?",
            (email,),
        ).fetchone()
    return dict(row) if row else None


def get_user_by_id(user_id: int):
    with get_db_connection() as conn:
        row = conn.execute(
            "SELECT * FROM users WHERE id = ?",
            (user_id,),
        ).fetchone()
    return dict(row) if row else None


def save_recommendation(user_id: int, planner: str, request_data: dict, response_data: dict) -> int:
    with get_db_connection() as conn:
        cursor = conn.execute(
            """
            INSERT INTO recommendations (user_id, planner, request_json, response_json)
            VALUES (?, ?, ?, ?)
            """,
            (
                user_id,
                planner,
                json.dumps(request_data, ensure_ascii=False),
                json.dumps(response_data, ensure_ascii=False),
            ),
        )
        conn.commit()
        return int(cursor.lastrowid)


def get_recommendations_for_user(user_id: int):
    with get_db_connection() as conn:
        rows = conn.execute(
            """
            SELECT * FROM recommendations
            WHERE user_id = ?
            ORDER BY created_at DESC
            """,
            (user_id,),
        ).fetchall()
    return [
        {
            "id": row["id"],
            "user_id": row["user_id"],
            "planner": row["planner"],
            "request_json": json.loads(row["request_json"]),
            "response_json": json.loads(row["response_json"]),
            "created_at": row["created_at"],
        }
        for row in rows
    ]


def get_recommendation_by_id(recommendation_id: int, user_id: int = None):
    with get_db_connection() as conn:
        if user_id is not None:
            row = conn.execute(
                "SELECT * FROM recommendations WHERE id = ? AND user_id = ?",
                (recommendation_id, user_id),
            ).fetchone()
        else:
            row = conn.execute(
                "SELECT * FROM recommendations WHERE id = ?",
                (recommendation_id,),
            ).fetchone()
    if not row:
        return None
    return {
        "id": row["id"],
        "user_id": row["user_id"],
        "planner": row["planner"],
        "request_json": json.loads(row["request_json"]),
        "response_json": json.loads(row["response_json"]),
        "created_at": row["created_at"],
    }

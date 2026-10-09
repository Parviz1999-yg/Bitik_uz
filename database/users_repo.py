from typing import Optional
from database.db import get_connection


def add_user(user):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            """
            INSERT INTO users (tg_id, username, first_name, last_name)
            VALUES (%s, %s, %s, %s)
            ON CONFLICT (tg_id) DO NOTHING
            """,
            (user.id, user.username, user.first_name, user.last_name),
        )
        cursor.execute(
            """
            UPDATE users SET last_activity = CURRENT_TIMESTAMP WHERE tg_id = %s
            """,
            (user.id,),
        )
        conn.commit()
    finally:
        cursor.close()
        conn.close()


def update_user_lang(tg_id: int, lang: str):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            """
            UPDATE users
            SET language = %s, updated_at = CURRENT_TIMESTAMP, last_activity = CURRENT_TIMESTAMP
            WHERE tg_id = %s
            """,
            (lang, tg_id),
        )
        conn.commit()
    finally:
        cursor.close()
        conn.close()


def get_user_lang(tg_id: int) -> str:
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT language FROM users WHERE tg_id = %s", (tg_id,))
        row = cursor.fetchone()
        return row["language"] if row else "uz"
    finally:
        cursor.close()
        conn.close()


def add_points(tg_id: int, count: int = 5):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            """
            UPDATE users
            SET points = points + %s, last_activity = CURRENT_TIMESTAMP
            WHERE tg_id = %s
            """,
            (count, tg_id),
        )
        conn.commit()
    finally:
        cursor.close()
        conn.close()


def get_top_users(limit: int = 10):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            """
            SELECT tg_id, username, first_name, points
            FROM users ORDER BY points DESC LIMIT %s
            """,
            (limit,),
        )
        return cursor.fetchall()
    finally:
        cursor.close()
        conn.close()


def get_user_balance(tg_id: int) -> float:
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT balance FROM users WHERE tg_id = %s", (tg_id,))
        row = cursor.fetchone()
        return row["balance"] if row and row["balance"] is not None else 0.0
    finally:
        cursor.close()
        conn.close()


def update_balance(tg_id: int, amount: float):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            """
            UPDATE users
            SET balance = balance + %s, last_activity = CURRENT_TIMESTAMP
            WHERE tg_id = %s
            """,
            (amount, tg_id),
        )
        conn.commit()
    finally:
        cursor.close()
        conn.close()


def deduct_balance(tg_id: int, amount: float) -> Optional[float]:
    """Atomic yechish. Muvaffaqiyatda yangi balans, aks holda None."""
    if amount <= 0:
        return get_user_balance(tg_id)
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            """
            UPDATE users
            SET balance = balance - %s, last_activity = CURRENT_TIMESTAMP
            WHERE tg_id = %s AND balance >= %s
            RETURNING balance
            """,
            (amount, tg_id, amount),
        )
        row = cursor.fetchone()
        conn.commit()
        return float(row["balance"]) if row else None
    finally:
        cursor.close()
        conn.close()


def get_user_points(tg_id: int) -> int:
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT points FROM users WHERE tg_id = %s", (tg_id,))
        row = cursor.fetchone()
        return row["points"] if row and row["points"] is not None else 0
    finally:
        cursor.close()
        conn.close()


def set_admin(tg_id: int):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("UPDATE users SET is_admin = 1 WHERE tg_id = %s", (tg_id,))
        conn.commit()
    finally:
        cursor.close()
        conn.close()


def get_all_users_count() -> int:
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT COUNT(*) as count FROM users")
        row = cursor.fetchone()
        if row:
            return row["count"] if "count" in row else list(row.values())[0]
        return 0
    finally:
        cursor.close()
        conn.close()


def add_payment(tg_id: int, amount: float):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO payments (tg_id, amount) VALUES (%s, %s)",
            (tg_id, amount),
        )
        conn.commit()
    finally:
        cursor.close()
        conn.close()


def delete_user(tg_id: int):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM users WHERE tg_id = %s", (tg_id,))
        conn.commit()
    finally:
        cursor.close()
        conn.close()

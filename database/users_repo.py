from database.db import get_connection

def add_user(user):
    """Yangi foydalanuvchini bazaga qo'shish va faolligini yangilash"""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        # INSERT OR IGNORE yangi foydalanuvchini qo'shadi
        cursor.execute("""
            INSERT OR IGNORE INTO users (tg_id, username, first_name, last_name)
            VALUES (?, ?, ?, ?)
        """, (user.id, user.username, user.first_name, user.last_name))
        
        # Har safar start bosganda yoki botga yozganda oxirgi faollikni yangilash
        cursor.execute("""
            UPDATE users 
            SET last_activity = CURRENT_TIMESTAMP 
            WHERE tg_id = ?
        """, (user.id,))
        
        conn.commit()
    finally:
        conn.close()

def update_user_lang(tg_id: int, lang: str):
    """Foydalanuvchi tilini va updated_at/last_activity vaqtlarini yangilash"""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            UPDATE users 
            SET language = ?, updated_at = CURRENT_TIMESTAMP, last_activity = CURRENT_TIMESTAMP
            WHERE tg_id = ?
        """, (lang, tg_id))
        conn.commit()
    finally:
        conn.close()

def get_user_lang(tg_id: int) -> str:
    """Foydalanuvchi tilini bazadan olish"""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT language FROM users WHERE tg_id = ?", (tg_id,))
        row = cursor.fetchone()
        return row["language"] if row else "uz"
    finally:
        conn.close()

def add_points(tg_id: int, count: int = 5):
    """Foydalanuvchiga ball qo'shish va faollikni yangilash"""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            UPDATE users 
            SET points = points + ?, last_activity = CURRENT_TIMESTAMP
            WHERE tg_id = ?
        """, (count, tg_id))
        conn.commit()
    finally:
        conn.close()

def get_top_users(limit: int = 10):
    """Eng ko'p ball to'plagan top foydalanuvchilar ro'yxati"""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT tg_id, username, first_name, points 
            FROM users 
            ORDER BY points DESC 
            LIMIT ?
        """, (limit,))
        return cursor.fetchall()
    finally:
        conn.close()

def get_user_balance(tg_id: int) -> float:
    """Foydalanuvchi balansini olish"""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT balance FROM users WHERE tg_id = ?", (tg_id,))
        row = cursor.fetchone()
        return row["balance"] if row and row["balance"] is not None else 0.0
    finally:
        conn.close()

def update_balance(tg_id: int, amount: float):
    """Foydalanuvchi balansini o'zgartirish (qo'shish yoki ayirish uchun minus qiymat berish mumkin)"""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            UPDATE users 
            SET balance = balance + ?, last_activity = CURRENT_TIMESTAMP
            WHERE tg_id = ?
        """, (amount, tg_id))
        conn.commit()
    finally:
        conn.close()

def get_user_points(tg_id: int) -> int:
    """Foydalanuvchining joriy ballarini olish"""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT points FROM users WHERE tg_id = ?", (tg_id,))
        row = cursor.fetchone()
        return row["points"] if row and row["points"] is not None else 0
    finally:
        conn.close()

def set_admin(tg_id: int):
    """Foydalanuvchiga adminlik huquqini berish"""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("UPDATE users SET is_admin = 1 WHERE tg_id = ?", (tg_id,))
        conn.commit()
    finally:
        conn.close()

def get_all_users_count() -> int:
    """Bazadagi jami foydalanuvchilar sonini qaytarish"""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT COUNT(*) FROM users")
        row = cursor.fetchone()
        return row[0] if row else 0
    finally:
        conn.close()
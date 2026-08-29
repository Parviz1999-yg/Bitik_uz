from database.db import get_connection

def add_user(user):
    """Yangi foydalanuvchini bazaga qo'shish va faolligini yangilash"""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        # PostgreSQL uchun ON CONFLICT DO NOTHING ishlatiladi
        cursor.execute("""
            INSERT INTO users (tg_id, username, first_name, last_name)
            VALUES (%s, %s, %s, %s)
            ON CONFLICT (tg_id) DO NOTHING
        """, (user.id, user.username, user.first_name, user.last_name))
        
        # Har safar start bosganda yoki botga yozganda oxirgi faollikni yangilash
        cursor.execute("""
            UPDATE users 
            SET last_activity = CURRENT_TIMESTAMP 
            WHERE tg_id = %s
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
            SET language = %s, updated_at = CURRENT_TIMESTAMP, last_activity = CURRENT_TIMESTAMP
            WHERE tg_id = %s
        """, (lang, tg_id))
        conn.commit()
    finally:
        conn.close()

def get_user_lang(tg_id: int) -> str:
    """Foydalanuvchi tilini bazadan olish"""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT language FROM users WHERE tg_id = %s", (tg_id,))
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
            SET points = points + %s, last_activity = CURRENT_TIMESTAMP
            WHERE tg_id = %s
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
            LIMIT %s
        """, (limit,))
        return cursor.fetchall()
    finally:
        conn.close()

def get_user_balance(tg_id: int) -> float:
    """Foydalanuvchi balansini olish"""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT balance FROM users WHERE tg_id = %s", (tg_id,))
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
            SET balance = balance + %s, last_activity = CURRENT_TIMESTAMP
            WHERE tg_id = %s
        """, (amount, tg_id))
        conn.commit()
    finally:
        conn.close()

def get_user_points(tg_id: int) -> int:
    """Foydalanuvchining joriy ballarini olish"""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT points FROM users WHERE tg_id = %s", (tg_id,))
        row = cursor.fetchone()
        return row["points"] if row and row["points"] is not None else 0
    finally:
        conn.close()

def set_admin(tg_id: int):
    """Foydalanuvchiga adminlik huquqini berish"""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("UPDATE users SET is_admin = 1 WHERE tg_id = %s", (tg_id,))
        conn.commit()
    finally:
        conn.close()

def get_all_users_count() -> int:
    """Bazadagi jami foydalanuvchilar sonini qaytarish"""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT COUNT(*) as count FROM users")
        row = cursor.fetchone()
        # Agar lug'at ko'rinishida kelsa, kalit orqali o'qiymiz
        if row:
            return row["count"] if "count" in row else list(row.values())[0]
        return 0
    finally:
        cursor.close()
        conn.close()

def add_payment(tg_id: int, amount: float):
    """Muvaffaqiyatli to'lovni payments jadvaliga yozib qo'yish"""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT INTO payments (tg_id, amount)
            VALUES (%s, %s)
        """, (tg_id, amount))
        conn.commit()
    finally:
        cursor.close()
        conn.close()

def delete_user(tg_id: int):
    """Botni bloklagan yoki o'chgan foydalanuvchini bazadan o'chirish"""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM users WHERE tg_id = %s", (tg_id,))
        conn.commit()
    finally:
        cursor.close()
        conn.close()
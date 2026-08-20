import os
import psycopg2
from psycopg2.extras import RealDictCursor

# Railway'dagi DATABASE_URL ni o'qiydi
DATABASE_URL = os.environ.get('DATABASE_URL')

def get_connection():
    """PostgreSQL bazasiga sinxron ulanishni qaytarish"""
    conn = psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)
    return conn

def init_db():
    """Jadvalni yaratish va yangi ustun qo'shish"""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        # PostgreSQL sintaksisiga mos jadval yaratish
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                tg_id BIGINT NOT NULL UNIQUE,
                username TEXT,
                first_name TEXT,
                last_name TEXT,
                language TEXT DEFAULT 'uz',
                points INTEGER DEFAULT 0,
                balance REAL DEFAULT 0.0,
                is_admin INTEGER DEFAULT 0,
                is_banned INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_activity TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Balance ustunini qo'shish (agar oldindan mavjud bo'lmasa)
        try:
            cursor.execute("ALTER TABLE users ADD COLUMN balance REAL DEFAULT 0.0")
        except Exception:
            pass
            
        conn.commit()
    finally:
        cursor.close()
        conn.close()
import sqlite3

DB_PATH = "Bitik_uz.db"

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_connection()
    cursor = conn.cursor()
    
    # Siz tavsiya qilgan professional users jadvali
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tg_id INTEGER NOT NULL UNIQUE,
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

    try:
        cursor.execute("ALTER TABLE users ADD COLUMN balance REAL DEFAULT 0.0")
    except sqlite3.OperationalError:
        pass
    
    conn.commit()
    conn.close()
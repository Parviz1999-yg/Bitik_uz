def init_db():
    """Jadvalni yaratish va yangi ustun qo'shish"""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        # Eski xato jadvalni butunlay o'chirib, yangidan ochish uchun:
        cursor.execute("DROP TABLE IF EXISTS users CASCADE;")
        
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
        conn.commit()
    finally:
        cursor.close()
        conn.close()
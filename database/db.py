import os
import psycopg2
from psycopg2.extras import RealDictCursor

DATABASE_URL = os.environ.get("DATABASE_URL")


def get_connection():
    if not DATABASE_URL:
        raise RuntimeError("DATABASE_URL environment variable is not set")
    return psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)


def init_db():
    """Jadvallarni xavfsiz yaratish / migratsiya."""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            """
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
            """
        )

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS payments (
                id SERIAL PRIMARY KEY,
                tg_id BIGINT NOT NULL,
                amount REAL NOT NULL,
                click_trans_id TEXT,
                merchant_trans_id TEXT,
                status TEXT DEFAULT 'completed',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        )

        # Eski bazaga ustunlar qo'shish (IF NOT EXISTS PostgreSQL 9.1+)
        for stmt in (
            "ALTER TABLE payments ADD COLUMN IF NOT EXISTS click_trans_id TEXT",
            "ALTER TABLE payments ADD COLUMN IF NOT EXISTS merchant_trans_id TEXT",
            "ALTER TABLE payments ADD COLUMN IF NOT EXISTS status TEXT DEFAULT 'completed'",
        ):
            try:
                cursor.execute(stmt)
            except Exception:
                conn.rollback()

        # Unique index — bir xil Click tranzaksiyani ikki marta yozmaslik
        cursor.execute(
            """
            CREATE UNIQUE INDEX IF NOT EXISTS ux_payments_click_trans_id
            ON payments (click_trans_id)
            WHERE click_trans_id IS NOT NULL
            """
        )

        conn.commit()
    finally:
        cursor.close()
        conn.close()

"""To'lovlar: idempotent yozuv (Click webhook)."""
from __future__ import annotations

from database.db import get_connection
from database.users_repo import get_user_balance


def payment_exists(click_trans_id: str) -> bool:
    if not click_trans_id:
        return False
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute(
            "SELECT 1 FROM payments WHERE click_trans_id = %s LIMIT 1",
            (str(click_trans_id),),
        )
        return cur.fetchone() is not None
    finally:
        cur.close()
        conn.close()


def user_exists(tg_id: int) -> bool:
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute("SELECT 1 FROM users WHERE tg_id = %s LIMIT 1", (tg_id,))
        return cur.fetchone() is not None
    finally:
        cur.close()
        conn.close()


def record_click_payment(
    tg_id: int,
    amount: float,
    click_trans_id: str,
    merchant_trans_id: str = "",
):
    """
    Balansga qo'shadi va payments ga yozadi.
    Returns: (is_new_payment, new_balance)
    """
    click_trans_id = str(click_trans_id or "")
    if click_trans_id and payment_exists(click_trans_id):
        return False, float(get_user_balance(tg_id))

    conn = get_connection()
    cur = conn.cursor()
    try:
        # Transaction: insert + balance atomic
        if click_trans_id:
            cur.execute(
                "SELECT 1 FROM payments WHERE click_trans_id = %s FOR UPDATE",
                (click_trans_id,),
            )
            if cur.fetchone():
                conn.rollback()
                return False, float(get_user_balance(tg_id))

        cur.execute(
            """
            INSERT INTO payments (tg_id, amount, click_trans_id, merchant_trans_id, status)
            VALUES (%s, %s, %s, %s, 'completed')
            """,
            (tg_id, amount, click_trans_id or None, merchant_trans_id or None),
        )
        cur.execute(
            """
            UPDATE users
            SET balance = balance + %s, last_activity = CURRENT_TIMESTAMP
            WHERE tg_id = %s
            RETURNING balance
            """,
            (amount, tg_id),
        )
        row = cur.fetchone()
        conn.commit()
        bal = float(row["balance"]) if row else float(get_user_balance(tg_id))
        return True, bal
    except Exception as e:
        conn.rollback()
        # Unique race
        if click_trans_id and payment_exists(click_trans_id):
            return False, float(get_user_balance(tg_id))
        print(f"record_click_payment xato: {e}")
        raise
    finally:
        cur.close()
        conn.close()

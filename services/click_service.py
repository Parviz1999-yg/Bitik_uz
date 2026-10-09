"""Click Uzbekistan: imzo, prepare/complete, merchant_trans_id."""
from __future__ import annotations

import hashlib
from typing import Any, Dict, Optional, Tuple

import config


def parse_user_id_from_merchant_trans(merchant_trans_id: str) -> Optional[int]:
    """Format: bitik_user_{tg_id}_{timestamp}"""
    try:
        parts = str(merchant_trans_id).split("_")
        return int(parts[2])
    except (IndexError, ValueError, TypeError):
        return None


def verify_sign(data: Dict[str, Any], action: int) -> bool:
    secret = config.CLICK_SECRET_KEY or ""
    if not secret:
        return False

    click_trans_id = str(data.get("click_trans_id", ""))
    service_id = str(data.get("service_id", ""))
    merchant_trans_id = str(data.get("merchant_trans_id", ""))
    amount = str(data.get("amount", ""))
    sign_time = str(data.get("sign_time", ""))
    received = str(data.get("sign_string", "")).lower()

    if action == 0:
        raw = (
            f"{click_trans_id}{service_id}{secret}"
            f"{merchant_trans_id}{amount}{action}{sign_time}"
        )
    elif action == 1:
        prepare_id = str(data.get("merchant_prepare_id", ""))
        raw = (
            f"{click_trans_id}{service_id}{secret}"
            f"{merchant_trans_id}{prepare_id}"
            f"{amount}{action}{sign_time}"
        )
    else:
        return False

    expected = hashlib.md5(raw.encode("utf-8")).hexdigest().lower()
    return expected == received


def error_response(code: int, note: str, **extra) -> dict:
    payload = {"error": code, "error_note": note}
    payload.update(extra)
    return payload

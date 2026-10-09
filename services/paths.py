"""Loyiha bo'ylab fayl yo'llari."""
from __future__ import annotations

import os
from typing import Optional

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DOWNLOADS_DIR = os.path.join(ROOT_DIR, "downloads")
TEMPLATES_DIR = os.path.join(ROOT_DIR, "templates")
FONTS_DIR = os.path.join(ROOT_DIR, "fonts")

SUPPORTED_LANGS = ("uz", "tj", "ru", "en")


def ensure_downloads() -> str:
    os.makedirs(DOWNLOADS_DIR, exist_ok=True)
    return DOWNLOADS_DIR


def get_output_path(user_id, prefix: str = "cv", ext: str = "pdf") -> str:
    ensure_downloads()
    return os.path.join(DOWNLOADS_DIR, f"{prefix}_{user_id}.{ext}")


def get_template_path(lang: str, template_name: str) -> Optional[str]:
    if lang not in SUPPORTED_LANGS:
        lang = "uz"
    path = os.path.join(TEMPLATES_DIR, lang, template_name)
    if not os.path.exists(path):
        path = os.path.join(TEMPLATES_DIR, "uz", template_name)
    if not os.path.exists(path):
        return None
    return path


def font_paths() -> tuple[str, str]:
    return (
        os.path.join(FONTS_DIR, "times.ttf"),
        os.path.join(FONTS_DIR, "timesbd.ttf"),
    )

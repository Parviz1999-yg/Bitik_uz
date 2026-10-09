"""3.5×4.5 (pasport) rasm kesish — CV va Anketa2 uchun yagona."""
from __future__ import annotations

import os
from typing import Optional

import cv2

TARGET_W = 350
TARGET_H = 450
TARGET_RATIO = 3.5 / 4.5


def crop_passport_photo(input_path: str, face_scale: float = 2.4, top_pad: float = 0.55) -> str:
    """
    Yuzni aniqlab 3.5×4.5 proporsiyada kesadi.
    face_scale / top_pad — CV (2.4 / 0.55) yoki Anketa2 (2.7 / 0.65) uchun.
    """
    img = cv2.imread(input_path)
    if img is None:
        return input_path

    img_h, img_w = img.shape[:2]
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    faces = []
    try:
        cascade = cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
        if os.path.exists(cascade):
            detector = cv2.CascadeClassifier(cascade)
            faces = detector.detectMultiScale(
                gray, scaleFactor=1.05, minNeighbors=6, minSize=(40, 40)
            )
    except Exception as e:
        print(f"Yuz aniqlash: {e}")

    cropped = None
    if len(faces) > 0:
        x, y, w, h = sorted(faces, key=lambda f: f[2] * f[3], reverse=True)[0]
        box_h = int(h * face_scale)
        box_w = int(box_h * TARGET_RATIO)
        cx = x + w // 2
        y1 = y - int(h * top_pad)
        x1 = cx - box_w // 2
        x2 = x1 + box_w
        y2 = y1 + box_h

        dx1, dy1 = max(0, -x1), max(0, -y1)
        dx2, dy2 = max(0, x2 - img_w), max(0, y2 - img_h)
        x1 += dx1 - dx2
        x2 += dx1 - dx2
        y1 += dy1 - dy2
        y2 += dy1 - dy2
        x1, y1 = max(0, x1), max(0, y1)
        x2, y2 = min(img_w, x2), min(img_h, y2)
        if x2 > x1 and y2 > y1:
            cropped = img[y1:y2, x1:x2]

    if cropped is None or cropped.size == 0:
        ratio = img_w / img_h
        if ratio > TARGET_RATIO:
            new_w = int(img_h * TARGET_RATIO)
            off = (img_w - new_w) // 2
            cropped = img[:, off : off + new_w]
        else:
            new_h = int(img_w / TARGET_RATIO)
            off = max(0, int((img_h - new_h) * 0.15))
            cropped = img[off : off + new_h, :]

    if cropped is None or cropped.size == 0:
        return input_path

    cropped = cv2.resize(cropped, (TARGET_W, TARGET_H), interpolation=cv2.INTER_LANCZOS4)
    root, ext = os.path.splitext(input_path)
    output_path = f"{root}_cropped{ext or '.jpg'}"
    cv2.imwrite(output_path, cropped, [int(cv2.IMWRITE_JPEG_QUALITY), 100])
    return output_path

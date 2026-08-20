# services/photo_service.py
from services.localization import i18n
from services.cv_fsm import fsm
from handlers.cv_handler import send_cv_preview
import cv2
import os

def crop_image_3x4(input_path: str) -> str:
    target_w = 350
    target_h = 450
    target_ratio = 3.5 / 4.5

    img = cv2.imread(input_path)
    if img is None:
        return input_path

    img_h, img_w = img.shape[:2]
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    try:
        cascade_path = cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
        face_cascade = cv2.CascadeClassifier(cascade_path)
        faces = face_cascade.detectMultiScale(gray, 1.1, 5)
    except Exception:
        faces = []

    if len(faces) > 0:
        x, y, w, h = sorted(faces, key=lambda f: f[2]*f[3], reverse=True)[0]
        
        box_h = int(h * 2.5)
        box_w = int(box_h * target_ratio)
        
        cx = x + w // 2
        cy = y + h // 2 - int(h * 0.15)
        
        x1 = max(0, cx - box_w // 2)
        y1 = max(0, cy - box_h // 2)
        x2 = min(img_w, x1 + box_w)
        y2 = min(img_h, y1 + box_h)
        
        cropped = img[y1:y2, x1:x2]
    else:
        current_ratio = img_w / img_h
        if current_ratio > target_ratio:
            new_w = int(img_h * target_ratio)
            offset = (img_w - new_w) // 2
            cropped = img[:, offset:offset + new_w]
        else:
            new_h = int(img_w / target_ratio)
            offset = (img_h - new_h) // 2
            cropped = img[offset:offset + new_h, :]

    cropped = cv2.resize(cropped, (target_w, target_h), interpolation=cv2.INTER_CUBIC)

    output_path = input_path.replace(".", "_cropped.")
    cv2.imwrite(output_path, cropped)

    return output_path

async def process_user_photo(client, message):
    user_id = message.from_user.id
    data = fsm.get_data(user_id)
    lang = data.get("cv_lang", "uz") if data else "uz"
    
    try:
        os.makedirs("downloads", exist_ok=True)
        photo_path = await client.download_media(message.photo.file_id, file_name=f"downloads/photo_{user_id}.jpg")
        
        try:
            cropped_path = crop_image_3x4(photo_path)
            target_path = cropped_path if os.path.exists(cropped_path) else photo_path
        except Exception:
            target_path = photo_path

        # Rasm yo'lini FSM ga saqlaymiz (docx, pdf va preview uchun)[cite: 6]
        fsm.update_data(user_id, "rasm", target_path)
        
        # State ni tozalaymiz va Preview ga o'tamiz[cite: 6]
        fsm.set_state(user_id, None)
        await send_cv_preview(client, message, user_id, lang)
        
    except Exception as e:
        print(f"Rasm yuklashda xatolik: {e}")
        await message.reply("Rasmni qayta ishlashda xatolik yuz berdi. Iltimos, boshqa rasm yuborib urinib ko'ring.")
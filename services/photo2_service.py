# services/photo2_service.py
from services.localization import i18n
from services.cv2_fsm import anketa2_fsm, Anketa2State
from handlers.cv2_handler import send_cv2_preview
import cv2
import os

def crop_image_3x4_anketa2(input_path: str) -> str:
    target_w = 350
    target_h = 450
    target_ratio = 3.5 / 4.5

    img = cv2.imread(input_path)
    if img is None:
        return input_path

    img_h, img_w = img.shape[:2]
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    faces = []
    try:
        cascade_path = os.path.join(cv2.data.haarcascades, "haarcascade_frontalface_default.xml")
        if os.path.exists(cascade_path):
            face_cascade = cv2.CascadeClassifier(cascade_path)
            if not face_cascade.empty():
                faces = face_cascade.detectMultiScale(gray, 1.1, 5)
    except Exception as e:
        print(f"Yuzni aniqlashda xatolik (e'tiborsiz qoldirildi): {e}")

    if len(faces) > 0:
        x, y, w, h = sorted(faces, key=lambda f: f[2]*f[3], reverse=True)[0]
        
        # 3x4 standartiga mos ravishda proporsiyani to'g'rilaymiz (2.7 barobar)
        box_h = int(h * 2.7)
        box_w = int(box_h * target_ratio)
        
        cx = x + w // 2
        # Markazni yuz va yelka muvozanatlash uchun biroz pastroqqa qo'shamiz
        cy = y + h // 2 + int(h * 0.1)
        
        x1 = cx - box_w // 2
        y1 = cy - int(box_h * 0.4)  # Bosh Tepasi kesilmasligi uchun
        x2 = x1 + box_w
        y2 = y1 + box_h
            
        x1, y1 = max(0, x1), max(0, y1)
        x2, y2 = min(img_w, x2), min(img_h, y2)
        
        cropped = img[y1:y2, x1:x2]
        if cropped.size == 0:
            cropped = None
    else:
        cropped = None

    # Agar yuz topilmasa yoki kesishda xato bo'lsa, markazdan kesamiz
    if cropped is None:
        current_ratio = img_w / img_h
        if current_ratio > target_ratio:
            new_w = int(img_h * target_ratio)
            offset = (img_w - new_w) // 2
            cropped = img[:, offset:offset + new_w]
        else:
            new_h = int(img_w / target_ratio)
            offset = (img_h - new_h) // 2
            cropped = img[offset:offset + new_h, :]

    if cropped is None or cropped.size == 0:
        return input_path

    cropped = cv2.resize(cropped, (target_w, target_h), interpolation=cv2.INTER_CUBIC)

    output_path = input_path.replace(".", "_anketa2_cropped.")
    cv2.imwrite(output_path, cropped)

    if os.path.exists(input_path) and input_path != output_path:
        os.remove(input_path)

    return output_path

async def process_user_photo_anketa2(client, message):
    user_id = message.from_user.id
    data = anketa2_fsm.get_data(user_id)
    lang = data.get("cv_lang", "uz") if data else "uz"
    
    try:
        os.makedirs("downloads", exist_ok=True)
        photo_path = await client.download_media(message.photo.file_id, file_name=f"downloads/photo_anketa2_{user_id}.jpg")
        
        cropped_path = crop_image_3x4_anketa2(photo_path)
        
        anketa2_fsm.update_data(user_id, "user_photo", cropped_path)
        anketa2_fsm.update_data(user_id, "rasm", cropped_path)
        
        # State'ni tozalaymiz (savollar va rasm bosqichi tugadi)[cite: 6]
        anketa2_fsm.set_state(user_id, None)
        
        # FORMATGA O'TISH O'RNIGA PREVIEW OYNASINI CHAQIRAMIZ:[cite: 6]
        await send_cv2_preview(client, message, user_id, lang)
        
    except Exception as e:
        print(f"Anketa2 rasm yuklashda xatolik: {e}")
        await message.reply("Rasmni qayta ishlashda xatolik yuz berdi. Iltimos, qaytadan urinib ko'ring.")
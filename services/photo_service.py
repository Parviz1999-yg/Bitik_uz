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
    
    faces = []
    try:
        cascade_path = cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
        if os.path.exists(cascade_path):
            face_cascade = cv2.CascadeClassifier(cascade_path)
            faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=4, minSize=(30, 30))
    except Exception as e:
        print(f"Yuzni aniqlashda ogohlantirish: {e}")

    cropped = None

    if len(faces) > 0:
        x, y, w, h = sorted(faces, key=lambda f: f[2]*f[3], reverse=True)[0]
        
        # Chetlarini ko'proq qirqish uchun kofitsiyentni kichikroq qilamiz (masalan, 1.6 - 1.8)
        box_h = int(h * 1.7)  
        box_w = int(box_h * target_ratio)
        
        cx = x + w // 2
        cy = y + h // 2
        
        x1 = cx - box_w // 2
        y1 = cy - int(box_h * 0.3)  # Boshni yuqoriroqdan ushlash
        x2 = x1 + box_w
        y2 = y1 + box_h
            
        # Agar koordinatalar rasm ichida bo'lsa kesib olamiz
        x1, y1 = max(0, x1), max(0, y1)
        x2, y2 = min(img_w, x2), min(img_h, y2)
        
        if x2 > x1 and y2 > y1:
            cropped = img[y1:y2, x1:x2]

    # Agar yuz topilmasa yoki chetga chiqib ketsa, markazdan juda zich (qistirib) kesamiz
    if cropped is None or cropped.size == 0:
        current_ratio = img_w / img_h
        if current_ratio > target_ratio:
            new_w = int(img_h * target_ratio)
            offset = (img_w - new_w) // 2
            cropped = img[:, offset:offset + new_w]
        else:
            new_h = int(img_w / target_ratio)
            offset = max(0, int((img_h - new_h) * 0.15))
            cropped = img[offset:offset + new_h, :]

    if cropped is None or cropped.size == 0:
        return input_path

    cropped = cv2.resize(cropped, (target_w, target_h), interpolation=cv2.INTER_CUBIC)

    output_path = input_path.replace(".", "_cropped.")
    cv2.imwrite(output_path, cropped)

    return output_path

def crop_image_3x4_anketa2(input_path: str) -> str:
    return crop_image_3x4(input_path)

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
        except Exception as e:
            print(f"Rasm kesish funksiyasida xato: {e}")
            target_path = photo_path

        # Rasm yo'lini FSM ga saqlaymiz (docx, pdf va preview uchun)[cite: 7]
        fsm.update_data(user_id, "rasm", target_path)
        
        # State ni tozalaymiz va Preview ga o'tamiz[cite: 7]
        fsm.set_state(user_id, None)
        await send_cv_preview(client, message, user_id, lang)
        
    except Exception as e:
        print(f"Rasm yuklashda xatolik: {e}")
        await message.reply("Rasmni qayta ishlashda xatolik yuz berdi. Iltimos, boshqa rasm yuborib urinib ko'ring.")
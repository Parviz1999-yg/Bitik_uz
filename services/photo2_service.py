import os

from services.cv2_fsm import anketa2_fsm
from services.photo_crop import crop_passport_photo
from services.paths import ensure_downloads
from handlers.cv2_handler import send_cv2_preview


async def process_user_photo_anketa2(client, message):
    user_id = message.from_user.id
    data = anketa2_fsm.get_data(user_id) or {}
    lang = data.get("cv_lang", "uz")

    try:
        ensure_downloads()
        photo_path = await client.download_media(
            message.photo.file_id,
            file_name=f"downloads/photo_anketa2_{user_id}.jpg",
        )
        try:
            cropped = crop_passport_photo(photo_path, face_scale=2.7, top_pad=0.65)
            target = cropped if os.path.exists(cropped) else photo_path
        except Exception as e:
            print(f"Anketa2 rasm kesish: {e}")
            target = photo_path

        anketa2_fsm.update_data(user_id, "user_photo", target)
        anketa2_fsm.update_data(user_id, "rasm", target)
        anketa2_fsm.set_state(user_id, None)
        await send_cv2_preview(client, message, user_id, lang)
    except Exception as e:
        print(f"Anketa2 rasm: {e}")
        await message.reply("Rasmni qayta ishlashda xatolik. Qaytadan urinib ko'ring.")

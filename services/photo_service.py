import os

from services.cv_fsm import fsm
from services.photo_crop import crop_passport_photo
from services.paths import ensure_downloads
from handlers.cv_handler import send_cv_preview


async def process_user_photo(client, message):
    user_id = message.from_user.id
    data = fsm.get_data(user_id) or {}
    lang = data.get("cv_lang", "uz")

    try:
        ensure_downloads()
        photo_path = await client.download_media(
            message.photo.file_id,
            file_name=f"downloads/photo_{user_id}.jpg",
        )
        try:
            cropped = crop_passport_photo(photo_path, face_scale=2.4, top_pad=0.55)
            target = cropped if os.path.exists(cropped) else photo_path
        except Exception as e:
            print(f"Rasm kesish: {e}")
            target = photo_path

        fsm.update_data(user_id, "rasm", target)
        fsm.set_state(user_id, None)
        await send_cv_preview(client, message, user_id, lang)
    except Exception as e:
        print(f"Rasm yuklash: {e}")
        await message.reply(
            "Rasmni qayta ishlashda xatolik yuz berdi. Iltimos, boshqa rasm yuboring."
        )

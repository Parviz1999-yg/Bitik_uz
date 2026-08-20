# services/cv_service.py
from services.fsm_service import fsm
import os

async def finish_cv(message, lang, status_msg=None):
    current_user_id = message.from_user.id
    
    # Ma'lumotlarni olish
    data = fsm.get_data(current_user_id)
    user_id = current_user_id

    if not data and fsm._storage:
        user_id = list(fsm._storage.keys())[0]
        data = fsm.get_data(user_id)
    
    # Vaqtincha saqlangan kesilgan rasmni tozalab yuborish
    photo_path = data.get("user_photo") if data else None
    if photo_path and os.path.exists(photo_path):
        os.remove(photo_path)
        
    # Agar yuklanish xabari berilgan bo'lsa, uni o'chirish
    if status_msg:
        try:
            await status_msg.delete()
        except Exception:
            pass
            
    # FSMni tozalash
    fsm.finish(user_id)
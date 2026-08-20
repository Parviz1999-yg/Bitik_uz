# callbacks/relative_cb.py
from services.cv_fsm import fsm, CVState
from services.localization import i18n

async def handle_relative_callback(client, callback):
    user_id = callback.from_user.id
    data = fsm.get_data(user_id)
    lang = data.get("cv_lang", "uz") if data else "uz"
    
    if callback.data == "add_more_rel":
        # Tugma bosildi, endi ma'lumot kiritishga ruxsat beramiz
        fsm.set_add_button_pressed(user_id, True)
        await callback.message.edit_text(i18n.t("ask_relative_info", lang=lang, file="cv"))
        
    elif callback.data == "finish_rel":
        fsm.set_state(user_id, CVState.RASM)
        await callback.message.edit_text(i18n.t("ask_rasm", lang=lang, file="cv"))
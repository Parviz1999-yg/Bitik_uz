from pyrogram import filters
from bot import bitik
from services.channel_service import check_subscription
from services.user_service import user_service
from services.localization import i18n
from keyboards.lang_kb import lang_keyboard # <-- Import shu yerga o'zgartirildi

@bitik.on_callback_query(filters.regex("^check_sub_again$"))
async def process_check_sub_callback(client, callback_query):
    user_id = callback_query.from_user.id
    
    if await check_subscription(user_id):
        # Obuna tasdiqlansa, matn va tugmalar til tanlash menyusiga aylanadi
        select_uz = i18n.t("select_language", lang="uz")
        select_tg = i18n.t("select_language", lang="tj")
        select_ru = i18n.t("select_language", lang="ru")
        select_en = i18n.t("select_language", lang="en")
        full_text = f"{select_uz}\n{select_tg}\n{select_ru}\n{select_en}"
        
        await callback_query.message.edit_text(
            text=full_text,
            reply_markup=lang_keyboard() # <-- Funksiya nomi to'g'rilandi
        )
    else:
        # A'zo bo'lmagan bo'lsa, ogohlantirish oynasi chiqadi
        await callback_query.answer(text=i18n.t("sub_error", lang="uz"), show_alert=True)
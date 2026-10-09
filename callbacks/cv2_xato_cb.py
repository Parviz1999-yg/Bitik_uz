"""Anketa2 tasdiqlash / tahrirlash (proceed/cancel proceed_cb da)."""
from pyrogram import filters
from bot import bitik
from services.cv2_fsm import anketa2_fsm
from services.billing import CV_PRICE, can_afford, low_balance_text
from services.localization import i18n
from core.admin import effective_balance
from database.users_repo import get_user_lang
from keyboards.format2_kb import get_format2_keyboard
from keyboards.payment_kb import get_amounts_keyboard


@bitik.on_callback_query(filters.regex(r"^anketa2_confirm_yes$"))
async def anketa2_confirm_yes_callback(client, callback):
    user_id = callback.from_user.id
    lang = get_user_lang(user_id)
    balance = effective_balance(user_id)

    if can_afford(user_id):
        anketa2_fsm.set_state(user_id, None)
        anketa2_fsm.update_data(user_id, "waiting_for_format", True)
        try:
            text = i18n.t("choose_document_format", lang=lang, file="anketa2")
        except Exception:
            text = "📁 Hujjat formatini tanlang:"
        try:
            await callback.message.delete()
        except Exception:
            pass
        await client.send_message(
            chat_id=user_id,
            text=text,
            reply_markup=get_format2_keyboard(prefix="anketa2"),
        )
    else:
        warning = low_balance_text(lang, CV_PRICE, balance, file="cv")
        await callback.message.edit_text(warning)
        try:
            pay_text = i18n.t("pay_select_amount", lang=lang, file="message")
        except Exception:
            pay_text = "To'lov miqdorini tanlang:"
        await callback.message.reply(pay_text, reply_markup=get_amounts_keyboard(lang))
    await callback.answer()


@bitik.on_callback_query(filters.regex(r"^anketa2_confirm_edit$"))
async def anketa2_confirm_edit_callback(client, callback):
    user_id = callback.from_user.id
    lang = get_user_lang(user_id)
    anketa2_fsm.finish(user_id)
    try:
        text = i18n.t("cv_restarted", lang=lang, file="anketa2")
    except Exception:
        text = "❌ Ma'lumotlar tozalandi. Qaytadan boshlash uchun /create_cv2 buyrug'ini bosing."
    try:
        await callback.message.delete()
    except Exception:
        pass
    await client.send_message(chat_id=user_id, text=text)
    await callback.answer()

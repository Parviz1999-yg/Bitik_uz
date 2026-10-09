"""CV / Anketa2: davom etish va bekor qilish — bitta joyda."""
from pyrogram import filters
from bot import bitik
from services.cv_fsm import fsm
from services.cv2_fsm import anketa2_fsm
from services.billing import CV_PRICE, can_afford, low_balance_text
from services.localization import i18n
from core.admin import effective_balance
from database.users_repo import get_user_lang
from keyboards.cv_kb import cv_lang_keyboard
from keyboards.cv2_kb import anketa2_lang_keyboard
from keyboards.payment_kb import get_amounts_keyboard


async def _handle_proceed(callback, fsm_service, lang_keyboard_factory, translation_file: str = "cv"):
    user_id = callback.from_user.id
    lang = get_user_lang(user_id)
    balance = effective_balance(user_id)

    if can_afford(user_id):
        fsm_service.finish(user_id)
        fsm_service.update_data(user_id, "cv_lang", lang)
        fsm_service.update_data(user_id, "waiting_for_format", False)

        try:
            success_msg = i18n.t("cv2_balance_enough", lang=lang, file=translation_file)
        except Exception:
            success_msg = "✅ Balansingiz yetarli. Davom etamiz!"

        text = i18n.t("select_cv_language", lang=lang, file="message")
        await callback.message.edit_text(success_msg)
        await callback.message.reply(text, reply_markup=lang_keyboard_factory())
    else:
        warning = low_balance_text(lang, CV_PRICE, balance, file=translation_file)
        await callback.message.edit_text(warning)
        try:
            pay_text = i18n.t("pay_select_amount", lang=lang, file="message")
        except Exception:
            pay_text = "To'lov miqdorini tanlang:"
        await callback.message.reply(pay_text, reply_markup=get_amounts_keyboard(lang))

    await callback.answer()


async def _handle_cancel(callback):
    user_id = callback.from_user.id
    lang = get_user_lang(user_id)
    try:
        cancel_text = i18n.t("payment_cancelled", lang=lang, file="message")
    except Exception:
        cancel_text = "❌ Amaliyot bekor qilindi."
    await callback.message.edit_text(cancel_text)
    await callback.answer()


@bitik.on_callback_query(filters.regex(r"^cv_proceed$"))
async def cv_proceed_callback(client, callback):
    await _handle_proceed(
        callback,
        fsm,
        lambda: cv_lang_keyboard(prefix="cv"),
        translation_file="cv",
    )


@bitik.on_callback_query(filters.regex(r"^cv_cancel$"))
async def cv_cancel_callback(client, callback):
    await _handle_cancel(callback)


@bitik.on_callback_query(filters.regex(r"^cv2_proceed$"))
async def cv2_proceed_callback(client, callback):
    await _handle_proceed(
        callback,
        anketa2_fsm,
        anketa2_lang_keyboard,
        translation_file="cv",
    )


@bitik.on_callback_query(filters.regex(r"^cv2_cancel$"))
async def cv2_cancel_callback(client, callback):
    await _handle_cancel(callback)

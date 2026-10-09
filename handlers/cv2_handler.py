import os
from pyrogram import filters
from pyrogram.errors import MessageNotModified
from bot import bitik
from services.cv2_fsm import anketa2_fsm, Anketa2State
from keyboards.cv2_xato_kb import cv2_xato_keyboard
from keyboards.cv2_davom_kb import get_cv2_davom_keyboard
from services.doc2_service import create_cv2_document
from services.pdf2_service import generate_pdf2_anketa
from services.localization import i18n
from callbacks.format_cb import universal_format_callback
from services.channel_service import enforce_subscription
from database.users_repo import get_user_lang
from core.admin import effective_balance
from services.billing import CV_PRICE


async def process_cv2_start(client, message):
    if not await enforce_subscription(client, message):
        return

    user_id = message.from_user.id
    anketa2_fsm.finish(user_id)
    lang = get_user_lang(user_id)
    balance = effective_balance(user_id)

    anketa2_fsm.update_data(user_id, "cv_lang", lang)
    anketa2_fsm.update_data(user_id, "waiting_for_format", False)

    try:
        price_tpl = i18n.t("cv2_price_info", lang=lang, file="cv")
    except Exception:
        try:
            price_tpl = i18n.t("cv2_price_info", lang=lang, file="anketa2")
        except Exception:
            price_tpl = "📄 Hujjat yaratish narxi: {price}\n💰 Sizning balansingiz: {balance}"

    text = price_tpl.format(price=f"{CV_PRICE:,.0f}", balance=f"{balance:,.0f}")
    await message.reply(text, reply_markup=get_cv2_davom_keyboard(lang))


@bitik.on_message(filters.command("create_cv2"))
async def start_anketa2(client, message):
    await process_cv2_start(client, message)


@bitik.on_callback_query(filters.regex(r"^anketa2_lang:(.*)"))
async def set_cv2_lang(client, callback):
    user_id = callback.from_user.id
    lang = callback.data.split(":")[-1]
    first = anketa2_fsm.start_flow(user_id, lang)
    if not first:
        return
    try:
        await callback.message.edit_text(i18n.t("cv_starting", lang=lang, file="message"))
    except MessageNotModified:
        pass
    try:
        q = i18n.t(anketa2_fsm.get_question_key(first), lang=lang, file="anketa2")
    except Exception:
        q = "Keyingi savol:"
    await callback.message.reply(q)
    await callback.answer()


async def check_cv2_filter(_, __, message):
    if not message or not message.from_user:
        return False
    uid = message.from_user.id
    state = anketa2_fsm.get_state(uid)
    data = anketa2_fsm.get_data(uid) or {}
    return state is not None or data.get("waiting_for_format") is True


cv2_filter = filters.create(check_cv2_filter)
anketa2_filter = cv2_filter


async def send_cv2_preview(client, message, user_id, lang):
    data = anketa2_fsm.get_data(user_id) or {}
    try:
        preview_title = i18n.t("preview_title", lang=lang, file="anketa2")
    except Exception:
        preview_title = "📋 Ma'lumotlarni tekshiring:"

    lines = [f"<b>{preview_title}</b>\n"]
    for index, state in enumerate(anketa2_fsm.QUESTIONS_FLOW, start=1):
        try:
            q_title = i18n.t(anketa2_fsm.get_question_key(state), lang=lang, file="anketa2")
        except Exception:
            q_title = state
        lines.append(f"{index}. {q_title}: {data.get(state, '-')}")

    try:
        btn_c = i18n.t("btn_confirm", lang=lang, file="anketa2")
    except Exception:
        btn_c = "✅ Tasdiqlash"
    try:
        btn_e = i18n.t("btn_edit", lang=lang, file="anketa2")
    except Exception:
        btn_e = "✏️ O'zgartirish"

    kb = cv2_xato_keyboard(btn_c, btn_e)
    photo_path = data.get("rasm")
    if photo_path and isinstance(photo_path, str) and os.path.exists(photo_path):
        await client.send_photo(chat_id=message.chat.id, photo=photo_path)
    await message.reply("\n".join(lines), reply_markup=kb)


@bitik.on_message(
    cv2_filter
    & filters.text
    & ~filters.command(["start", "create_cv", "create_cv2", "language"])
)
async def handle_cv2_inputs(client, message):
    user_id = message.from_user.id
    state = anketa2_fsm.get_state(user_id)
    data = anketa2_fsm.get_data(user_id) or {}
    lang = data.get("cv_lang", "uz")

    if data.get("waiting_for_format"):
        try:
            w = i18n.t("warning_choose_format", lang=lang, file="anketa2")
        except Exception:
            w = "Iltimos, formatni tanlang!"
        await message.reply(w)
        return

    if state in anketa2_fsm.QUESTIONS_FLOW:
        if not message.text:
            try:
                w = i18n.t("warning_text_required", lang=lang, file="anketa2")
            except Exception:
                w = "Iltimos, matn ko'rinishida kiriting!"
            await message.reply(w)
            return

        next_state = anketa2_fsm.process_answer(user_id, message.text)
        if next_state:
            try:
                q = i18n.t(anketa2_fsm.get_question_key(next_state), lang=lang, file="anketa2")
            except Exception:
                q = "Keyingi ma'lumotni kiriting:"
            await message.reply(q)
        else:
            anketa2_fsm.set_state(user_id, Anketa2State.RASM)
            try:
                ask = i18n.t(f"ask_{Anketa2State.RASM}", lang=lang, file="anketa2")
            except Exception:
                ask = "Iltimos, rasmingizni yuboring:"
            await message.reply(ask)


@bitik.on_callback_query(filters.regex(r"^anketa2_format_(pdf|docx)$"))
async def format_cv2_callback(client, callback):
    await universal_format_callback(
        client=client,
        callback=callback,
        prefix="cv2",
        translation_file="anketa2",
        doc_func=create_cv2_document,
        pdf_func=generate_pdf2_anketa,
        fsm_service=anketa2_fsm,
    )

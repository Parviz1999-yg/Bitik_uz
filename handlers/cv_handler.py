import os
from pyrogram import filters
from pyrogram.errors import MessageNotModified
from bot import bitik
from services.cv_fsm import fsm, CVState
from keyboards.relative_kb import get_relatives_keyboard
from keyboards.cv_xato_kb import cv_xato_keyboard
from keyboards.cv_davom_kb import get_cv_davom_keyboard
from services.doc_service import create_cv_document
from services.pdf_service import generate_pdf_anketa
from services.localization import i18n
from callbacks.relative_cb import handle_relative_callback
from callbacks.format_cb import universal_format_callback
from services.channel_service import enforce_subscription
from database.users_repo import get_user_lang
from core.admin import effective_balance
from services.billing import CV_PRICE, can_afford


async def process_cv_start(client, message):
    if not await enforce_subscription(client, message):
        return

    user_id = message.from_user.id
    fsm.finish(user_id)
    lang = get_user_lang(user_id)
    balance = effective_balance(user_id)

    fsm.update_data(user_id, "cv_lang", lang)
    fsm.update_data(user_id, "waiting_for_format", False)

    try:
        price_tpl = i18n.t("cv2_price_info", lang=lang, file="cv")
    except Exception:
        price_tpl = i18n.t("cv2_price_info", lang=lang, file="anketa2")

    text = price_tpl.format(price=f"{CV_PRICE:,.0f}", balance=f"{balance:,.0f}")
    await message.reply(text, reply_markup=get_cv_davom_keyboard(lang))


@bitik.on_message(filters.command("create_cv"))
async def start_cv(client, message):
    await process_cv_start(client, message)


@bitik.on_callback_query(filters.regex(r"^cv_lang:(.*)"))
async def set_cv_lang(client, callback):
    user_id = callback.from_user.id
    lang = callback.data.split(":")[-1]
    first = fsm.start_flow(user_id, lang)
    if not first:
        return
    try:
        await callback.message.edit_text(i18n.t("cv_starting", lang=lang, file="message"))
    except MessageNotModified:
        pass
    await callback.message.reply(i18n.t(fsm.get_question_key(first), lang=lang, file="cv"))
    await callback.answer()


async def check_cv_filter(_, __, message):
    if not message or not message.from_user:
        return False
    uid = message.from_user.id
    state = fsm.get_state(uid)
    data = fsm.get_data(uid) or {}
    return state is not None or data.get("waiting_for_format") is True


cv_filter = filters.create(check_cv_filter)


async def send_cv_preview(client, message, user_id, lang):
    data = fsm.get_data(user_id) or {}
    preview_title = i18n.t("preview_title", lang=lang, file="cv")
    lines = [f"📋 <b>{preview_title}</b>\n"]

    for index, state in enumerate(fsm.QUESTIONS_FLOW, start=1):
        q_title = i18n.t(fsm.get_question_key(state), lang=lang, file="cv")
        if state == CVState.QARINDOSHLAR:
            relatives = data.get("qarindoshlar_list") or data.get(CVState.QARINDOSHLAR) or []
            if relatives and isinstance(relatives, list):
                formatted = []
                for q in relatives:
                    if isinstance(q, dict):
                        formatted.append(
                            f"{q.get('qarindosh', '')}: {q.get('qarindosh_ism', '')}, "
                            f"{q.get('qatr_ty_tj', '')}, {q.get('qarin_kasb', '')}, {q.get('qar_manzil', '')}"
                        )
                    else:
                        formatted.append(str(q))
                user_value = "\n    " + "\n    ".join(f"- {i}" for i in formatted)
            else:
                user_value = "-"
        else:
            user_value = data.get(state, "-")
        lines.append(f"{index}. {q_title}: {user_value}")

    kb = cv_xato_keyboard(
        i18n.t("btn_confirm", lang=lang, file="cv"),
        i18n.t("btn_edit", lang=lang, file="cv"),
    )
    photo_path = data.get("rasm")
    if photo_path and isinstance(photo_path, str) and os.path.exists(photo_path):
        await client.send_photo(chat_id=message.chat.id, photo=photo_path)
    await message.reply("\n".join(lines), reply_markup=kb)


@bitik.on_message(
    cv_filter
    & filters.text
    & ~filters.command(["start", "create_cv", "create_cv2", "language"])
)
async def handle_cv_inputs(client, message):
    user_id = message.from_user.id
    state = fsm.get_state(user_id)
    data = fsm.get_data(user_id) or {}
    lang = data.get("cv_lang", "uz")

    if data.get("waiting_for_format"):
        await message.reply(i18n.t("warning_choose_format", lang=lang, file="cv"))
        return

    if state == CVState.QARINDOSHLAR:
        if not fsm.is_add_button_pressed(user_id):
            await message.reply(i18n.t("warning_press_add_more", lang=lang, file="cv"))
            return
        if not message.text:
            await message.reply("Iltimos, matn ko'rinishida kiriting!")
            return

        parts = [p.strip() for p in message.text.strip().split(",")]
        rel_dict = {
            "qarindosh": parts[0] if parts else message.text.strip(),
            "qarindosh_ism": parts[1] if len(parts) > 1 else "-",
            "qatr_ty_tj": parts[2] if len(parts) > 2 else "-",
            "qarin_kasb": parts[3] if len(parts) > 3 else "-",
            "qar_manzil": parts[4] if len(parts) > 4 else "-",
        }
        lst = data.get("qarindoshlar_list", [])
        lst.append(rel_dict)
        fsm.update_data(user_id, "qarindoshlar_list", lst)
        fsm.add_data_to_list(user_id, CVState.QARINDOSHLAR, message.text.strip())
        fsm.set_add_button_pressed(user_id, False)
        await message.reply(
            f"{i18n.t('relative_saved', lang=lang, file='cv')}\n\n"
            f"{i18n.t('ask_add_more', lang=lang, file='cv')}",
            reply_markup=get_relatives_keyboard(lang=lang),
        )
        return

    if state in fsm.QUESTIONS_FLOW:
        if not message.text:
            await message.reply("Iltimos, matn ko'rinishida kiriting!")
            return
        next_state = fsm.process_answer(user_id, message.text)
        if next_state:
            await message.reply(i18n.t(fsm.get_question_key(next_state), lang=lang, file="cv"))
        else:
            fsm.set_state(user_id, CVState.RASM)
            await message.reply(i18n.t(f"ask_{CVState.RASM}", lang=lang, file="cv"))


@bitik.on_callback_query(filters.regex(r"^(add_more_rel|finish_rel)$"))
async def rel_callback_handler(client, callback):
    await handle_relative_callback(client, callback)


@bitik.on_callback_query(filters.regex(r"^cv_format_(pdf|docx)$"))
async def format_cv_callback(client, callback):
    if not can_afford(callback.from_user.id):
        await callback.answer(
            "⚠️ Balansingiz yetarli emas! Iltimos, hisobingizni to'ldiring.",
            show_alert=True,
        )
        return
    await universal_format_callback(
        client=client,
        callback=callback,
        prefix="cv",
        translation_file="cv",
        doc_func=create_cv_document,
        pdf_func=generate_pdf_anketa,
        fsm_service=fsm,
    )

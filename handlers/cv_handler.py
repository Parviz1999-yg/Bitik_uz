# handlers/cv_handler.py
import os
from pyrogram import filters
from pyrogram.errors import MessageNotModified
from bot import bitik
import config  # <--- Admin ID uchun config import qilindi[cite: 5]
from services.cv_fsm import fsm, CVState
from keyboards.relative_kb import get_relatives_keyboard
from keyboards.cv_kb import cv_lang_keyboard
from keyboards.cv_xato_kb import cv_xato_keyboard
from keyboards.cv_davom_kb import get_cv_davom_keyboard
from keyboards.payment_kb import get_amounts_keyboard
from services.doc_service import create_cv_document
from services.pdf_service import generate_pdf_anketa
from services.localization import i18n
from callbacks.relative_cb import handle_relative_callback
from callbacks.format_cb import universal_format_callback
from services.channel_service import enforce_subscription
from database.users_repo import get_user_lang, get_user_balance, update_balance

CV_PRICE = 5000  # Ma'lumotnoma yaratish narxi (5 000 so'm)

# --- MA'LUMOTNOMA YARATISH BOSHLASH (Umumiy funksiya) ---
async def process_cv_start(client, message):
    if not await enforce_subscription(client, message):
        return

    user_id = message.from_user.id
    fsm.finish(user_id) 
    
    lang = get_user_lang(user_id)
    
    # 👑 ADMIN UCHUN BALANSNI CHEKSIZ QILIB KO'RSATISH
    if user_id == config.ADMIN_ID:
        balance = 999999999.0
    else:
        balance = get_user_balance(user_id)
    
    fsm.update_data(user_id, "cv_lang", lang)
    fsm.update_data(user_id, "waiting_for_format", False) 
    
    try:
        price_text_template = i18n.t("cv2_price_info", lang=lang, file="cv")
    except:
        price_text_template = i18n.t("cv2_price_info", lang=lang, file="anketa2")

    text = price_text_template.format(
        price=f"{CV_PRICE:,.0f}",
        balance=f"{balance:,.0f}"
    )
    
    await message.reply(text, reply_markup=get_cv_davom_keyboard(lang))

@bitik.on_message(filters.command("create_cv"))
async def start_cv(client, message):
    await process_cv_start(client, message)

@bitik.on_message(filters.command("create_cv2"))
async def start_cv2_pricing(client, message):
    await process_cv_start(client, message)


# --- TILNI TANLASH CALLBACK'I ---
@bitik.on_callback_query(filters.regex(r"^cv_lang:(.*)"))
async def set_cv_lang(client, callback):
    user_id = callback.from_user.id
    lang = callback.data.split(":")[-1]
    
    fsm.update_data(user_id, "cv_lang", lang)
    fsm.update_data(user_id, "waiting_for_format", False)
    
    flow = fsm.QUESTIONS_FLOW
    if not flow:
        return
        
    first_state = flow[0]
    fsm.set_state(user_id, first_state)
    
    try:
        await callback.message.edit_text(i18n.t("cv_starting", lang=lang, file="message"))
    except MessageNotModified:
        pass
    
    key = fsm.get_question_key(first_state)
    await callback.message.reply(i18n.t(key, lang=lang, file="cv"))
    await callback.answer()


# --- FSM FILTER ---
async def check_cv_filter(_, __, message):
    if not message or not message.from_user:
        return False
    user_id = message.from_user.id
    state = fsm.get_state(user_id)
    data = fsm.get_data(user_id) or {}
    return state is not None or data.get("waiting_for_format") == True

cv_filter = filters.create(check_cv_filter)


# --- PREVIEW (TEKSHIRUV) FUNKSIYASI ---
async def send_cv_preview(client, message, user_id, lang):
    data = fsm.get_data(user_id) or {}
    
    preview_title = i18n.t('preview_title', lang=lang, file='cv')
    text_lines = [f"📋 <b>{preview_title}</b>\n"]
    
    for index, state in enumerate(fsm.QUESTIONS_FLOW, start=1):
        question_key = fsm.get_question_key(state)
        question_title = i18n.t(question_key, lang=lang, file='cv')
        
        if state == CVState.QARINDOSHLAR:
            relatives = data.get("qarindoshlar_list") or data.get(CVState.QARINDOSHLAR) or []
            if relatives and isinstance(relatives, list):
                formatted_list = []
                for q in relatives:
                    if isinstance(q, dict):
                        q_str = f"{q.get('qarindosh', '')}: {q.get('qarindosh_ism', '')}, {q.get('qatr_ty_tj', '')}, {q.get('qarin_kasb', '')}, {q.get('qar_manzil', '')}"
                        formatted_list.append(q_str)
                    else:
                        formatted_list.append(str(q))
                user_value = "\n    " + "\n    ".join([f"- {item}" for item in formatted_list])
            else:
                user_value = "-"
        else:
            user_value = data.get(state, '-')
        
        text_lines.append(f"{index}. {question_title}: {user_value}")
    
    text = "\n".join(text_lines)
    
    btn_confirm = i18n.t("btn_confirm", lang=lang, file="cv")
    btn_edit = i18n.t("btn_edit", lang=lang, file="cv")
    
    keyboard = cv_xato_keyboard(btn_confirm, btn_edit)
    
    photo_path = data.get("rasm")
    
    if photo_path and isinstance(photo_path, str) and os.path.exists(photo_path):
        await client.send_photo(chat_id=message.chat.id, photo=photo_path)
    
    await message.reply(text, reply_markup=keyboard)


# --- MATNLI XABARLARNI QABUL QILISH ---
@bitik.on_message(cv_filter & filters.text & ~filters.command(["start", "create_cv", "create_cv2", "language"]))
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
            warning_msg = "Iltimos, matn ko'rinishida kiriting!"
            await message.reply(warning_msg)
            return

        text_input = message.text.strip()
        parts = [p.strip() for p in text_input.split("|")]
        
        rel_dict = {
            "qarindosh": parts[0] if len(parts) > 0 else text_input,
            "qarindosh_ism": parts[1] if len(parts) > 1 else "-",
            "qatr_ty_tj": parts[2] if len(parts) > 2 else "-",
            "qarin_kasb": parts[3] if len(parts) > 3 else "-",
            "qar_manzil": parts[4] if len(parts) > 4 else "-"
        }

        qarindoshlar_list = data.get("qarindoshlar_list", [])
        qarindoshlar_list.append(rel_dict)
        fsm.update_data(user_id, "qarindoshlar_list", qarindoshlar_list)
        fsm.add_data_to_list(user_id, CVState.QARINDOSHLAR, text_input)
        fsm.set_add_button_pressed(user_id, False)
        
        success_text = i18n.t("relative_saved", lang=lang, file="cv")
        ask_more_text = i18n.t("ask_add_more", lang=lang, file="cv")
        
        await message.reply(
            f"{success_text}\n\n{ask_more_text}", 
            reply_markup=get_relatives_keyboard(lang=lang)
        )
        return

    flow = fsm.QUESTIONS_FLOW
    if state in flow:
        if not message.text:
            warning_msg = "Iltimos, matn ko'rinishida kiriting!"
            await message.reply(warning_msg)
            return

        current_index = flow.index(state)
        next_index = current_index + 1
        
        fsm.update_data(user_id, state, message.text)
        
        if next_index < len(flow):
            next_state = flow[next_index]
            fsm.set_state(user_id, next_state)
            
            key = fsm.get_question_key(next_state)
            await message.reply(i18n.t(key, lang=lang, file="cv"))
        else:
            fsm.set_state(user_id, CVState.RASM)
            await message.reply(i18n.t(f"ask_{CVState.RASM}", lang=lang, file="cv"))


# --- CALLBACK ROUTERS ---
@bitik.on_callback_query(filters.regex(r"^(add_more_rel|finish_rel)$"))
async def rel_callback_handler(client, callback):
    await handle_relative_callback(client, callback)


# --- FORMAT TANLANGANDA ISHGA TUSHUVCHI HANDLER (Admin uchun balans tekshiruvisiz) ---
@bitik.on_callback_query(filters.regex(r"^cv_format_(pdf|docx)$"))
async def format_cv_callback(client, callback):
    user_id = callback.from_user.id
    
    # 👑 AGAR ADMIN BO'LSA - BALANS TEKSHIRILMAYDI VA PUL YECHILMAYDI
    if user_id != config.ADMIN_ID:
        balance = get_user_balance(user_id)
        if balance < CV_PRICE:
            await callback.answer("⚠️ Balansingiz yetarli emas! Iltimos, hisobingizni to'ldiring.", show_alert=True)
            return

    await universal_format_callback(
        client=client,
        callback=callback,
        prefix="cv",
        translation_file="cv",
        doc_func=create_cv_document,
        pdf_func=generate_pdf_anketa,
        fsm_service=fsm
    )
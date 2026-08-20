# handlers/cv2_handler.py
import os
from pyrogram import filters
from pyrogram.errors import MessageNotModified
from bot import bitik
import config  # <--- Admin ID uchun config import qilindi[cite: 8]
from services.cv2_fsm import anketa2_fsm, Anketa2State
from keyboards.cv2_kb import anketa2_lang_keyboard
from keyboards.cv2_xato_kb import cv2_xato_keyboard
from keyboards.cv2_davom_kb import get_cv2_davom_keyboard
from keyboards.payment_kb import get_amounts_keyboard
from services.doc2_service import create_cv2_document
from services.pdf2_service import generate_pdf2_anketa
from services.localization import i18n
from callbacks.format2_cb import universal_format2_callback  # <--- FORMAT2_CB DAN IMPORT QILINDI[cite: 8]
from services.channel_service import enforce_subscription
from database.users_repo import get_user_lang, get_user_balance, update_balance

CV_PRICE = 5000  # 2-anketa yaratish narxi (5 000 so'm)[cite: 8]

# --- 2-ANKETA YARATISHNI BOSHLASH (Umumiy funksiya) ---
async def process_cv2_start(client, message):
    if not await enforce_subscription(client, message):
        return

    user_id = message.from_user.id
    anketa2_fsm.finish(user_id) 
    
    lang = get_user_lang(user_id)
    
    # 👑 ADMIN UCHUN BALANSNI CHEKSIZ QILIB KO'RSATISH[cite: 8]
    if user_id == config.ADMIN_ID:
        balance = 999999999.0
    else:
        balance = get_user_balance(user_id)
    
    anketa2_fsm.update_data(user_id, "cv_lang", lang)
    anketa2_fsm.update_data(user_id, "waiting_for_format", False) 
    
    try:
        price_text_template = i18n.t("cv2_price_info", lang=lang, file="cv")
    except:
        try:
            price_text_template = i18n.t("cv2_price_info", lang=lang, file="anketa2")
        except:
            price_text_template = "📄 Hujjat yaratish narxi: {price}\n💰 Sizning balansingiz: {balance}"

    text = price_text_template.format(
        price=f"{CV_PRICE:,.0f}",
        balance=f"{balance:,.0f}"
    )
    
    await message.reply(text, reply_markup=get_cv2_davom_keyboard(lang))

@bitik.on_message(filters.command("create_cv2"))
async def start_anketa2(client, message):
    await process_cv2_start(client, message)


# --- TILNI TANLASH CALLBACK'I ---
@bitik.on_callback_query(filters.regex(r"^anketa2_lang:(.*)"))
async def set_cv2_lang(client, callback):
    user_id = callback.from_user.id
    lang = callback.data.split(":")[-1]
    
    anketa2_fsm.update_data(user_id, "cv_lang", lang)
    anketa2_fsm.update_data(user_id, "waiting_for_format", False)
    
    flow = anketa2_fsm.QUESTIONS_FLOW
    if not flow:
        return
        
    first_state = flow[0]
    anketa2_fsm.set_state(user_id, first_state)
    
    try:
        await callback.message.edit_text(i18n.t("cv_starting", lang=lang, file="message"))
    except MessageNotModified:
        pass
    
    try:
        question_text = i18n.t(anketa2_fsm.get_question_key(first_state), lang=lang, file="anketa2")
    except:
        question_text = "Keyingi savol:"

    await callback.message.reply(question_text)
    await callback.answer()


# --- FSM FILTER ---
async def check_cv2_filter(_, __, message):
    if not message or not message.from_user:
        return False
    user_id = message.from_user.id
    state = anketa2_fsm.get_state(user_id)
    data = anketa2_fsm.get_data(user_id) or {}
    return state is not None or data.get("waiting_for_format") == True

cv2_filter = filters.create(check_cv2_filter)
anketa2_filter = cv2_filter

# --- PREVIEW (TEKSHIRUV) FUNKSIYASI ---
async def send_cv2_preview(client, message, user_id, lang):
    data = anketa2_fsm.get_data(user_id) or {}
    
    try:
        preview_title = i18n.t('preview_title', lang=lang, file='anketa2')
    except:
        preview_title = "📋 Ma'lumotlarni tekshiring:"
        
    text_lines = [f"<b>{preview_title}</b>\n"]
    
    for index, state in enumerate(anketa2_fsm.QUESTIONS_FLOW, start=1):
        question_key = anketa2_fsm.get_question_key(state)
        try:
            question_title = i18n.t(question_key, lang=lang, file='anketa2')
        except:
            question_title = state
            
        user_value = data.get(state, '-')
        text_lines.append(f"{index}. {question_title}: {user_value}")
    
    text = "\n".join(text_lines)
    
    try:
        btn_confirm = i18n.t("btn_confirm", lang=lang, file="anketa2")
    except:
        btn_confirm = "✅ Tasdiqlash"
        
    try:
        btn_edit = i18n.t("btn_edit", lang=lang, file="anketa2")
    except:
        btn_edit = "✏️ O'zgartirish"
    
    keyboard = cv2_xato_keyboard(btn_confirm, btn_edit)
    
    photo_path = data.get("rasm")
    if photo_path and isinstance(photo_path, str) and os.path.exists(photo_path):
        await client.send_photo(chat_id=message.chat.id, photo=photo_path)
    
    await message.reply(text, reply_markup=keyboard)


# --- MATNLI XABARLARNI QABUL QILISH ---
@bitik.on_message(cv2_filter & filters.text & ~filters.command(["start", "create_cv", "create_cv2", "language"]))
async def handle_cv2_inputs(client, message):
    user_id = message.from_user.id
    state = anketa2_fsm.get_state(user_id)
    data = anketa2_fsm.get_data(user_id) or {}
    lang = data.get("cv_lang", "uz")

    if data.get("waiting_for_format"):
        try:
            warning_msg = i18n.t("warning_choose_format", lang=lang, file="anketa2")
        except:
            warning_msg = "Iltimos, formatni tanlang!"
        await message.reply(warning_msg)
        return

    flow = anketa2_fsm.QUESTIONS_FLOW
    if state in flow:
        if not message.text:
            try:
                warning_msg = i18n.t("warning_text_required", lang=lang, file="anketa2")
            except:
                warning_msg = "Iltimos, matn ko'rinishida kiriting!"
            await message.reply(warning_msg)
            return

        current_index = flow.index(state)
        next_index = current_index + 1
        
        anketa2_fsm.update_data(user_id, state, message.text)
        
        if next_index < len(flow):
            next_state = flow[next_index]
            anketa2_fsm.set_state(user_id, next_state)
            
            key = anketa2_fsm.get_question_key(next_state)
            try:
                next_q_text = i18n.t(key, lang=lang, file="anketa2")
            except:
                next_q_text = "Keyingi ma'lumotni kiriting:"
            await message.reply(next_q_text)
        else:
            anketa2_fsm.set_state(user_id, Anketa2State.RASM)
            ask_rasm_key = f"ask_{Anketa2State.RASM}"
            
            try:
                ask_rasm_text = i18n.t(ask_rasm_key, lang=lang, file="anketa2")
            except:
                ask_rasm_text = "Iltimos, rasmingizni yuboring:"
                
            await message.reply(ask_rasm_text)


# --- FORMAT TANLANGANDA ISHGA TUSHUVCHI HANDLER (format2_cb.py dan foydalanadi) ---[cite: 8]
@bitik.on_callback_query(filters.regex(r"^anketa2_format_(pdf|docx)$"))
async def format_cv2_callback(client, callback):
    await universal_format2_callback(
        client=client,
        callback=callback,
        prefix="cv2",
        translation_file="anketa2",
        doc_func=create_cv2_document,
        pdf_func=generate_pdf2_anketa,
        fsm_service=anketa2_fsm
    )
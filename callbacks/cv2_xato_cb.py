# callbacks/cv2_xato_cb.py
from pyrogram import filters
from bot import bitik
import config
from services.cv2_fsm import anketa2_fsm, Anketa2State
from keyboards.cv2_kb import anketa2_lang_keyboard
from keyboards.cv2_xato_kb import cv2_xato_keyboard
from keyboards.payment_kb import get_amounts_keyboard
from keyboards.format2_kb import get_format2_keyboard
from services.localization import i18n
from database.users_repo import get_user_lang, get_user_balance

CV_PRICE = 5000  # Ma'lumotnoma yaratish narxi

# --- DAVOM ETISH CALLBACK'I ---
@bitik.on_callback_query(filters.regex(r"^cv2_proceed$"))
async def cv2_proceed_callback(client, callback):
    user_id = callback.from_user.id
    lang = get_user_lang(user_id)
    
    # 👑 ADMIN UCHUN BALANSNI CHEKSIZ QILIB OLISH
    if user_id == config.ADMIN_ID:
        balance = 999999999.0
    else:
        balance = get_user_balance(user_id)
    
    if balance >= CV_PRICE:
        anketa2_fsm.update_data(user_id, "cv_lang", lang)
        anketa2_fsm.update_data(user_id, "waiting_for_format", False)
        
        text = i18n.t("select_cv_language", lang=lang, file="message")
        try:
            success_msg = i18n.t("cv2_balance_enough", lang=lang, file="cv")
        except:
            success_msg = "✅ Balansingiz yetarli. Davom etamiz!"
        
        await callback.message.edit_text(success_msg)
        await callback.message.reply(text, reply_markup=anketa2_lang_keyboard())
    else:
        try:
            warning_text = i18n.t("cv2_balance_low", lang=lang, file="cv").format(
                price=f"{CV_PRICE:,.0f}",
                balance=f"{balance:,.0f}"
            )
        except:
            warning_text = f"⚠️ Balansingiz yetarli emas! Kerakli summa: {CV_PRICE:,.0f} so'm, Sizda: {balance:,.0f} so'm."
            
        await callback.message.edit_text(warning_text)
        try:
            pay_select_text = i18n.t("pay_select_amount", lang=lang, file="message")
        except:
            pay_select_text = "To'lov miqdorini tanlang:"
            
        await callback.message.reply(
            pay_select_text,
            reply_markup=get_amounts_keyboard(lang)
        )
        
    await callback.answer()


# --- BEKOR QILISH CALLBACK'I ---
@bitik.on_callback_query(filters.regex(r"^cv2_cancel$"))
async def cv2_cancel_callback(client, callback):
    user_id = callback.from_user.id
    lang = get_user_lang(user_id)
    
    try:
        cancel_text = i18n.t("payment_cancelled", lang=lang, file="message")
    except:
        cancel_text = "❌ Amaliyot bekor qilindi."
    
    await callback.message.edit_text(cancel_text)
    await callback.answer()


# --- TASDIQLASH (YES) CALLBACK'I (cv2_xato_kb uchun) ---
@bitik.on_callback_query(filters.regex(r"^anketa2_confirm_yes$"))
async def anketa2_confirm_yes_callback(client, callback):
    user_id = callback.from_user.id
    lang = get_user_lang(user_id)
    
    # Balansni tekshirish
    if user_id == config.ADMIN_ID:
        balance = 999999999.0
    else:
        balance = get_user_balance(user_id)
        
    if balance >= CV_PRICE:
        # Ma'lumotlar tasdiqlandi, endi format tanlashga o'tamiz
        anketa2_fsm.update_data(user_id, "waiting_for_format", True)
        
        try:
            format_text = i18n.t("select_format", lang=lang, file="anketa2")
        except:
            format_text = "📄 Hujjat formatini tanlang:"
            
        try:
            success_msg = i18n.t("cv2_balance_enough", lang=lang, file="cv")
        except:
            success_msg = "✅ Ma'lumotlar tasdiqlandi!"
            
        await callback.message.edit_text(success_msg)
        
        # Format tanlash tugmalarini chiqaramiz
        try:
            kb = get_format2_keyboard("anketa2")[cite: 4]
        except:
            kb = None
            
        await callback.message.reply(format_text, reply_markup=kb)
    else:
        warning_text = f"⚠️ Balansingiz yetarli emas! Kerakli summa: {CV_PRICE:,.0f} so'm."
        await callback.message.edit_text(warning_text)
        try:
            pay_select_text = i18n.t("pay_select_amount", lang=lang, file="message")
        except:
            pay_select_text = "To'lov miqdorini tanlang:"
        await callback.message.reply(
            pay_select_text,
            reply_markup=get_amounts_keyboard(lang)
        )
    await callback.answer()


# --- TAHRIRLASH (EDIT) CALLBACK'I (cv2_xato_kb uchun) ---
@bitik.on_callback_query(filters.regex(r"^anketa2_confirm_edit$"))
async def anketa2_confirm_edit_callback(client, callback):
    user_id = callback.from_user.id
    lang = get_user_lang(user_id)
    
    flow = anketa2_fsm.QUESTIONS_FLOW
    if flow:
        first_state = flow[0]
        anketa2_fsm.set_state(user_id, first_state)
        anketa2_fsm.update_data(user_id, "waiting_for_format", False)
        
        try:
            edit_start_text = i18n.t("edit_started", lang=lang, file="anketa2")
        except:
            edit_start_text = "🔄 Ma'lumotlarni qaytadan tahrirlash boshlandi."
            
        await callback.message.edit_text(edit_start_text)
        
        try:
            first_q_text = i18n.t(anketa2_fsm.get_question_key(first_state), lang=lang, file="anketa2")
        except:
            first_q_text = "Birinchi ma'lumotni kiriting:"
            
        await callback.message.reply(first_q_text)
    
    await callback.answer()
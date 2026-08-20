# callbacks/format_cb.py
import os
from pyrogram.errors import MessageNotModified
import config  # <--- Config import qilindi
from services.localization import i18n
from database.users_repo import get_user_balance, update_balance
from keyboards.payment_kb import get_amounts_keyboard

CV_PRICE = 5000  # Standart narx (agar har xil bo'lsa, buni parametr sifatida ham berish mumkin)

async def universal_format_callback(client, callback, prefix, translation_file, doc_func, pdf_func, fsm_service):
    user_id = callback.from_user.id
    
    # 👑 ADMIN UCHUN BALANSNI CHEKSIZ QILIB OLISH
    if user_id == config.ADMIN_ID:
        balance = 999999999.0
    else:
        balance = get_user_balance(user_id)
    
    format_type = callback.data.split("_")[-1]  # pdf yoki docx
    
    # 1. Balansni tekshiramiz
    if balance < CV_PRICE:
        lang = user_data = fsm_service.get_data(user_id).get("cv_lang", "uz") if fsm_service.get_data(user_id) else "uz"
        try:
            warning_text = i18n.t("cv2_balance_low", lang=lang, file=translation_file).format(
                price=f"{CV_PRICE:,.0f}",
                balance=f"{balance:,.0f}"
            )
        except:
            warning_text = f"❌ Balansingiz yetarli emas!\nKerakli summa: {CV_PRICE:,.0f} so'm\nJoriy balans: {balance:,.0f} so'm"
            
        await callback.message.edit_text(warning_text)
        await callback.message.reply(
            i18n.t("pay_select_amount", lang=lang, file="message"),
            reply_markup=get_amounts_keyboard(lang)
        )
        await callback.answer()
        return

    # 2. Balansdan pul yechish (Faqat oddiy foydalanuvchilar uchun)
    if user_id != config.ADMIN_ID:
        update_balance(user_id, -CV_PRICE)
        
    await callback.answer()
    
    fsm_service.update_data(user_id, "waiting_for_format", False)
    
    user_data = fsm_service.get_data(user_id) or {}
    lang = user_data.get("cv_lang", "uz")
    user_data["user_id"] = user_id
    
    processing_key = f"processing_{format_type}"
    success_key = f"success_{format_type}"
    
    try:
        if format_type == "pdf":
            await callback.message.edit_text(i18n.t(processing_key, lang=lang, file=translation_file))
            
            output_path = f"downloads/{prefix}_{user_id}.pdf"
            success = pdf_func(data=user_data, lang=lang, output_pdf_path=output_path)
            
            if success and os.path.exists(output_path):
                await callback.message.reply_document(output_path, caption=i18n.t(success_key, lang=lang, file=translation_file))
                os.remove(output_path)
            else:
                await callback.message.edit_text(i18n.t("error_text", lang=lang, file=translation_file))
                
        else:
            await callback.message.edit_text(i18n.t("processing_docx", lang=lang, file=translation_file))
            
            output_path = doc_func(data=user_data, lang=lang)
            
            if output_path and os.path.exists(output_path):
                await callback.message.reply_document(output_path, caption=i18n.t("success_docx", lang=lang, file=translation_file))
                os.remove(output_path)
            else:
                await callback.message.edit_text(i18n.t("error_text", lang=lang, file=translation_file))
                
    except MessageNotModified:
        pass
    except Exception as e:
        print(f"Hujjat yaratishda xatolik ({prefix}): {e}")
    finally:
        fsm_service.finish(user_id)
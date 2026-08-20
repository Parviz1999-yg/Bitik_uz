# callbacks/format2_cb.py
import os
from pyrogram.errors import MessageNotModified
from services.localization import i18n
from database.users_repo import get_user_balance, update_balance
from keyboards.payment_kb import get_amounts_keyboard

CV_PRICE = 5000  # 2-anketa uchun narx

async def universal_format2_callback(client, callback, prefix, translation_file, doc_func, pdf_func, fsm_service):
    user_id = callback.from_user.id
    
    # Xavfsiz tarzda foydalanuvchi tilini va balansini aniqlaymiz
    user_data = fsm_service.get_data(user_id) or {}
    lang = user_data.get("cv_lang", "uz")
    balance = get_user_balance(user_id)
    
    format_type = callback.data.split("_")[-1]  # pdf yoki docx
    
    # 1. Balansni tekshiramiz
    if balance < CV_PRICE:
        try:
            warning_text = i18n.t("cv2_balance_low", lang=lang, file=translation_file).format(
                price=f"{CV_PRICE:,.0f}",
                balance=f"{balance:,.0f}"
            )
        except:
            warning_text = f"❌ Balansingiz yetarli emas!\nKerakli summa: {CV_PRICE:,.0f} so'm\nJoriy balans: {balance:,.0f} so'm"
            
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
        return

    # 2. Balansdan 5000 so'm yechib olamiz
    update_balance(user_id, -CV_PRICE)
    await callback.answer()
    
    fsm_service.update_data(user_id, "waiting_for_format", False)
    
    user_data["user_id"] = user_id
    
    processing_key = f"processing_{format_type}"
    success_key = f"success_{format_type}"
    
    try:
        if format_type == "pdf":
            try:
                proc_text = i18n.t(processing_key, lang=lang, file=translation_file)
            except:
                proc_text = "Hujjat tayyorlanmoqda..."
            await callback.message.edit_text(proc_text)
            
            output_path = f"downloads/{prefix}_{user_id}.pdf"
            success = pdf_func(data=user_data, lang=lang, output_pdf_path=output_path)
            
            if success and os.path.exists(output_path):
                try:
                    succ_text = i18n.t(success_key, lang=lang, file=translation_file)
                except:
                    succ_text = "Mana sizning hujjatingiz:"
                await callback.message.reply_document(output_path, caption=succ_text)
                os.remove(output_path)
            else:
                try:
                    err_text = i18n.t("error_text", lang=lang, file=translation_file)
                except:
                    err_text = "Xatolik yuz berdi."
                await callback.message.edit_text(err_text)
                
        else:
            try:
                proc_docx_text = i18n.t("processing_docx", lang=lang, file=translation_file)
            except:
                proc_docx_text = "Word hujjati tayyorlanmoqda..."
            await callback.message.edit_text(proc_docx_text)
            
            output_path = doc_func(data=user_data, lang=lang)
            
            if output_path and os.path.exists(output_path):
                try:
                    succ_docx_text = i18n.t("success_docx", lang=lang, file=translation_file)
                except:
                    succ_docx_text = "Mana sizning hujjatingiz:"
                await callback.message.reply_document(output_path, caption=succ_docx_text)
                os.remove(output_path)
            else:
                try:
                    err_text = i18n.t("error_text", lang=lang, file=translation_file)
                except:
                    err_text = "Xatolik yuz berdi."
                await callback.message.edit_text(err_text)
                
    except MessageNotModified:
        pass
    except Exception as e:
        print(f"Hujjat yaratishda xatolik ({prefix}): {e}")
    finally:
        fsm_service.finish(user_id)
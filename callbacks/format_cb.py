"""CV va Anketa2 uchun yagona format (pdf/docx) callback."""
import os
from pyrogram.errors import MessageNotModified

from services.billing import CV_PRICE, can_afford, charge_user, low_balance_text
from services.localization import i18n
from keyboards.payment_kb import get_amounts_keyboard
from core.admin import effective_balance


async def universal_format_callback(
    client,
    callback,
    prefix: str,
    translation_file: str,
    doc_func,
    pdf_func,
    fsm_service,
):
    user_id = callback.from_user.id
    user_data = fsm_service.get_data(user_id) or {}
    lang = user_data.get("cv_lang", "uz")
    balance = effective_balance(user_id)

    # callback data: cv_format_pdf | anketa2_format_docx | ...
    raw = callback.data or ""
    if "format_" in raw:
        format_type = raw.split("format_")[-1]
    else:
        format_type = raw.split("_")[-1]

    if not can_afford(user_id):
        warning = low_balance_text(lang, CV_PRICE, balance, file=translation_file)
        await callback.message.edit_text(warning)
        try:
            pay_text = i18n.t("pay_select_amount", lang=lang, file="message")
        except Exception:
            pay_text = "To'lov miqdorini tanlang:"
        await callback.message.reply(pay_text, reply_markup=get_amounts_keyboard(lang))
        await callback.answer()
        return

    ok, _ = charge_user(user_id)
    if not ok:
        await callback.answer("⚠️ Balans yetarli emas!", show_alert=True)
        return

    await callback.answer()
    fsm_service.update_data(user_id, "waiting_for_format", False)
    user_data = fsm_service.get_data(user_id) or {}
    user_data["user_id"] = user_id
    lang = user_data.get("cv_lang", "uz")

    def _t(key: str, default: str) -> str:
        try:
            return i18n.t(key, lang=lang, file=translation_file)
        except Exception:
            return default

    try:
        os.makedirs("downloads", exist_ok=True)
        if format_type == "pdf":
            await callback.message.edit_text(_t(f"processing_{format_type}", "Hujjat tayyorlanmoqda..."))
            output_path = f"downloads/{prefix}_{user_id}.pdf"
            success = pdf_func(data=user_data, lang=lang, output_pdf_path=output_path)
            if success and os.path.exists(output_path):
                await callback.message.reply_document(
                    output_path,
                    caption=_t(f"success_{format_type}", "Mana sizning hujjatingiz:"),
                )
                os.remove(output_path)
            else:
                await callback.message.edit_text(_t("error_text", "Xatolik yuz berdi."))
        else:
            await callback.message.edit_text(_t("processing_docx", "Word hujjati tayyorlanmoqda..."))
            output_path = doc_func(data=user_data, lang=lang)
            if output_path and os.path.exists(output_path):
                await callback.message.reply_document(
                    output_path,
                    caption=_t("success_docx", "Mana sizning hujjatingiz:"),
                )
                os.remove(output_path)
            else:
                await callback.message.edit_text(_t("error_text", "Xatolik yuz berdi."))
    except MessageNotModified:
        pass
    except Exception as e:
        print(f"Hujjat yaratishda xatolik ({prefix}): {e}")
    finally:
        fsm_service.finish(user_id)


# Orqaga moslik: format2_cb importlari uchun alias
universal_format2_callback = universal_format_callback

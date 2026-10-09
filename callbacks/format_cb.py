# callbacks/format_cb.py
import os
from pyrogram.errors import MessageNotModified
import config
from services.localization import i18n
from database.users_repo import get_user_balance, deduct_balance
from keyboards.payment_kb import get_amounts_keyboard

CV_PRICE = getattr(config, "CV_PRICE", 5000)


def _is_admin(user_id: int) -> bool:
    """Admin — cheksiz balans / bepul foydalanish."""
    return bool(config.ADMIN_ID) and user_id == config.ADMIN_ID


async def universal_format_callback(client, callback, prefix, translation_file, doc_func, pdf_func, fsm_service):
    user_id = callback.from_user.id
    user_data = fsm_service.get_data(user_id) or {}
    lang = user_data.get("cv_lang", "uz")

    # Admin uchun cheksiz balans ko'rsatish va bepul
    if _is_admin(user_id):
        balance = 999999999.0
    else:
        balance = get_user_balance(user_id)

    format_type = callback.data.split("_")[-1]  # pdf yoki docx

    # 1. Balans tekshiruvi (admin o'tkazib yuboriladi)
    if not _is_admin(user_id) and balance < CV_PRICE:
        try:
            warning_text = i18n.t("cv2_balance_low", lang=lang, file=translation_file).format(
                price=f"{CV_PRICE:,.0f}",
                balance=f"{balance:,.0f}",
            )
        except Exception:
            warning_text = (
                f"❌ Balansingiz yetarli emas!\n"
                f"Kerakli summa: {CV_PRICE:,.0f} so'm\n"
                f"Joriy balans: {balance:,.0f} so'm"
            )

        await callback.message.edit_text(warning_text)
        await callback.message.reply(
            i18n.t("pay_select_amount", lang=lang, file="message"),
            reply_markup=get_amounts_keyboard(lang),
        )
        await callback.answer()
        return

    # 2. Atomic yechish — faqat oddiy foydalanuvchilar (admin bepul)
    if not _is_admin(user_id):
        new_balance = deduct_balance(user_id, CV_PRICE)
        if new_balance is None:
            await callback.answer("⚠️ Balans yetarli emas!", show_alert=True)
            return

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
            os.makedirs("downloads", exist_ok=True)
            success = pdf_func(data=user_data, lang=lang, output_pdf_path=output_path)

            if success and os.path.exists(output_path):
                await callback.message.reply_document(
                    output_path,
                    caption=i18n.t(success_key, lang=lang, file=translation_file),
                )
                os.remove(output_path)
            else:
                await callback.message.edit_text(i18n.t("error_text", lang=lang, file=translation_file))

        else:
            await callback.message.edit_text(i18n.t("processing_docx", lang=lang, file=translation_file))

            output_path = doc_func(data=user_data, lang=lang)

            if output_path and os.path.exists(output_path):
                await callback.message.reply_document(
                    output_path,
                    caption=i18n.t("success_docx", lang=lang, file=translation_file),
                )
                os.remove(output_path)
            else:
                await callback.message.edit_text(i18n.t("error_text", lang=lang, file=translation_file))

    except MessageNotModified:
        pass
    except Exception as e:
        print(f"Hujjat yaratishda xatolik ({prefix}): {e}")
    finally:
        fsm_service.finish(user_id)

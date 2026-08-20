from pyrogram import filters, raw
from bot import bitik
import config
from services.payment import PaymentService
from database.users_repo import get_user_lang
from services.localization import i18n
from keyboards.payment_kb import get_amounts_keyboard, get_payment_methods_keyboard

user_invoices = {}

@bitik.on_message(filters.command("buy"))
async def buy_command(client, message):
    user_id = message.from_user.id
    lang = get_user_lang(user_id)
    
    text = i18n.t("pay_select_amount", lang=lang, file="message")
    await message.reply(
        text,
        reply_markup=get_amounts_keyboard(lang)
    )

@bitik.on_callback_query(filters.regex(r"^pay_amt_(\d+)"))
async def select_amount_callback(client, callback_query):
    amount = int(callback_query.data.split("_")[2])
    user_id = callback_query.from_user.id
    lang = get_user_lang(user_id)
    
    transaction_param = f"bitik_user_{user_id}_{int(callback_query.message.date.timestamp())}"
    click_web_url = PaymentService.generate_click_pay_url(amount, transaction_param)
    
    raw_template = i18n.t("pay_choose_method", lang=lang, file="message")
    text = raw_template.format(amount=f"{amount:,.0f}")
    
    await callback_query.message.edit_text(
        text,
        reply_markup=get_payment_methods_keyboard(amount, click_web_url, lang)
    )
    await callback_query.answer()

@bitik.on_callback_query(filters.regex(r"^method_clickterm_(\d+)"))
async def click_terminal_payment(client, callback_query):
    amount = int(callback_query.data.split("_")[2])
    amount_tiyin = PaymentService.format_amount_to_tiyin(amount)
    
    await callback_query.message.delete()
    chat_id = callback_query.from_user.id
    lang = get_user_lang(chat_id)
    
    try:
        peer = await client.resolve_peer(chat_id)
        
        # Raw orqali invoys yuborish
        response = await client.invoke(
            raw.functions.messages.SendMedia(
                peer=peer,
                media=raw.types.InputMediaInvoice(
                    title="bitik.uz Balansini to'ldirish",
                    description=f"Hisobingizni {amount:,.0f} so'mga to'ldirish uchun invoys.",
                    invoice=raw.types.Invoice(
                        currency="UZS",
                        prices=[
                            raw.types.LabeledPrice(
                                label=f"{amount:,.0f} UZS to'lash",
                                amount=amount_tiyin
                            )
                        ],
                        test=True
                    ),
                    provider=config.CLICK_PROVIDER_TOKEN,
                    provider_data=raw.types.DataJSON(data='{}'),
                    payload=f"bitik_topup_{amount}".encode("utf-8")
                ),
                message="",
                random_id=client.rnd_id()
            )
        )
        
        # Yuborilgan invoys xabarining ID sini saqlab qo'yamiz
        for update in response.updates:
            if hasattr(update, "id"):
                user_invoices[chat_id] = update.id
                break
            elif hasattr(update, "message") and hasattr(update.message, "id"):
                user_invoices[chat_id] = update.message.id
                break
                
    except Exception as e:
        err_template = i18n.t("invoice_error_msg", lang=lang, file="message")
        await client.send_message(chat_id, f"{err_template} {e}")
        
    await callback_query.answer()

@bitik.on_callback_query(filters.regex(r"^pay_cancel"))
async def cancel_payment(client, callback_query):
    user_id = callback_query.from_user.id
    lang = get_user_lang(user_id)
    cancel_text = i18n.t("payment_cancelled", lang=lang, file="message")
    
    await callback_query.message.edit_text(cancel_text)
    await callback_query.answer()

# Barcha raw update'larni to'g'ri va xavfsiz ushlash
@bitik.on_raw_update()
async def raw_updates_handler(client, update, users, chats):
    # Faqat to'lovga aloqador update turlarini o'tkazib yuboramiz, qolganlarini to'sib qo'ymaymiz
    if not isinstance(update, (raw.types.UpdateBotPrecheckoutQuery, raw.types.UpdateNewMessage, raw.types.UpdateNewChannelMessage)):
        return

    # 1. Pre-checkout so'rovini tasdiqlash
    if isinstance(update, raw.types.UpdateBotPrecheckoutQuery):
        await client.invoke(
            raw.functions.messages.SetBotPrecheckoutResults(
                query_id=update.query_id,
                success=True
            )
        )
        return
    
    # 2. Muvaffaqiyatli to'lovni (Service message) ushlash
    elif isinstance(update, (raw.types.UpdateNewMessage, raw.types.UpdateNewChannelMessage)):
        msg = update.message
        if not isinstance(msg, raw.types.MessageService) or not isinstance(msg.action, raw.types.MessageActionPaymentSentMe):
            return

        # Foydalanuvchi ID sini aniqlash
        user_id = None
        if hasattr(msg.peer_id, "user_id"):
            user_id = msg.peer_id.user_id
        elif hasattr(msg, "from_id") and hasattr(msg.from_id, "user_id"):
            user_id = msg.from_id.user_id
        
        if not user_id:
            return

        lang = get_user_lang(user_id)
        amount_tiyin = msg.action.total_amount
        amount_uzs = amount_tiyin / 100
        
        # Bazada balansni yangilash
        updated_balance = await PaymentService.process_successful_payment(user_id, amount_uzs)
        
        # Invoys xabarini o'chirish
        if user_id in user_invoices:
            try:
                await client.delete_messages(chat_id=user_id, message_ids=user_invoices[user_id])
                del user_invoices[user_id]
            except Exception as e:
                print(f"Invoys xabarini o'chirishda xatolik: {e}")
        
        # Tarjima matnlarini olish va xabar yuborish
        title_text = i18n.t("payment_success_title", lang=lang, file="message")
        added_text = i18n.t("payment_added", lang=lang, file="message")
        balance_text = i18n.t("payment_current_balance", lang=lang, file="message")
        
        await client.send_message(
            chat_id=user_id,
            text=f"{title_text}\n\n"
                 f"{added_text}: `{amount_uzs:,.0f}`\n"
                 f"{balance_text} `{updated_balance:,.0f}`"
        )
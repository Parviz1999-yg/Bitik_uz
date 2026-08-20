from pyrogram.errors import UserNotParticipant
from bot import bitik
from services.localization import i18n
from keyboards.sub_kb import get_sub_keyboard

REQUIRED_CHANNELS = ["@tm_bitik_uz"]

async def check_subscription(user_id: int) -> bool:
    """Foydalanuvchi hamma majburiy kanallarga a'zomi?"""
    for channel in REQUIRED_CHANNELS:
        try:
            member = await bitik.get_chat_member(channel, user_id)
            if member.status in ["left", "kicked"]:
                return False
        except UserNotParticipant:
            return False
        except Exception as e:
            print(f"Kanal tekshirishda xatolik: {e}")
            return False
    return True

async def enforce_subscription(client, message_or_callback) -> bool:
    """A'zolikni tekshiradi, a'zo bo'lmasa 4 tildagi tugma va matnni chiqaradi"""
    is_callback = hasattr(message_or_callback, "message")
    user_id = message_or_callback.from_user.id
    
    if await check_subscription(user_id):
        return True
        
    # Majburiy obuna matnini 4 tilda tayyorlaymiz
    sub_uz = i18n.t("sub_required", lang="uz")
    sub_tg = i18n.t("sub_required", lang="tg")
    sub_ru = i18n.t("sub_required", lang="ru")
    sub_en = i18n.t("sub_required", lang="en")
    full_text = f"{sub_uz}\n\n{sub_tg}\n\n{sub_ru}\n\n{sub_en}"
    
    # Tugma tilini default 'uz' deb uzatamiz
    reply_markup = get_sub_keyboard(lang="uz")
    
    if is_callback:
        await message_or_callback.answer(text=i18n.t("sub_error", lang="uz"), show_alert=True)
        if message_or_callback.message.text != full_text:
            await message_or_callback.message.edit_text(text=full_text, reply_markup=reply_markup)
    else:
        await message_or_callback.reply(text=full_text, reply_markup=reply_markup)
        
    return False
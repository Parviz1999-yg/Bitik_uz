from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def get_format2_keyboard(prefix: str = "anketa2") -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("📄 PDF", callback_data=f"{prefix}_format_pdf"),
            InlineKeyboardButton("📝 Word (DOCX)", callback_data=f"{prefix}_format_docx")
        ]
    ])
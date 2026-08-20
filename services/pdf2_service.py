import os
import re
import shutil
import pdfkit

def link_callback(uri, rel):
    """
    pdfkit yoki shablon uchun resurslar yo'lini to'g'rilashga yordam beradi.
    """
    base_dir = os.path.dirname(os.path.abspath(__file__))
    
    if "fonts" in uri or "templates" in uri:
        full_path = os.path.join(base_dir, "..", uri)
        if os.path.exists(full_path):
            return os.path.abspath(full_path)
            
    if os.path.exists(uri):
        return uri
        
    return uri

def get_template_path(lang: str, template_name: str) -> str:
    base_dir = os.path.dirname(os.path.abspath(__file__))
    supported_langs = ["uz", "tj", "ru", "en"]
    if lang not in supported_langs:
        lang = "uz"
        
    template_path = os.path.join(base_dir, "..", "templates", lang, template_name)
    if not os.path.exists(template_path):
        template_path = os.path.join(base_dir, "..", "templates", "uz", template_name)
        
    if not os.path.exists(template_path):
        print(f"Xatolik: Shablon topilmadi: {template_path}")
        return None
    return template_path

def get_user_photo_html(data: dict) -> str:
    photo_path = data.get("rasm") or data.get("user_photo")
    if photo_path and os.path.exists(photo_path):
        abs_photo_path = os.path.abspath(photo_path)
        return f'<img src="{abs_photo_path}" width="132" height="170" style="width: 3.5cm; height: 4.5cm; object-fit: cover;" />'
    return ""

def get_output_path(user_id: any, prefix: str = "anketa2", ext: str = "pdf") -> str:
    base_dir = os.path.dirname(os.path.abspath(__file__))
    output_path = os.path.join(base_dir, "..", "downloads", f"{prefix}_{user_id}.{ext}")
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    return output_path

def generate_pdf2_anketa(data: dict, lang: str, output_pdf_path: str = None) -> bool:
    """
    Anketa2 (cv2) ma'lumotlari asosida anketa2.html shablonini to'ldirib, PDF yaratadi.
    """
    # 1. Anketa2 HTML shablonini topamiz
    template_path = get_template_path(lang, "anketa2.html")
    if not template_path:
        return False
        
    with open(template_path, "r", encoding="utf-8") as f:
        html_content = f.read()

    # 2. Rasmni HTML formatga o'tkazish
    data["rasm"] = get_user_photo_html(data)

    # 3. Anketa2 maydonlarini regex orqali almashtirish
    for key, value in data.items():
        val_str = str(value or "")
        pattern = r"\{\{\s*" + re.escape(key) + r"\s*\}\}"
        html_content = re.sub(pattern, lambda m: val_str, html_content)

    # 4. Chiqish fayl yo'lini aniqlash (anketa2 prefiksi bilan)
    if not output_pdf_path:
        user_id = data.get("tg_id") or data.get("user_id", "anketa2")
        output_pdf_path = get_output_path(user_id, prefix="anketa2", ext="pdf")

    # 5. PDF YARATISH (Avtomatikani aniqlash)
    try:
        wkhtmltopdf_path = shutil.which("wkhtmltopdf")
        if not wkhtmltopdf_path and os.path.exists(r'C:\Program Files (x86)\wkhtmltopdf\bin\wkhtmltopdf.exe'):
            wkhtmltopdf_path = r'C:\Program Files (x86)\wkhtmltopdf\bin\wkhtmltopdf.exe'
            
        config = pdfkit.configuration(wkhtmltopdf=wkhtmltopdf_path) if wkhtmltopdf_path else None
        
        pdfkit.from_string(
            html_content, 
            output_pdf_path, 
            configuration=config, 
            options={
                'encoding': "UTF-8",
                'enable-local-file-access': None
            }
        )
        return True
    except Exception as e:
        print(f"Anketa2 PDF yaratishda xatolik: {e}")
        return False
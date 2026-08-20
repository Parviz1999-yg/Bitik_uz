import os
import re
import shutil
import pdfkit

def link_callback(uri, rel):
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

def get_output_path(user_id: any, prefix: str = "cv", ext: str = "pdf") -> str:
    base_dir = os.path.dirname(os.path.abspath(__file__))
    output_path = os.path.join(base_dir, "..", "downloads", f"{prefix}_{user_id}.{ext}")
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    return output_path

def generate_pdf_anketa(data: dict, lang: str, output_pdf_path: str = None) -> bool:
    # 1. Shablonni topamiz[cite: 5]
    template_path = get_template_path(lang, "anketa.html")
    if not template_path:
        return False
        
    with open(template_path, "r", encoding="utf-8") as f:
        html_content = f.read()

    # 2. Rasmni HTML formatga o'tkazish[cite: 5]
    data["rasm"] = get_user_photo_html(data)

    # 3. Ma'lumotlarni regex orqali almashtirish[cite: 5]
    for key, value in data.items():
        val_str = str(value or "")
        pattern = r"\{\{\s*" + re.escape(key) + r"\s*\}\}"
        html_content = re.sub(pattern, lambda m: val_str, html_content)

    # 4. Qarindoshlar ro'yxatini render qilish[cite: 5]
    qarindoshlar_html = ""
    raw_qarindoshlar = data.get("qarindoshlar_list", []) or data.get("qarindoshlar", [])
    for q in raw_qarindoshlar:
        qarindoshlar_html += f"""
            <tr>
                <td>{q.get('qarindosh', '')}</td>
                <td>{q.get('qarindosh_ism', '')}</td>
                <td>{q.get('qatr_ty_tj', '')}</td>
                <td>{q.get('qarin_kasb', '')}</td>
                <td>{q.get('qar_manzil', '')}</td>
            </tr>
        """
    
    qarindosh_pattern = r"\{\{\s*qarindoshlar\s*\}\}"
    html_content = re.sub(qarindosh_pattern, lambda m: qarindoshlar_html, html_content)

    # 5. Chiqish fayl yo'lini aniqlash[cite: 5]
    if not output_pdf_path:
        user_id = data.get("tg_id") or data.get("user_id", "cv")
        output_pdf_path = get_output_path(user_id, prefix="cv", ext="pdf")

    # 6. PDF YARATISH (Environment variables va tizimdan qidirish)
    try:
        # Avval .env / environment variables dan qidiramiz
        wkhtmltopdf_path = os.getenv("WKHTMLTOPDF_PATH")
        
        # Agar u yerda bo'lmasa, tizimdan (shutil.which) qidiramiz
        if not wkhtmltopdf_path:
            wkhtmltopdf_path = shutil.which("wkhtmltopdf")
            
        # Agar topilmasa va Windows'da bo'lsangiz, standart yo'lni tekshiramiz[cite: 5]
        if not wkhtmltopdf_path and os.path.exists(r'C:\Program Files (x86)\wkhtmltopdf\bin\wkhtmltopdf.exe'):
            wkhtmltopdf_path = r'C:\Program Files (x86)\wkhtmltopdf\bin\wkhtmltopdf.exe'
            
        if wkhtmltopdf_path:
            config = pdfkit.configuration(wkhtmltopdf=wkhtmltopdf_path)
            pdfkit.from_string(
                html_content, 
                output_pdf_path, 
                configuration=config, 
                options={
                    'encoding': "UTF-8",
                    'enable-local-file-access': None
                }
            )
        else:
            pdfkit.from_string(
                html_content, 
                output_pdf_path, 
                options={
                    'encoding': "UTF-8",
                    'enable-local-file-access': None
                }
            )
        return True
    except Exception as e:
        print(f"PDF yaratishda xatolik: {e}")
        return False
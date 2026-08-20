import os
from typing import Dict, Optional
from docxtpl import DocxTemplate, InlineImage
from docx.shared import Inches

def get_template_path(lang: str, template_name: str) -> Optional[str]:
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

def get_user_photo(doc, data: dict):
    photo_path = data.get("rasm") or data.get("user_photo")
    if photo_path and os.path.exists(photo_path):
        try:
            return InlineImage(doc, photo_path, width=Inches(1.5), height=Inches(2.0))
        except Exception as e:
            print(f"Rasm qo'shishda xatolik: {e}")
    return None

def get_output_path(user_id: any, prefix: str = "anketa2", ext: str = "docx") -> str:
    base_dir = os.path.dirname(os.path.abspath(__file__))
    output_path = os.path.join(base_dir, "..", "downloads", f"{prefix}_{user_id}.{ext}")
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    return output_path

def save_document(doc, user_id: any, prefix: str = "anketa2") -> str:
    output_path = get_output_path(user_id, prefix=prefix, ext="docx")
    doc.save(output_path)
    return output_path

def create_cv2_document(data: Dict, lang: str) -> str:
    template_path = get_template_path(lang, "anketa2.docx")
    if not template_path:
        return None

    doc = DocxTemplate(template_path)
    
    rasm_context = get_user_photo(doc, data)

    # Anketa2 FSM maydonlariga mos kontekst
    context = {
        "talim_muassasa": data.get("talim_muassasa", ""),
        "yonalish": data.get("yonalish", ""),
        "kurs": data.get("kurs", ""),
        "mutaxasislik": data.get("mutaxasislik", ""),
        "familiya": data.get("familiya", ""),
        "ism": data.get("ism", ""),
        "sharif": data.get("sharif", ""),
        "tugilgan": data.get("tugilgan", ""),
        "millati": data.get("millati", ""),
        "malumoti": data.get("malumoti", ""),
        "okishga_kirgan": data.get("okishga_kirgan", ""),
        "okishga_kirgunch": data.get("okishga_kirgunch", ""),
        "ota_ona": data.get("ota_ona", ""),
        "ota_ona_manzl": data.get("ota_ona_manzl", ""),
        "oilaviy": data.get("oilaviy", ""),
        "pasport": data.get("pasport", ""),
        "doimiy_manzil": data.get("doimiy_manzil", ""),
        "ijara": data.get("ijara", ""),
        "ijara_sana": data.get("ijara_sana", ""),
        "rasm": rasm_context
    }
    
    doc.render(context)
    user_id = data.get("tg_id") or data.get("user_id", "anketa2")
    return save_document(doc, user_id, prefix="anketa2")
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

def get_output_path(user_id: any, prefix: str = "cv", ext: str = "pdf") -> str:
    base_dir = os.path.dirname(os.path.abspath(__file__))
    output_path = os.path.join(base_dir, "..", "downloads", f"{prefix}_{user_id}.{ext}")
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    return output_path

def save_document(doc, user_id: any, prefix: str = "cv") -> str:
    output_path = get_output_path(user_id, prefix=prefix, ext="docx")
    doc.save(output_path)
    return output_path

def create_cv_document(data: Dict, lang: str) -> str:
    template_path = get_template_path(lang, "anketa.docx")
    if not template_path:
        return None

    doc = DocxTemplate(template_path)
    
    raw_qarindoshlar = data.get("qarindoshlar_list", [])
    qarindoshlar_context = [
        {
            "qarindosh": q.get("qarindosh", "-"),
            "qarindosh_ism": q.get("qarindosh_ism", "-"),
            "qatr_ty_tj": q.get("qatr_ty_tj", "-"),
            "qarin_kasb": q.get("qarin_kasb", "-"),
            "qar_manzil": q.get("qar_manzil", "-")
        } for q in raw_qarindoshlar
    ]
    
    rasm_context = get_user_photo(doc, data)

    context = {
        "familiya": data.get("familiya", ""),
        "ism": data.get("ism", ""),
        "nasab": data.get("nasab", ""),
        "boshlangich_sana": data.get("boshlangich_sana", ""),
        "oliygoh": data.get("oliygoh", ""),
        "yonalish": data.get("yonalish", ""),
        "togilgan_yili": data.get("togilgan_yili", ""),
        "togilgan_joyi": data.get("togilgan_joyi", ""),
        "millati": data.get("millati", ""),
        "partiya": data.get("partiya", ""),
        "malmoti": data.get("malmoti", ""),
        "tugatgan": data.get("tugatgan", ""),
        "mutaxasisligi": data.get("mutaxasisligi", ""),
        "ilmiy_darajasi": data.get("ilmiy_darajasi", ""),
        "ilmiy_unvoni": data.get("ilmiy_unvoni", ""),
        "til_bilish": data.get("til_bilish", ""),
        "mukofot": data.get("mukofot", ""),
        "deputatlik": data.get("deputatlik", ""),
        "faoliyati": data.get("faoliyati", ""),
        "qarindoshlar": qarindoshlar_context,
        "rasm": rasm_context
    }
    
    doc.render(context)
    user_id = data.get("tg_id") or data.get("user_id", "cv")
    return save_document(doc, user_id, prefix="cv")
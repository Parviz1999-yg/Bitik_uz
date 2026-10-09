from typing import Dict, Optional

from docxtpl import DocxTemplate, InlineImage
from docx.shared import Inches

from services.paths import get_template_path, get_output_path


def get_user_photo(doc, data: dict):
    photo_path = data.get("rasm") or data.get("user_photo")
    if photo_path:
        try:
            import os

            if os.path.exists(photo_path):
                return InlineImage(doc, photo_path, width=Inches(1.5), height=Inches(2.0))
        except Exception as e:
            print(f"Rasm qo'shishda xatolik: {e}")
    return None


def create_cv_document(data: Dict, lang: str) -> Optional[str]:
    template_path = get_template_path(lang, "anketa.docx")
    if not template_path:
        return None

    doc = DocxTemplate(template_path)
    raw_qarindoshlar = data.get("qarindoshlar_list", []) or []
    qarindoshlar_context = [
        {
            "qarindosh": q.get("qarindosh", "-"),
            "qarindosh_ism": q.get("qarindosh_ism", "-"),
            "qatr_ty_tj": q.get("qatr_ty_tj", "-"),
            "qarin_kasb": q.get("qarin_kasb", "-"),
            "qar_manzil": q.get("qar_manzil", "-"),
        }
        for q in raw_qarindoshlar
    ]

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
        "rasm": get_user_photo(doc, data),
    }
    doc.render(context)
    user_id = data.get("tg_id") or data.get("user_id", "cv")
    output_path = get_output_path(user_id, prefix="cv", ext="docx")
    doc.save(output_path)
    return output_path

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


def create_cv2_document(data: Dict, lang: str) -> Optional[str]:
    template_path = get_template_path(lang, "anketa2.docx")
    if not template_path:
        return None

    doc = DocxTemplate(template_path)
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
        "rasm": get_user_photo(doc, data),
    }
    doc.render(context)
    user_id = data.get("tg_id") or data.get("user_id", "anketa2")
    output_path = get_output_path(user_id, prefix="anketa2", ext="docx")
    doc.save(output_path)
    return output_path

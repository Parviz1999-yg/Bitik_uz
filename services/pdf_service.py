# services/pdf_service.py
import os
from reportlab.lib.pagesizes import A4
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, 
    Image as RLImage, PageBreak
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from services.localization import i18n

def get_output_path(user_id: any, prefix: str = "cv", ext: str = "pdf") -> str:
    base_dir = os.path.dirname(os.path.abspath(__file__))
    output_path = os.path.join(base_dir, "..", "downloads", f"{prefix}_{user_id}.{ext}")
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    return output_path

def generate_pdf_anketa(data: dict, lang: str = "uz", output_pdf_path: str = None) -> bool:
    try:
        # 1. Chiqish fayl yo'lini aniqlash
        if not output_pdf_path:
            user_id = data.get("tg_id") or data.get("user_id", "cv")
            output_pdf_path = get_output_path(user_id, prefix="cv", ext="pdf")

        # 2. Times New Roman (normal va bold) shriftlarini to'liq ro'yxatdan o'tkazish
        base_dir = os.path.dirname(os.path.abspath(__file__))
        font_path = os.path.join(base_dir, "..", "fonts", "times.ttf")
        bold_font_path = os.path.join(base_dir, "..", "fonts", "timesbd.ttf")
        
        font_name = "Helvetica" # Zaxira shrift
        if os.path.exists(font_path):
            try:
                pdfmetrics.registerFont(TTFont('TimesNewRoman', font_path))
                if os.path.exists(bold_font_path):
                    pdfmetrics.registerFont(TTFont('TimesNewRoman-Bold', bold_font_path))
                    pdfmetrics.registerFontFamily(
                        'TimesNewRoman',
                        normal='TimesNewRoman',
                        bold='TimesNewRoman-Bold',
                        italic='TimesNewRoman',
                        boldItalic='TimesNewRoman-Bold'
                    )
                font_name = 'TimesNewRoman'
            except Exception:
                pass

        # 3. PDF hujjatni sozlash
        doc = SimpleDocTemplate(
            output_pdf_path,
            pagesize=A4,
            leftMargin=36, rightMargin=36,
            topMargin=36, bottomMargin=36
        )
        story = []

        # Matn uslublari
        styles = getSampleStyleSheet()
        normal_style = ParagraphStyle(
            'AnketaNormal',
            fontName=font_name,
            fontSize=10,
            leading=13,
            textColor=colors.black
        )
        center_style = ParagraphStyle(
            'AnketaCenter',
            parent=normal_style,
            alignment=1, # Markazga tekislash
        )
        header_style = ParagraphStyle(
            'AnketaHeader',
            parent=normal_style,
            fontSize=14,
            leading=16,
            alignment=1, # Markazga tekislash
        )

        # --- LOKALIZATSIYA MATNLARI ---
        title_main = i18n.t("pdf_main_title", lang=lang, file="cv")
        if title_main == "pdf_main_title": title_main = "MA’LUMOTNOMA"

        no_photo_text = i18n.t("pdf_no_photo", lang=lang, file="cv")
        if no_photo_text == "pdf_no_photo": no_photo_text = "Rasm yo'q"

        # --- 1-SAHIFA: ASOSIY MA'LUMOTNOMA ---
        # Foydalanuvchi rasmini yuklash
        photo_path = data.get("rasm") or data.get("user_photo")
        if photo_path and os.path.exists(photo_path):
            photo_flowable = RLImage(photo_path, width=3.5 * 28.35, height=4.5 * 28.35)
            photo_flowable.hAlign = 'RIGHT'
        else:
            photo_flowable = Paragraph(f"<b>{no_photo_text}</b>", center_style)

        # F.I.Sh va O'qish joyi
        fio_text = f"{data.get('familiya', '')} {data.get('ism', '')} {data.get('nasab', '')}"
        
        study_template = i18n.t("pdf_study_template", lang=lang, file="cv")
        if study_template == "pdf_study_template":
            study_text = f"{data.get('boshlangich_sana', '')}- yildan buyon: <br/><b>{data.get('oliygoh', '')}ning “{data.get('yonalish', '')}” yo‘nalishi talabasi</b>"
        else:
            study_text = study_template.format(
                boshlangich_sana=data.get('boshlangich_sana', ''),
                oliygoh=data.get('oliygoh', ''),
                yonalish=data.get('yonalish', '')
            )
        
        # Sarlavha va asosiy matn rasm bilan bir chiziqda (birinchi katakda) boshlanadi
        top_cell_content = [
            Paragraph(f"<b>{title_main}</b>", header_style),
            Spacer(1, 6),
            Paragraph(f"<b>{fio_text}</b>", center_style),
            Spacer(1, 4),
            Paragraph(study_text, normal_style)
        ]

        # Jadval maydonlari (Labels)
        lbl_togilgan_yili = i18n.t("lbl_togilgan_yili", lang=lang, file="cv")
        if lbl_togilgan_yili == "lbl_togilgan_yili": lbl_togilgan_yili = "Tug‘ilgan yili:"

        lbl_togilgan_joyi = i18n.t("lbl_togilgan_joyi", lang=lang, file="cv")
        if lbl_togilgan_joyi == "lbl_togilgan_joyi": lbl_togilgan_joyi = "Tug‘ilgan joyi:"

        lbl_millati = i18n.t("lbl_millati", lang=lang, file="cv")
        if lbl_millati == "lbl_millati": lbl_millati = "Millati:"

        lbl_partiya = i18n.t("lbl_partiya", lang=lang, file="cv")
        if lbl_partiya == "lbl_partiya": lbl_partiya = "Partiyaviyligi:"

        lbl_malmoti = i18n.t("lbl_malmoti", lang=lang, file="cv")
        if lbl_malmoti == "lbl_malmoti": lbl_malmoti = "Ma’lumoti:"

        lbl_tugatgan = i18n.t("lbl_tugatgan", lang=lang, file="cv")
        if lbl_tugatgan == "lbl_tugatgan": lbl_tugatgan = "Tamomlagan:"

        lbl_mutaxasisligi = i18n.t("lbl_mutaxasisligi", lang=lang, file="cv")
        if lbl_mutaxasisligi == "lbl_mutaxasisligi": lbl_mutaxasisligi = "Ma’lumoti bo‘yicha mutaxassisligi:"

        lbl_ilmiy_darajasi = i18n.t("lbl_ilmiy_darajasi", lang=lang, file="cv")
        if lbl_ilmiy_darajasi == "lbl_ilmiy_darajasi": lbl_ilmiy_darajasi = "Ilmiy darajasi:"

        lbl_ilmiy_unvoni = i18n.t("lbl_ilmiy_unvoni", lang=lang, file="cv")
        if lbl_ilmiy_unvoni == "lbl_ilmiy_unvoni": lbl_ilmiy_unvoni = "Ilmiy unvoni:"

        lbl_til_bilish = i18n.t("lbl_til_bilish", lang=lang, file="cv")
        if lbl_til_bilish == "lbl_til_bilish": lbl_til_bilish = "Qaysi chet el tillarini biladi:"

        lbl_mukofot = i18n.t("lbl_mukofot", lang=lang, file="cv")
        if lbl_mukofot == "lbl_mukofot": lbl_mukofot = "Davlat mukofoti bilan taqdirlanganmi (qanaqa):"

        lbl_deputatlik = i18n.t("lbl_deputatlik", lang=lang, file="cv")
        if lbl_deputatlik == "lbl_deputatlik": lbl_deputatlik = "Xalq deputatlari, Respublika, viloyat, shahar va tuman kengashi deputati yoki boshqa saylanadigan organlarning a’zosimi (to‘liq ko‘rsatilishi lozim):"

        lbl_faoliyati_title = i18n.t("lbl_faoliyati_title", lang=lang, file="cv")
        if lbl_faoliyati_title == "lbl_faoliyati_title": lbl_faoliyati_title = "MEHNAT FAOLIYATI:"

        # Asosiy jadval ma'lumotlari
        t_data = [
            [top_cell_content, '', photo_flowable],
            [
                Paragraph(f"<b>{lbl_togilgan_yili}</b><br/>{data.get('togilgan_yili', '')}- yil", normal_style),
                Paragraph(f"<b>{lbl_togilgan_joyi}</b><br/>{data.get('togilgan_joyi', '')}", normal_style),
                ''
            ],
            [
                Paragraph(f"<b>{lbl_millati}</b><br/>{data.get('millati', '')}", normal_style),
                Paragraph(f"<b>{lbl_partiya}</b><br/>{data.get('partiya', '')}", normal_style),
                ''
            ],
            [
                Paragraph(f"<b>{lbl_malmoti}</b><br/>{data.get('malmoti', '')}", normal_style),
                Paragraph(f"<b>{lbl_tugatgan}</b><br/>{data.get('tugatgan', '')}", normal_style),
                ''
            ],
            # Mutaxassisligi: Nomi birinchi ustunda, qiymati keyingi ustunda
            [
                Paragraph(f"<b>{lbl_mutaxasisligi}</b>", normal_style), 
                Paragraph(str(data.get('mutaxasisligi', '')), normal_style), 
                ''
            ],
            # Ilmiy darajasi va Ilmiy unvoni yonma-yon bitta qatorda
            [
                Paragraph(f"<b>{lbl_ilmiy_darajasi}</b><br/>{data.get('ilmiy_darajasi', '')}", normal_style),
                Paragraph(f"<b>{lbl_ilmiy_unvoni}</b><br/>{data.get('ilmiy_unvoni', '')}", normal_style),
                ''
            ],
            [
                Paragraph(f"<b>{lbl_til_bilish}</b><br/>{data.get('til_bilish', '')}", normal_style), 
                '', 
                ''
            ],
            [
                Paragraph(f"<b>{lbl_mukofot}</b><br/>{data.get('mukofot', '')}", normal_style), 
                '', 
                ''
            ],
            [
                Paragraph(f"<b>{lbl_deputatlik}</b><br/>{data.get('deputatlik', '')}", normal_style), 
                '', 
                ''
            ],
        ]

        main_table = Table(t_data, colWidths=[211, 211, 101])
        main_table.setStyle(TableStyle([
            ('VALIGN', (0,0), (-1,-1), 'TOP'),
            ('SPAN', (0,0), (1,0)), 
            ('SPAN', (2,0), (2,3)), # Rasm 4 ta qatordan iborat bo'lishi uchun davom etadi
            ('SPAN', (1,4), (2,4)), # Mutaxassisligi qiymati uchun ustunlar birlashtirildi
            ('SPAN', (1,5), (2,5)), # Ilmiy unvoni uchun o'ngdagi ustunlar birlashtirildi
            ('SPAN', (0,6), (2,6)), # Til bilish
            ('SPAN', (0,7), (2,7)), # Mukofot
            ('SPAN', (0,8), (2,8)), # Deputatlik
            ('BOTTOMPADDING', (0,0), (-1,-1), 3),
            ('TOPPADDING', (0,0), (-1,-1), 3),
            ('LEFTPADDING', (0,0), (-1,-1), 3),
            ('RIGHTPADDING', (0,0), (-1,-1), 3),
        ]))

        story.append(main_table)
        story.append(Spacer(1, 10))

        # Mehnat faoliyati bo'limi
        story.append(Paragraph(f"<b>{lbl_faoliyati_title}</b>", header_style))
        story.append(Spacer(1, 3))
        faoliyat_text = data.get('faoliyati', '')
        story.append(Paragraph(faoliyat_text.replace('\n', '<br/>'), normal_style))

        # --- 2-SAHIFA: QARINDOSHLAR HAQIDA MA'LUMOT ---
        story.append(PageBreak())

        rel_title_template = i18n.t("pdf_rel_title_template", lang=lang, file="cv")
        if rel_title_template == "pdf_rel_title_template":
            rel_title_text = f"<b>{fio_text}ning yaqin qarindoshlari haqida</b><br/><b>MA’LUMOT</b>"
        else:
            rel_title_text = rel_title_template.format(fio=fio_text)

        story.append(Paragraph(rel_title_text, header_style))
        story.append(Spacer(1, 10))

        # Qarindoshlar jadvali sarlavhasi
        col1_text = i18n.t("pdf_rel_col_1", lang=lang, file="cv")
        if col1_text == "pdf_rel_col_1": col1_text = "Qarindoshligi"

        col2_text = i18n.t("pdf_rel_col_2", lang=lang, file="cv")
        if col2_text == "pdf_rel_col_2": col2_text = "Familiya, ismi, otasining ismi"

        col3_text = i18n.t("pdf_rel_col_3", lang=lang, file="cv")
        if col3_text == "pdf_rel_col_3": col3_text = "Tug‘ilgan yili va joyi"

        col4_text = i18n.t("pdf_rel_col_4", lang=lang, file="cv")
        if col4_text == "pdf_rel_col_4": col4_text = "Ish joyi va lavozimi"

        col5_text = i18n.t("pdf_rel_col_5", lang=lang, file="cv")
        if col5_text == "pdf_rel_col_5": col5_text = "Turar joyi"

        rel_headers = [
            Paragraph(f"<b>{col1_text}</b>", normal_style),
            Paragraph(f"<b>{col2_text}</b>", normal_style),
            Paragraph(f"<b>{col3_text}</b>", normal_style),
            Paragraph(f"<b>{col4_text}</b>", normal_style),
            Paragraph(f"<b>{col5_text}</b>", normal_style)
        ]
        rel_data = [rel_headers]

        # Qarindoshlar qatorlarini qo'shish (1-ustun - qarindoshlik darajasi - qalin qilib qo'yildi)
        raw_qarindoshlar = data.get("qarindoshlar_list", []) or data.get("qarindoshlar", [])
        for q in raw_qarindoshlar:
            rel_data.append([
                Paragraph(f"<b>{str(q.get('qarindosh', ''))}</b>", normal_style),
                Paragraph(str(q.get('qarindosh_ism', '')), normal_style),
                Paragraph(str(q.get('qatr_ty_tj', '')), normal_style),
                Paragraph(str(q.get('qarin_kasb', '')), normal_style),
                Paragraph(str(q.get('qar_manzil', '')), normal_style),
            ])

        rel_table = Table(rel_data, colWidths=[75, 130, 100, 120, 98])
        rel_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#f2f2f2')),
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('GRID', (0,0), (-1,-1), 0.5, colors.black),
            ('TOPPADDING', (0,0), (-1,-1), 3),
            ('BOTTOMPADDING', (0,0), (-1,-1), 3),
            ('LEFTPADDING', (0,0), (-1,-1), 3),
            ('RIGHTPADDING', (0,0), (-1,-1), 3),
        ]))

        story.append(rel_table)

        # PDF hujjatni yig'ib saqlash
        doc.build(story)
        return True

    except Exception as e:
        print(f"ReportLab orqali PDF yaratishda xatolik: {e}")
        import traceback
        traceback.print_exc()
        return False
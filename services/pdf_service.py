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
            alignment=1, # Markazga tekislash (HTML <para align='center'> o'rniga xavfsiz usul)
        )

        # --- 1-SAHIFA: ASOSIY MA'LUMOTNOMA ---
        story.append(Paragraph("<b>MA’LUMOTNOMA</b>", header_style))
        story.append(Spacer(1, 15))

        # Foydalanuvchi rasmini yuklash
        photo_path = data.get("rasm") or data.get("user_photo")
        if photo_path and os.path.exists(photo_path):
            photo_flowable = RLImage(photo_path, width=3.5 * 28.35, height=4.5 * 28.35)
            photo_flowable.hAlign = 'RIGHT'
        else:
            photo_flowable = Paragraph("<b>Rasm yo'q</b>", normal_style)

        # F.I.Sh va O'qish joyi (xatolik bermaydigan elementlar ro'yxati)
        fio_text = f"{data.get('familiya', '')} {data.get('ism', '')} {data.get('nasab', '')}"
        study_text = f"{data.get('boshlangich_sana', '')}- yildan buyon: <br/><b>{data.get('oliygoh', '')}ning “{data.get('yonalish', '')}” yo‘nalishi talabasi</b>"
        
        top_cell_content = [
            Paragraph(f"<b>{fio_text}</b>", center_style),
            Spacer(1, 6),
            Paragraph(study_text, normal_style)
        ]

        # Asosiy jadval ma'lumotlari
        t_data = [
            [top_cell_content, '', photo_flowable],
            [
                Paragraph(f"<b>Tug‘ilgan yili:</b><br/>{data.get('togilgan_yili', '')}- yil", normal_style),
                Paragraph(f"<b>Tug‘ilgan joyi:</b><br/>{data.get('togilgan_joyi', '')}", normal_style),
                ''
            ],
            [
                Paragraph(f"<b>Millati:</b><br/>{data.get('millati', '')}", normal_style),
                Paragraph(f"<b>Partiyaviyligi:</b><br/>{data.get('partiya', '')}", normal_style),
                ''
            ],
            [
                Paragraph(f"<b>Ma’lumoti:</b><br/>{data.get('malmoti', '')}", normal_style),
                Paragraph(f"<b>Tamomlagan:</b><br/>{data.get('tugatgan', '')}", normal_style),
                ''
            ],
            [Paragraph(f"<b>Ma’lumoti bo‘yicha mutaxassisligi:</b><br/>{data.get('mutaxasisligi', '')}", normal_style), '', ''],
            [Paragraph(f"<b>Ilmiy darajasi:</b><br/>{data.get('ilmiy_darajasi', '')}", normal_style), '', ''],
            [Paragraph(f"<b>Ilmiy unvoni:</b><br/>{data.get('ilmiy_unvoni', '')}", normal_style), '', ''],
            [Paragraph(f"<b>Qaysi chet el tillarini biladi:</b><br/>{data.get('til_bilish', '')}", normal_style), '', ''],
            [Paragraph(f"<b>Davlat mukofoti bilan taqdirlanganmi (qanaqa):</b><br/>{data.get('mukofot', '')}", normal_style), '', ''],
            [Paragraph(f"<b>Xalq deputatlari, Respublika, viloyat, shahar va tuman kengashi deputati yoki boshqa saylanadigan organlarning a’zosimi (to‘liq ko‘rsatilishi lozim):</b><br/>{data.get('deputatlik', '')}", normal_style), '', ''],
        ]

        main_table = Table(t_data, colWidths=[211, 211, 101])
        main_table.setStyle(TableStyle([
            ('VALIGN', (0,0), (-1,-1), 'TOP'),
            ('SPAN', (0,0), (1,0)), 
            ('SPAN', (2,0), (2,3)), 
            ('SPAN', (0,4), (2,4)), 
            ('SPAN', (0,5), (2,5)),
            ('SPAN', (0,6), (2,6)),
            ('SPAN', (0,7), (2,7)),
            ('SPAN', (0,8), (2,8)),
            ('SPAN', (0,9), (2,9)),
            ('BOTTOMPADDING', (0,0), (-1,-1), 5),
            ('TOPPADDING', (0,0), (-1,-1), 5),
            ('LEFTPADDING', (0,0), (-1,-1), 4),
            ('RIGHTPADDING', (0,0), (-1,-1), 4),
        ]))

        story.append(main_table)
        story.append(Spacer(1, 15))

        # Mehnat faoliyati bo'limi
        story.append(Paragraph("<b>MEHNAT FAOLIYATI:</b>", header_style))
        story.append(Spacer(1, 5))
        faoliyat_text = data.get('faoliyati', '')
        story.append(Paragraph(faoliyat_text.replace('\n', '<br/>'), normal_style))

        # --- 2-SAHIFA: QARINDOSHLAR HAQIDA MA'LUMOT ---
        story.append(PageBreak())

        # Xavfli <para align='center'> o'rniga xavfsiz Paragraph va header_style ishlatildi
        rel_title_text = f"<b>{fio_text}ning yaqin qarindoshlari haqida</b><br/><b>MA’LUMOT</b>"
        story.append(Paragraph(rel_title_text, header_style))
        story.append(Spacer(1, 15))

        # Qarindoshlar jadvali sarlavhasi
        rel_headers = [
            Paragraph("<b>Qarindoshligi</b>", normal_style),
            Paragraph("<b>Familiya, ismi, otasining ismi</b>", normal_style),
            Paragraph("<b>Tug‘ilgan yili va joyi</b>", normal_style),
            Paragraph("<b>Ish joyi va lavozimi</b>", normal_style),
            Paragraph("<b>Turar joyi</b>", normal_style)
        ]
        rel_data = [rel_headers]

        # Qarindoshlar qatorlarini qo'shish
        raw_qarindoshlar = data.get("qarindoshlar_list", []) or data.get("qarindoshlar", [])
        for q in raw_qarindoshlar:
            rel_data.append([
                Paragraph(str(q.get('qarindosh', '')), normal_style),
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
            ('TOPPADDING', (0,0), (-1,-1), 5),
            ('BOTTOMPADDING', (0,0), (-1,-1), 5),
            ('LEFTPADDING', (0,0), (-1,-1), 4),
            ('RIGHTPADDING', (0,0), (-1,-1), 4),
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
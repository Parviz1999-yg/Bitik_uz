import os
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image as RLImage
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from services.localization import i18n  # <--- i18n import qilindi

def get_output_path(user_id: any, prefix: str = "anketa2", ext: str = "pdf") -> str:
    base_dir = os.path.dirname(os.path.abspath(__file__))
    output_path = os.path.join(base_dir, "..", "downloads", f"{prefix}_{user_id}.{ext}")
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    return output_path

def generate_pdf2_anketa(data: dict, lang: str = "uz", output_pdf_path: str = None) -> bool:
    """
    ReportLab yordamida Anketa2 shablonini yaratadi: 
    Barcha statik matnlar i18n orqali tillarga moslashtirilgan.
    """
    try:
        if not output_pdf_path:
            user_id = data.get("tg_id") or data.get("user_id", "anketa2")
            output_pdf_path = get_output_path(user_id, prefix="anketa2", ext="pdf")

        doc = SimpleDocTemplate(
            output_pdf_path,
            pagesize=A4,
            leftMargin=28.3,
            rightMargin=28.3,
            topMargin=22.6,
            bottomMargin=22.6
        )
        
        story = []

        base_dir = os.path.dirname(os.path.abspath(__file__))
        font_path = os.path.join(base_dir, "..", "fonts", "times.ttf")
        bold_font_path = os.path.join(base_dir, "..", "fonts", "timesbd.ttf")
        
        if os.path.exists(font_path):
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
        else:
            font_name = 'Helvetica'

        header_center_style = ParagraphStyle(
            'HeaderCenterStyle', fontName=font_name, fontSize=10, leading=12, alignment=1, textColor=colors.black
        )
        title_center_style = ParagraphStyle(
            'TitleCenterStyle', fontName=font_name, fontSize=11.5, leading=14, alignment=1, textColor=colors.black
        )
        normal_style = ParagraphStyle(
            'NormalStyle', fontName=font_name, fontSize=9, leading=11.5, textColor=colors.black
        )
        center_style = ParagraphStyle(
            'CenterStyle', fontName=font_name, fontSize=9, leading=11.5, alignment=1, textColor=colors.black
        )

        # --- 1. FIO JADVALI ---
        fio_total_width = 535 - 113.4  # ~421.6 pt
        col_w = fio_total_width / 3.0

        fio_data = [
            [
                Paragraph(f"<b>{i18n.t('familiya', lang=lang, file='anketa2')}</b><br/>" + str(data.get('familiya', '')), normal_style),
                Paragraph(f"<b>{i18n.t('ism', lang=lang, file='anketa2')}</b><br/>" + str(data.get('ism', '')), normal_style),
                Paragraph(f"<b>{i18n.t('sharif', lang=lang, file='anketa2')}</b><br/>" + str(data.get('sharif', '')), normal_style)
            ]
        ]
        
        fio_table = Table(fio_data, colWidths=[col_w, col_w, col_w])
        fio_table.setStyle(TableStyle([
            ('VALIGN', (0,0), (-1,-1), 'BOTTOM'),
            ('TOPPADDING', (0,0), (-1,-1), 2),
            ('BOTTOMPADDING', (0,0), (-1,-1), 2),
            ('LEFTPADDING', (0,0), (-1,-1), 2),
            ('RIGHTPADDING', (0,0), (-1,-1), 2),
        ]))

        # --- 2. RASM JADVALI ---
        photo_path = data.get("rasm") or data.get("user_photo")
        photo_height = 4.5 * 28.35  # ~127.58 pt
        
        if photo_path and os.path.exists(photo_path):
            img_element = RLImage(photo_path, width=3.5 * 28.35, height=photo_height)
            photo_cell = img_element
        else:
            photo_cell = Paragraph(i18n.t('foto_placeholder', lang=lang, file='anketa2'), center_style)

        photo_table_data = [[photo_cell]]
        photo_table = Table(photo_table_data, colWidths=[113.4])
        photo_table.setStyle(TableStyle([
            ('VALIGN', (0,0), (-1,-1), 'BOTTOM'),
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('TOPPADDING', (0,0), (-1,-1), 2),
            ('BOTTOMPADDING', (0,0), (-1,-1), 2),
            ('LEFTPADDING', (0,0), (-1,-1), 2),
            ('RIGHTPADDING', (0,0), (-1,-1), 2),
        ]))

        # --- 3. CHAP TOMONGI ICHKI KONTENT ---
        raw_student_title = i18n.t('student_title', lang=lang, file='anketa2')
        talim_raw = raw_student_title.format(
            muassasa=data.get('talim_muassasa', ''),
            yonalish=data.get('yonalish', ''),
            kurs=data.get('kurs', '')
        )
        talim_text = f"<b>{talim_raw}</b>"
        
        top_content = [
            Paragraph(talim_text, header_center_style),
            Spacer(1, 6),
            Paragraph(f"<b>{i18n.t('shaxsiy_varaqasi', lang=lang, file='anketa2')}</b>", title_center_style)
        ]

        mutaxassislik_text = Paragraph(f"<b>{i18n.t('mutaxassislik', lang=lang, file='anketa2')}</b> {data.get('yonalish', '')}", normal_style)
        bottom_content = [
            mutaxassislik_text,
            Spacer(1, 2),
            fio_table
        ]

        left_inner_data = [
            [top_content],
            [bottom_content]
        ]
        
        left_inner_table = Table(left_inner_data, colWidths=[fio_total_width], rowHeights=[45, photo_height - 45])
        left_inner_table.setStyle(TableStyle([
            ('VALIGN', (0,0), (0,0), 'TOP'),
            ('VALIGN', (0,1), (0,1), 'BOTTOM'),
            ('LEFTPADDING', (0,0), (-1,-1), 0),
            ('RIGHTPADDING', (0,0), (-1,-1), 0),
            ('TOPPADDING', (0,0), (-1,-1), 0),
            ('BOTTOMPADDING', (0,0), (-1,-1), 0),
        ]))

        # --- 4. ASOSIY YONMA-YON LAYOUT ---
        top_layout_data = [[left_inner_table, photo_table]]
        top_layout_table = Table(top_layout_data, colWidths=[fio_total_width, 113.4])
        top_layout_table.setStyle(TableStyle([
            ('VALIGN', (0,0), (-1,-1), 'TOP'),
            ('LEFTPADDING', (0,0), (-1,-1), 0),
            ('RIGHTPADDING', (0,0), (-1,-1), 0),
            ('TOPPADDING', (0,0), (-1,-1), 0),
            ('BOTTOMPADDING', (0,0), (-1,-1), 0),
        ]))
        
        story.append(top_layout_table)
        story.append(Spacer(1, 4))

        # --- 5. ASOSIY RAQAMLANGAN JADVAL (1-10 bandlar) ---
        form_rows_keys = [
            ("1.", "q_tugilgan", 'tugilgan'),
            ("2.", "q_millati", 'millati'),
            ("3.", "q_malumoti", 'malumoti'),
            ("4.", "q_okishga_kirgan", 'okishga_kirgan'),
            ("5.", "q_okishga_kirgunch", 'okishga_kirgunch'),
            ("6.", "q_ota_ona", 'ota_ona'),
            ("7.", "q_ota_ona_manzl", 'ota_ona_manzl'),
            ("8.", "q_oilaviy", 'oilaviy'),
            ("9.", "q_pasport", 'pasport'),
            ("10.", "q_doimiy_manzil", 'doimiy_manzil'),
        ]

        table_data = []
        for num, key_name, data_key in form_rows_keys:
            question_text = i18n.t(key_name, lang=lang, file='anketa2')
            table_data.append([
                Paragraph(num, center_style),
                Paragraph(question_text, normal_style),
                Paragraph(str(data.get(data_key, '')), normal_style)
            ])

        main_table = Table(table_data, colWidths=[30, 165, 340])
        main_table.setStyle(TableStyle([
            ('GRID', (0,0), (-1,-1), 0.5, colors.black),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('TOPPADDING', (0,0), (-1,-1), 3),
            ('BOTTOMPADDING', (0,0), (-1,-1), 3),
            ('LEFTPADDING', (0,0), (-1,-1), 4),
            ('RIGHTPADDING', (0,0), (-1,-1), 4),
        ]))
        story.append(main_table)

        # --- 6. VAQTINCHA YASHASH MANZILLARI JADVALI ---
        ijara_rows = [
            [
                Paragraph(f"<b>{i18n.t('ijara_tr', lang=lang, file='anketa2')}</b>", center_style),
                Paragraph(f"<b>{i18n.t('ijara_manzil_title', lang=lang, file='anketa2')}</b>", normal_style),
                Paragraph(f"<b>{i18n.t('ijara_sana_title', lang=lang, file='anketa2')}</b>", center_style)
            ],
            [
                Paragraph("1.", center_style),
                Paragraph(str(data.get('ijara', '')), normal_style),
                Paragraph(str(data.get('ijara_sana', '')), center_style)
            ],
            [Paragraph("2.", center_style), "", ""],
            [Paragraph("3.", center_style), "", ""],
            [Paragraph("4.", center_style), "", ""]
        ]

        ijara_table = Table(ijara_rows, colWidths=[30, 365, 140])
        ijara_table.setStyle(TableStyle([
            ('GRID', (0,0), (-1,-1), 0.5, colors.black),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('TOPPADDING', (0,0), (-1,-1), 3),
            ('BOTTOMPADDING', (0,0), (-1,-1), 3),
            ('LEFTPADDING', (0,0), (-1,-1), 4),
            ('RIGHTPADDING', (0,0), (-1,-1), 4),
        ]))
        
        story.append(Spacer(1, 0))
        story.append(ijara_table)

        doc.build(story)
        return True

    except Exception as e:
        print(f"ReportLab orqali Anketa2 PDF yaratishda xatolik: {e}")
        return False
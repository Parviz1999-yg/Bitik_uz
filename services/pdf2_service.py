import os
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image as RLImage
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

def get_output_path(user_id: any, prefix: str = "anketa2", ext: str = "pdf") -> str:
    base_dir = os.path.dirname(os.path.abspath(__file__))
    output_path = os.path.join(base_dir, "..", "downloads", f"{prefix}_{user_id}.{ext}")
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    return output_path

def generate_pdf2_anketa(data: dict, lang: str = "uz", output_pdf_path: str = None) -> bool:
    """
    ReportLab yordamida Anketa2 shablonini yaratadi: 
    Sarlavha rasmning chap tomonida, <b> taglari to'g'ri ishlashi uchun Regular va Bold shriftlar ro'yxatdan o'tkazilgan.
    """
    try:
        if not output_pdf_path:
            user_id = data.get("tg_id") or data.get("user_id", "anketa2")
            output_pdf_path = get_output_path(user_id, prefix="anketa2", ext="pdf")

        # A4 sahifa va chekkalar (margins)
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
            
            # Agar bold shrift fayli mavjud bo'lsa, uni ham ro'yxatdan o'tkazamiz (<b> ishlashi uchun shart)
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

        # --- 1. FIO JADVALI (Ko'rinmas chiziqli) ---
        fio_total_width = 535 - 113.4  # ~421.6 pt
        col_w = fio_total_width / 3.0

        fio_data = [
            [
                Paragraph("<b>Familiya</b><br/>" + str(data.get('familiya', '')), normal_style),
                Paragraph("<b>Ismi</b><br/>" + str(data.get('ism', '')), normal_style),
                Paragraph("<b>Sharifi</b><br/>" + str(data.get('sharif', '')), normal_style)
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

        # --- 2. RASM JADVALI (Ko'rinmas chiziqli) ---
        photo_path = data.get("rasm") or data.get("user_photo")
        if photo_path and os.path.exists(photo_path):
            img_element = RLImage(photo_path, width=3.5 * 28.35, height=4.5 * 28.35)
            photo_cell = img_element
        else:
            photo_cell = Paragraph("3.5 x 4.5<br/>foto", center_style)

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

        # --- 3. CHAP TOMONGI KONTENT (Sarlavha, Mutaxassislik va FIO rasmdan chapda) ---
        talim_raw = f"{data.get('talim_muassasa', '')} {data.get('yonalish', '')} yo’nalishi<br/>{data.get('kurs', '')}-kurs talabasi"
        talim_text = f"<b>{talim_raw}</b>"
        
        mutaxassislik_text = Paragraph(f"<b>Mutaxassislik:</b> {data.get('yonalish', '')}", normal_style)

        left_cell_content = [
            Paragraph(talim_text, header_center_style),
            Spacer(1, 2),
            Paragraph("<b>SHAXSIY VARAQASI</b>", title_center_style),
            Spacer(1, 4),
            mutaxassislik_text,
            Spacer(1, 2),
            fio_table
        ]

        # --- 4. YONMA-YON LAYOUT JADVALI ---
        top_layout_data = [[left_cell_content, photo_table]]
        top_layout_table = Table(top_layout_data, colWidths=[fio_total_width, 113.4])
        top_layout_table.setStyle(TableStyle([
            ('VALIGN', (0,0), (-1,-1), 'BOTTOM'),
            ('LEFTPADDING', (0,0), (-1,-1), 0),
            ('RIGHTPADDING', (0,0), (-1,-1), 0),
            ('TOPPADDING', (0,0), (-1,-1), 0),
            ('BOTTOMPADDING', (0,0), (-1,-1), 0),
        ]))
        
        story.append(top_layout_table)
        story.append(Spacer(1, 4))

        # 5. Asosiy raqamlangan jadval (1-10 bandlar)
        form_rows = [
            ["1.", "Tug’ilgan yili joyi sanasi", data.get('tugilgan', '')],
            ["2.", "Millati", data.get('millati', '')],
            ["3.", "Ma’lumoti (maktab, Al, kxk yoki boshqa o’quv yurti, nomi, tugatgan yili)", data.get('malumoti', '')],
            ["4.", "O’qishga kirgan sanasi, buyruq nomeri", data.get('okishga_kirgan', '')],
            ["5.", "O’qishga kirgunga qadar ish joyi, mansabi (agar ishlagan bo’lsa)", data.get('okishga_kirgunch', '')],
            ["6.", "Ota-ona haqida ma’lumot (F.I.SH, qayerda, kim bo’lib ishlaydi, telefoni)", data.get('ota_ona', '')],
            ["7.", "Ota-onasining yashash manzili, telefoni", data.get('ota_ona_manzl', '')],
            ["8.", "Talabaning oilaviy ahvoli (turmush o’rtog’ining F.I.SH. qayerda, kim bo’lib ishlaydi, telefoni)", data.get('oilaviy', '')],
            ["9.", "Pasport seriyasi, raqami, kim tomonidan, qachon berilgan", data.get('pasport', '')],
            ["10.", "Talabaning doimiy yashash joyi (pasport bo’yicha doimiy ro’yxatga qo’yilgan joyi va vaqti)", data.get('doimiy_manzil', '')],
        ]

        table_data = []
        for row in form_rows:
            table_data.append([
                Paragraph(row[0], center_style),
                Paragraph(row[1], normal_style),
                Paragraph(str(row[2]), normal_style)
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

        # 6. Vaqtincha yashash manzillari jadvali
        ijara_rows = [
            [
                Paragraph("<b>T/R</b>", center_style),
                Paragraph("<b>Talabaning vaqtincha yashash manzili (talabalar turar joyi, ijara uy, yaqin qarindoshlarning uy manzili va telefon raqamlari)</b>", normal_style),
                Paragraph("<b>Ro’yxatdan o’tkazilgan sana</b>", center_style)
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
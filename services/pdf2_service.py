import os
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image as RLImage
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

def get_output_path(user_id: any, prefix: str = "anketa2", ext: str = "pdf") -> str:
    base_dir = os.path.dirname(os.path.abspath(__file__))
    output_path = os.path.join(base_dir, "..", "downloads", f"{prefix}_{user_id}.{ext}")
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    return output_path

def generate_pdf2_anketa(data: dict, lang: str, output_pdf_path: str = None) -> bool:
    """
    ReportLab yordamida Anketa2 shablonini mukammal va xatosiz PDF formatida yaratadi.
    """
    try:
        # 1. Chiqish fayl yo'lini aniqlash[cite: 4]
        if not output_pdf_path:
            user_id = data.get("tg_id") or data.get("user_id", "anketa2")
            output_pdf_path = get_output_path(user_id, prefix="anketa2", ext="pdf")

        # 2. A4 sahifa o'lchamlari va chekkalari (marginlar)[cite: 4]
        doc = SimpleDocTemplate(
            output_pdf_path,
            pagesize=A4,
            leftMargin=28.3,   # ~10mm
            rightMargin=28.3,
            topMargin=22.6,    # ~8mm
            bottomMargin=22.6
        )
        
        story = []

        # 3. Times New Roman shriftini ro'yxatdan o'tkazish[cite: 4]
        base_dir = os.path.dirname(os.path.abspath(__file__))
        font_path = os.path.join(base_dir, "..", "fonts", "times.ttf")
        
        if os.path.exists(font_path):
            pdfmetrics.registerFont(TTFont('TimesNewRoman', font_path))
            font_name = 'TimesNewRoman'
        else:
            font_name = 'Helvetica'

        # Stillarni aniqlash[cite: 4]
        header_style = ParagraphStyle(
            'HeaderStyle',
            fontName=font_name,
            fontSize=10,
            leading=12,
            alignment=1, # Center
            textColor=colors.black
        )
        
        title_style = ParagraphStyle(
            'TitleStyle',
            fontName=font_name,
            fontSize=11.5,
            leading=14,
            alignment=1,
            textColor=colors.black
        )
        
        normal_style = ParagraphStyle(
            'NormalStyle',
            fontName=font_name,
            fontSize=9,
            leading=11.5,
            textColor=colors.black
        )

        center_style = ParagraphStyle(
            'CenterStyle',
            fontName=font_name,
            fontSize=9,
            leading=11.5,
            alignment=1,
            textColor=colors.black
        )

        # 4. Yuqori qism (Talim muassasa, yo'nalish, kurs va SHAXSIY VARAQASI)[cite: 4]
        talim_text = f"{data.get('talim_muassasa', '')} {data.get('yonalish', '')} yo’nalishi<br/>{data.get('kurs', '')}-kurs talabasi"
        
        # Foydalanuvchi rasmini yuklash (3.5cm x 4.5cm)[cite: 4]
        photo_path = data.get("rasm") or data.get("user_photo")
        img_element = ""
        if photo_path and os.path.exists(photo_path):
            img_element = RLImage(photo_path, width=99, height=127)

        top_left_content = [
            Paragraph(talim_text, header_style),
            Spacer(1, 4),
            Paragraph("<b>SHAXSIY VARAQASI</b>", title_style),
            Spacer(1, 6),
            Paragraph(f"<b>Mutaxassislik:</b> {data.get('yonalish', '')}", normal_style),
            Spacer(1, 6)
        ]

        # Familiya | Ismi | Sharifi kichik jadvali[cite: 4]
        fio_data = [
            [
                Paragraph("<b>Familiya</b><br/>" + str(data.get('familiya', '')), normal_style),
                Paragraph("<b>Ismi</b><br/>" + str(data.get('ism', '')), normal_style),
                Paragraph("<b>Sharifi</b><br/>" + str(data.get('sharif', '')), normal_style)
            ]
        ]
        fio_table = Table(fio_data, colWidths=[130, 130, 140])
        fio_table.setStyle(TableStyle([
            ('VALIGN', (0,0), (-1,-1), 'TOP'),
            ('TOPPADDING', (0,0), (-1,-1), 0),
            ('BOTTOMPADDING', (0,0), (-1,-1), 0),
            ('LEFTPADDING', (0,0), (-1,-1), 0),
            ('RIGHTPADDING', (0,0), (-1,-1), 0),
        ]))
        
        top_left_content.append(fio_table)

        # Yuqori blok jadvali (Chapda matnlar, o'ngda rasm)[cite: 4]
        top_table_data = [[top_left_content, img_element if img_element else ""]]
        top_table = Table(top_table_data, colWidths=[415, 120])
        top_table.setStyle(TableStyle([
            ('VALIGN', (0,0), (-1,-1), 'TOP'),
            ('LEFTPADDING', (0,0), (-1,-1), 0),
            ('RIGHTPADDING', (0,0), (-1,-1), 0),
            ('BOTTOMPADDING', (0,0), (-1,-1), 0),  # <-- Ortiqcha bo'shliq olib tashlandi
        ]))
        
        # Yuqori qism story'ga qo'shiladi[cite: 4]
        story.append(top_table)
        
        # ORADAGI SPACER BUTUNLAY OLIB TASHLANDI (Oraliq bo'shliq yo'q)[cite: 4]

        # 5. Asosiy raqamlangan jadval (1-dan 10-gacha) to'g'ridan-to'g'ri ostiga tushadi[cite: 4]
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
            ('TOPPADDING', (0,0), (-1,-1), 3.5),
            ('BOTTOMPADDING', (0,0), (-1,-1), 3.5),
            ('LEFTPADDING', (0,0), (-1,-1), 5),
            ('RIGHTPADDING', (0,0), (-1,-1), 5),
        ]))
        story.append(main_table)

        # 6. Vaqtincha yashash manzillari jadvali[cite: 2, 4]
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
            ('TOPPADDING', (0,0), (-1,-1), 3.5),
            ('BOTTOMPADDING', (0,0), (-1,-1), 3.5),
            ('LEFTPADDING', (0,0), (-1,-1), 5),
            ('RIGHTPADDING', (0,0), (-1,-1), 5),
        ]))
        
        story.append(Spacer(1, 0))
        story.append(ijara_table)

        # 7. PDF faylni yig'ish va saqlash[cite: 4]
        doc.build(story)
        return True

    except Exception as e:
        print(f"ReportLab orqali Anketa2 PDF yaratishda xatolik: {e}")
        return False
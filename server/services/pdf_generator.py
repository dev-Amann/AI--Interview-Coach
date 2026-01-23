from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY, TA_RIGHT
from io import BytesIO
from datetime import datetime

def generate_interview_report(report_data):
    buffer = BytesIO()
    
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=40,
        leftMargin=40,
        topMargin=40,
        bottomMargin=40
    )
    
    styles = getSampleStyleSheet()
    
    # Define primary colors (Modern Indigo/Violet palette)
    PRIMARY = colors.HexColor('#4F46E5')     # Indigo 600
    SECONDARY = colors.HexColor('#7C3AED')   # Violet 600
    SUCCESS = colors.HexColor('#059669')     # Emerald 600
    WARNING = colors.HexColor('#D97706')     # Amber 600
    DANGER = colors.HexColor('#DC2626')      # Red 600
    TEXT_MAIN = colors.HexColor('#111827')   # Gray 900
    TEXT_MUTED = colors.HexColor('#6B7280')  # Gray 500
    BG_LIGHT = colors.HexColor('#F9FAFB')    # Gray 50
    BORDER = colors.HexColor('#E5E7EB')      # Gray 200

    # Custom Styles
    title_style = ParagraphStyle(
        'PremiumTitle',
        parent=styles['Heading1'],
        fontSize=28,
        textColor=PRIMARY,
        alignment=TA_CENTER,
        spaceAfter=10,
        fontName='Helvetica-Bold'
    )
    
    subtitle_style = ParagraphStyle(
        'PremiumSubtitle',
        parent=styles['Normal'],
        fontSize=12,
        textColor=TEXT_MUTED,
        alignment=TA_CENTER,
        spaceAfter=30
    )
    
    card_label_style = ParagraphStyle(
        'CardLabel',
        fontSize=9,
        textColor=TEXT_MUTED,
        fontName='Helvetica-Bold',
        alignment=TA_CENTER,
        spaceAfter=2
    )
    
    card_value_style = ParagraphStyle(
        'CardValue',
        fontSize=12,
        textColor=TEXT_MAIN,
        fontName='Helvetica-Bold',
        alignment=TA_CENTER
    )
    
    section_title_style = ParagraphStyle(
        'SectionTitle',
        parent=styles['Heading2'],
        fontSize=16,
        textColor=TEXT_MAIN,
        spaceBefore=25,
        spaceAfter=15,
        borderPadding=5,
        fontName='Helvetica-Bold'
    )
    
    question_style = ParagraphStyle(
        'Question',
        parent=styles['Normal'],
        fontSize=11,
        textColor=TEXT_MAIN,
        fontName='Helvetica-Bold',
        spaceAfter=6,
        leading=14
    )
    
    answer_box_style = ParagraphStyle(
        'AnswerBox',
        parent=styles['Normal'],
        fontSize=10,
        textColor=colors.HexColor('#374151'),
        leftIndent=10,
        rightIndent=10,
        spaceBefore=5,
        spaceAfter=10,
        leading=14
    )
    
    feedback_style = ParagraphStyle(
        'Feedback',
        parent=styles['Normal'],
        fontSize=10,
        textColor=TEXT_MAIN,
        leftIndent=10,
        leading=14
    )

    elements = []
    
    # 1. HEADER
    elements.append(Paragraph("🎯 AI Interview Coach", title_style))
    elements.append(Paragraph(f"Performance Report • {datetime.now().strftime('%B %d, %Y')}", subtitle_style))
    
    # 2. METRICS CARDS (Summary Section)
    avg_score = report_data.get('avg_score', 0)
    score_color = DANGER if avg_score < 5 else WARNING if avg_score < 7 else SUCCESS
    
    metric_cards_data = [
        [
            Paragraph("ROLE", card_label_style),
            Paragraph("CATEGORY", card_label_style),
            Paragraph("SCORE", card_label_style),
            Paragraph("STATUS", card_label_style)
        ],
        [
            Paragraph(report_data.get('job_role', 'N/A'), card_value_style),
            Paragraph(report_data.get('category', 'Technical'), card_value_style),
            Paragraph(f"<font color={score_color.hexval()}>{avg_score:.1f}/10</font>", card_value_style),
            Paragraph(
                "PASSED" if report_data.get('qualified', False) else "PRACTICE", 
                ParagraphStyle('status', parent=card_value_style, textColor=score_color)
            )
        ]
    ]
    
    metrics_table = Table(metric_cards_data, colWidths=[130, 130, 130, 130])
    metrics_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), BG_LIGHT),
        ('BOX', (0, 0), (-1, -1), 1, BORDER),
        ('GRID', (0, 0), (-1, -1), 0.5, BORDER),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 12),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
    ]))
    elements.append(metrics_table)
    elements.append(Spacer(1, 25))
    
    # 3. QUESTION ANALYSIS
    elements.append(Paragraph("Detailed Question Analysis", section_title_style))
    
    questions = report_data.get('questions', [])
    answers = report_data.get('answers', {})
    scores = report_data.get('scores', [])
    feedback_list = report_data.get('feedback_list', [])
    ideal_answers_list = report_data.get('ideal_answers_list', [])
    
    for i, question in enumerate(questions):
        score = scores[i] if i < len(scores) else 0
        ans_text = answers.get(i, 'No answer provided')
        fb_text = feedback_list[i] if i < len(feedback_list) else 'N/A'
        ideal_text = ideal_answers_list[i] if i < len(ideal_answers_list) else 'N/A'
        
        q_score_color = DANGER if score < 5 else WARNING if score < 7 else SUCCESS
        
        # Question Header Card
        q_header_data = [[
            Paragraph(f"QUESTION {i+1}", ParagraphStyle('qh', fontSize=9, fontName='Helvetica-Bold', textColor=PRIMARY)),
            Paragraph(f"SCORE: {score}/10", ParagraphStyle('qs', fontSize=9, fontName='Helvetica-Bold', textColor=q_score_color, alignment=TA_RIGHT))
        ]]
        q_header_table = Table(q_header_data, colWidths=[260, 260])
        q_header_table.setStyle(TableStyle([
            ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
            ('TOPPADDING', (0, 0), (-1, -1), 2),
        ]))
        elements.append(q_header_table)
        
        # The Question itself
        elements.append(Paragraph(question, question_style))
        
        # Response & Feedback Card
        response_data = [
            [Paragraph("<b>YOUR RESPONSE:</b>", ParagraphStyle('rl', fontSize=8, textColor=TEXT_MUTED))],
            [Paragraph(str(ans_text), answer_box_style)],
            [Paragraph("<b>COACH FEEDBACK:</b>", ParagraphStyle('rl', fontSize=8, textColor=TEXT_MUTED))],
            [Paragraph(fb_text, feedback_style)],
            [Spacer(1, 10)],
            [Paragraph("<b>💡 IDEAL ANSWER:</b>", ParagraphStyle('rl', fontSize=8, textColor=SUCCESS))],
            [Paragraph(f'<font color="{SUCCESS.hexval()}">{ideal_text}</font>', ParagraphStyle('ideal', parent=answer_box_style, backColor=colors.HexColor('#ECFDF5')))]
        ]
        
        response_table = Table(response_data, colWidths=[520])
        response_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.white),
            ('BOX', (0, 0), (-1, -1), 0.5, BORDER),
            ('TOPPADDING', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
            ('LEFTPADDING', (0, 0), (-1, -1), 15),
            ('RIGHTPADDING', (0, 0), (-1, -1), 15),
        ]))
        
        elements.append(response_table)
        elements.append(Spacer(1, 20))

    # 4. RECOMMENDATIONS
    elements.append(Paragraph("Expert Recommendations", section_title_style))
    rec_box_data = []
    
    if avg_score < 5:
        recs = ["Focus on fundamental concepts and definitions.", "Practice coding daily on basic problem sets.", "Review the core requirements of the job role."]
    elif avg_score < 7:
        recs = ["Elaborate more on your past projects as examples.", "Prepare better for behavioral scenarios (STAR method).", "Try explaining technical concepts to a non-technical person."]
    else:
        recs = ["Excellent foundation! Aim for senior-level depth in answers.", "Keep up with the latest trends in the industry.", "Polish your delivery and confidence further."]
        
    for rec in recs:
        rec_box_data.append([Paragraph(f"• {rec}", ParagraphStyle('rec', fontSize=10, textColor=TEXT_MAIN, leading=14))])
        
    rec_table = Table(rec_box_data, colWidths=[520])
    rec_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), BG_LIGHT),
        ('BOX', (0, 0), (-1, -1), 0.5, BORDER),
        ('TOPPADDING', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
        ('LEFTPADDING', (0, 0), (-1, -1), 15),
    ]))
    elements.append(rec_table)
    
    # 5. FOOTER
    elements.append(Spacer(1, 40))
    elements.append(HRFlowable(width="100%", thickness=1, color=BORDER))
    elements.append(Spacer(1, 10))
    elements.append(Paragraph(
        f"Automated Assessment Report • Generated by AI Interview Coach • {datetime.now().strftime('%d %b %Y %H:%M')}",
        ParagraphStyle('Footer', fontSize=8, textColor=TEXT_MUTED, alignment=TA_CENTER)
    ))

    doc.build(elements)
    
    pdf_bytes = buffer.getvalue()
    buffer.close()
    
    return pdf_bytes

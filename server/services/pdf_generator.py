from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from io import BytesIO
from datetime import datetime

def generate_interview_report(report_data):
    buffer = BytesIO()
    
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=50,
        leftMargin=50,
        topMargin=50,
        bottomMargin=50
    )
    
    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        spaceAfter=20,
        alignment=TA_CENTER,
        textColor=colors.HexColor('#6366f1')
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=14,
        spaceAfter=10,
        spaceBefore=15,
        textColor=colors.HexColor('#8b5cf6')
    )
    
    subheading_style = ParagraphStyle(
        'CustomSubheading',
        parent=styles['Heading3'],
        fontSize=12,
        spaceAfter=8,
        textColor=colors.HexColor('#334155')
    )
    
    body_style = ParagraphStyle(
        'CustomBody',
        parent=styles['Normal'],
        fontSize=10,
        spaceAfter=8,
        alignment=TA_JUSTIFY,
        textColor=colors.HexColor('#475569')
    )
    
    small_style = ParagraphStyle(
        'SmallText',
        parent=styles['Normal'],
        fontSize=9,
        textColor=colors.HexColor('#64748b')
    )
    
    elements = []
    
    elements.append(Paragraph("🎯 AI Interview Coach", title_style))
    elements.append(Paragraph("Interview Performance Report", ParagraphStyle(
        'Subtitle',
        parent=styles['Normal'],
        fontSize=14,
        alignment=TA_CENTER,
        textColor=colors.HexColor('#94a3b8'),
        spaceAfter=30
    )))
    
    elements.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#e2e8f0')))
    elements.append(Spacer(1, 20))
    
    job_role = report_data.get('job_role', 'N/A')
    category = report_data.get('category', 'Technical')
    difficulty = report_data.get('difficulty', 'Medium')
    avg_score = report_data.get('avg_score', 0)
    qualified = report_data.get('qualified', False)
    
    info_data = [
        ['Job Role:', job_role, 'Date:', datetime.now().strftime('%B %d, %Y')],
        ['Category:', category, 'Difficulty:', difficulty],
        ['Avg Score:', f"{avg_score:.1f}/10", 'Status:', '✅ QUALIFIED' if qualified else '❌ NEEDS PRACTICE']
    ]
    
    info_table = Table(info_data, colWidths=[80, 150, 80, 150])
    info_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#64748b')),
        ('TEXTCOLOR', (2, 0), (2, -1), colors.HexColor('#64748b')),
        ('TEXTCOLOR', (1, 0), (1, -1), colors.HexColor('#1e293b')),
        ('TEXTCOLOR', (3, 0), (3, -1), colors.HexColor('#1e293b')),
        ('FONTNAME', (1, 0), (1, -1), 'Helvetica-Bold'),
        ('FONTNAME', (3, 0), (3, -1), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
    ]))
    
    elements.append(info_table)
    elements.append(Spacer(1, 20))
    
    score_color = colors.HexColor('#22c55e') if avg_score >= 7 else colors.HexColor('#eab308') if avg_score >= 5 else colors.HexColor('#ef4444')
    
    score_data = [
        [Paragraph(f"<font size='24' color='#{score_color.hexval()[2:]}'><b>{avg_score:.1f}</b></font>", 
                   ParagraphStyle('score', alignment=TA_CENTER))],
        [Paragraph("Overall Score out of 10", ParagraphStyle('label', alignment=TA_CENTER, textColor=colors.HexColor('#64748b')))]
    ]
    
    score_table = Table(score_data, colWidths=[200])
    score_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#f8fafc')),
        ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#e2e8f0')),
        ('TOPPADDING', (0, 0), (-1, -1), 15),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 15),
    ]))
    
    elements.append(score_table)
    elements.append(Spacer(1, 30))
    
    elements.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#e2e8f0')))
    elements.append(Paragraph("📋 Question-by-Question Analysis", heading_style))
    
    questions = report_data.get('questions', [])
    answers = report_data.get('answers', {})
    scores = report_data.get('scores', [])
    feedback_list = report_data.get('feedback_list', [])
    ideal_answers_list = report_data.get('ideal_answers_list', [])
    
    for i, question in enumerate(questions):
        score = scores[i] if i < len(scores) else 0
        answer = answers.get(i, 'No answer provided')
        feedback = feedback_list[i] if i < len(feedback_list) else 'N/A'
        ideal = ideal_answers_list[i] if i < len(ideal_answers_list) else 'N/A'
        
        score_color_hex = '#22c55e' if score >= 7 else '#eab308' if score >= 5 else '#ef4444'
        
        elements.append(Spacer(1, 15))
        
        q_header = f"<b>Question {i+1}</b> <font color='{score_color_hex}'>[Score: {score}/10]</font>"
        elements.append(Paragraph(q_header, subheading_style))
        
        elements.append(Paragraph(f"<i>{question}</i>", body_style))
        elements.append(Spacer(1, 5))
        
        elements.append(Paragraph("<b>Your Answer:</b>", small_style))
        elements.append(Paragraph(str(answer), body_style))
        
        elements.append(Paragraph("<b>Feedback:</b>", small_style))
        elements.append(Paragraph(feedback, body_style))
        
        elements.append(Paragraph("<b>💡 Ideal Answer:</b>", small_style))
        elements.append(Paragraph(ideal, ParagraphStyle(
            'IdealAnswer',
            parent=body_style,
            textColor=colors.HexColor('#059669'),
            backColor=colors.HexColor('#ecfdf5'),
            borderPadding=8
        )))
        
        elements.append(Spacer(1, 10))
        elements.append(HRFlowable(width="80%", thickness=0.5, color=colors.HexColor('#e2e8f0')))
    
    elements.append(Spacer(1, 30))
    elements.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#e2e8f0')))
    elements.append(Paragraph("💡 Recommendations", heading_style))
    
    if avg_score < 5:
        recommendations = [
            "📚 Focus on strengthening fundamental concepts",
            "🎯 Practice with more questions at easier difficulty first",
            "✍️ Write out detailed answers to reinforce learning"
        ]
    elif avg_score < 7:
        recommendations = [
            "✨ Good foundation! Add more specific examples from experience",
            "🔍 Dive deeper into advanced topics",
            "💬 Practice articulating your thoughts clearly"
        ]
    else:
        recommendations = [
            "🌟 Excellent performance! Keep up the great work",
            "🚀 Challenge yourself with harder difficulty levels",
            "🎤 Consider mock interviews for additional practice"
        ]
    
    for rec in recommendations:
        elements.append(Paragraph(f"• {rec}", body_style))
    
    elements.append(Spacer(1, 30))
    elements.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#e2e8f0')))
    elements.append(Spacer(1, 10))
    elements.append(Paragraph(
        f"Generated by AI Interview Coach on {datetime.now().strftime('%B %d, %Y at %I:%M %p')}",
        ParagraphStyle('Footer', alignment=TA_CENTER, fontSize=8, textColor=colors.HexColor('#94a3b8'))
    ))
    
    doc.build(elements)
    
    pdf_bytes = buffer.getvalue()
    buffer.close()
    
    return pdf_bytes

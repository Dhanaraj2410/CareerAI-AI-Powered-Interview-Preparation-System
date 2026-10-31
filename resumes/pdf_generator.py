"""
CareerAI Resume PDF Generation Engine
-------------------------------------
Generates ATS-compliant, beautifully styled PDF resumes using ReportLab Platypus.
"""

import io
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT

def generate_resume_pdf(resume_obj):
    """
    Builds a professional, ATS-formatted PDF for a Resume model instance.
    Returns bytes buffer.
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=40,
        leftMargin=40,
        topMargin=40,
        bottomMargin=40
    )

    styles = getSampleStyleSheet()
    
    # Custom styles
    name_style = ParagraphStyle(
        'ResumeName',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=20,
        leading=24,
        textColor=colors.HexColor('#0f172a'),
        alignment=TA_CENTER
    )

    contact_style = ParagraphStyle(
        'ResumeContact',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9.5,
        leading=13,
        textColor=colors.HexColor('#475569'),
        alignment=TA_CENTER
    )

    section_header_style = ParagraphStyle(
        'ResumeSection',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=12,
        leading=16,
        textColor=colors.HexColor('#1e40af'),
        spaceAfter=4,
        spaceBefore=10
    )

    body_style = ParagraphStyle(
        'ResumeBody',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9.5,
        leading=14,
        textColor=colors.HexColor('#1e293b')
    )

    bullet_style = ParagraphStyle(
        'ResumeBullet',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9.5,
        leading=13.5,
        textColor=colors.HexColor('#334155'),
        leftIndent=15
    )

    elements = []

    user = resume_obj.user
    full_name = f"{user.first_name} {user.last_name}".strip() or user.username
    email = user.email or f"{user.username}@example.com"
    phone = getattr(getattr(user, 'profile', None), 'phone', '')
    target_role = getattr(getattr(user, 'profile', None), 'target_role', 'Software Professional')

    # Header
    elements.append(Paragraph(full_name.upper(), name_style))
    elements.append(Spacer(1, 4))
    
    contact_parts = [email]
    if phone:
        contact_parts.append(phone)
    contact_parts.append(f"Target: {target_role}")
    elements.append(Paragraph(" &bull; ".join(contact_parts), contact_style))
    elements.append(Spacer(1, 10))
    elements.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor('#3b82f6'), spaceBefore=2, spaceAfter=10))

    # Professional Summary / Objective
    if resume_obj.objective:
        elements.append(Paragraph("PROFESSIONAL SUMMARY", section_header_style))
        elements.append(Paragraph(resume_obj.objective, body_style))
        elements.append(Spacer(1, 8))

    # Technical Skills
    if resume_obj.skills:
        elements.append(Paragraph("TECHNICAL SKILLS", section_header_style))
        skills_formatted = " &bull; ".join([s.strip() for s in resume_obj.skills.split(',') if s.strip()])
        elements.append(Paragraph(skills_formatted, body_style))
        elements.append(Spacer(1, 8))

    # Experience
    if resume_obj.experience:
        elements.append(Paragraph("WORK EXPERIENCE", section_header_style))
        for line in resume_obj.experience.split('\n'):
            line = line.strip()
            if line:
                if line.startswith(('-', '*', '•')):
                    elements.append(Paragraph(f"&bull; {line.lstrip('-*• ').strip()}", bullet_style))
                else:
                    elements.append(Paragraph(f"<b>{line}</b>", body_style))
        elements.append(Spacer(1, 8))

    # Projects
    if resume_obj.projects:
        elements.append(Paragraph("KEY PROJECTS", section_header_style))
        for line in resume_obj.projects.split('\n'):
            line = line.strip()
            if line:
                if line.startswith(('-', '*', '•')):
                    elements.append(Paragraph(f"&bull; {line.lstrip('-*• ').strip()}", bullet_style))
                else:
                    elements.append(Paragraph(f"<b>{line}</b>", body_style))
        elements.append(Spacer(1, 8))

    # Education
    if resume_obj.education:
        elements.append(Paragraph("EDUCATION & CREDENTIALS", section_header_style))
        for line in resume_obj.education.split('\n'):
            line = line.strip()
            if line:
                elements.append(Paragraph(line, body_style))
        elements.append(Spacer(1, 8))

    doc.build(elements)
    buffer.seek(0)
    return buffer.getvalue()


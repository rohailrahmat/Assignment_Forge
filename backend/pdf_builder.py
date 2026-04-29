from reportlab.lib.pagesizes import LETTER
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib.units import inch
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import os

def build_pdf(content: dict, output_path: str):
    doc = SimpleDocTemplate(
        output_path,
        pagesize=LETTER,
        rightMargin=72,
        leftMargin=72,
        topMargin=72,
        bottomMargin=72
    )

    styles = getSampleStyleSheet()
    
    # Premium Color Palette
    PRIMARY = colors.HexColor("#0F172A")    # Deep Slate/Navy
    SECONDARY = colors.HexColor("#334155")  # Slate
    ACCENT = colors.HexColor("#4F46E5")     # Indigo
    LIGHT_BG = colors.HexColor("#F8FAFC")
    BORDER = colors.HexColor("#E2E8F0")

    # Custom Styles
    title_style = ParagraphStyle(
        'TitleStyle',
        parent=styles['Heading1'],
        fontSize=28,
        alignment=1,
        spaceAfter=30,
        textColor=PRIMARY,
        fontName='Helvetica-Bold'
    )
    
    header_style = ParagraphStyle(
        'HeaderStyle',
        parent=styles['Normal'],
        fontSize=16,
        spaceBefore=20,
        spaceAfter=12,
        fontName='Helvetica-Bold',
        textColor=PRIMARY,
        borderPadding=5,
        leading=20
    )
    
    normal_style = ParagraphStyle(
        'NormalStyle',
        parent=styles['Normal'],
        fontSize=11,
        leading=16,
        fontName='Helvetica',
        textColor=SECONDARY,
        alignment=4 # Justified
    )

    label_style = ParagraphStyle(
        'LabelStyle',
        parent=normal_style,
        fontName='Helvetica-Bold',
        textColor=PRIMARY
    )

    elements = []

    # Cover Page
    elements.append(Spacer(1, 2*inch))
    elements.append(Paragraph(content.get("title", "Assignment"), title_style))
    elements.append(Spacer(1, 0.5*inch))
    
    meta_data = [
        ["Student Name:", content.get("student_name", "")],
        ["Course:", content.get("course", "")],
        ["Instructor:", content.get("instructor", "TBD")],
        ["Due Date:", content.get("due_date", "")]
    ]
    
    t = Table(meta_data, colWidths=[1.5*inch, 3*inch])
    t.setStyle(TableStyle([
        ('FONTNAME', (0,0), (0,-1), 'Helvetica-Bold'),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('TEXTCOLOR', (0,0), (-1,-1), colors.black),
        ('FONTSIZE', (0,0), (-1,-1), 12),
        ('TOPPADDING', (0,0), (-1,-1), 6),
    ]))
    elements.append(t)
    elements.append(PageBreak())

    # Content Sections
    for section in content.get("sections", []):
        elements.append(Paragraph(section.get("heading", ""), header_style))
        elements.append(Spacer(1, 6))
        
        for item in section.get("content", []):
            itype = item.get("type")
            
            if itype == "paragraph":
                label = item.get("label", "")
                text = item.get("text", "")
                
                # Check for image[[...]] syntax
                import re
                img_match = re.search(r'image\[\[(.*?)\]\]', text)
                if img_match:
                    data = [[Paragraph(f"<b>📷 IMAGE PLACEHOLDER [[{img_match.group(1)}]]</b>", normal_style), ""]]
                    table = Table(data, colWidths=[doc.width, 0])
                    table.setStyle(TableStyle([
                        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#F8F9FA")),
                        ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#6382FF")),
                        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
                        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
                        ('TOPPADDING', (0,0), (-1,-1), 15),
                        ('BOTTOMPADDING', (0,0), (-1,-1), 15),
                    ]))
                    elements.append(table)
                    elements.append(Spacer(1, 10))
                    continue

                # Check for # Subheading syntax
                if text.startswith("# "):
                    elements.append(Paragraph(text.replace("# ", "").upper(), header_style))
                    elements.append(Spacer(1, 6))
                    continue

                full_text = f"<b>{label}:</b> {text}" if label else text
                elements.append(Paragraph(full_text, normal_style))
                elements.append(Spacer(1, 10))
                
            elif itype == "field":
                elements.append(Paragraph(f"<b>{item.get('label')}:</b> {item.get('value')}", normal_style))
                elements.append(Spacer(1, 8))
                
            elif itype in ["bullet_list", "numbered_list"]:
                label = item.get("label")
                if label:
                    elements.append(Paragraph(f"<b>{label}</b>", normal_style))
                
                for i, li in enumerate(item.get("items", []), 1):
                    prefix = f"{i}. " if itype == "numbered_list" else "• "
                    elements.append(Paragraph(f"{prefix}{li}", normal_style, leftIndent=20))
                elements.append(Spacer(1, 10))

            elif itype == "grid_table":
                headers = item.get("headers", [])
                rows = item.get("rows", [])
                if headers:
                    data = [headers] + rows
                    col_width = (doc.width) / len(headers)
                    table = Table(data, colWidths=[col_width]*len(headers))
                    
                    # Premium Table Styling
                    style_list = [
                        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#1E293B")), # Deep header
                        ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
                        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
                        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
                        ('FONTSIZE', (0,0), (-1,0), 10),
                        ('BOTTOMPADDING', (0,0), (-1,0), 12),
                        ('TOPPADDING', (0,0), (-1,0), 12),
                        
                        ('FONTNAME', (0,1), (-1,-1), 'Helvetica'),
                        ('FONTSIZE', (0,1), (-1,-1), 9),
                        ('BOTTOMPADDING', (0,1), (-1,-1), 10),
                        ('TOPPADDING', (0,1), (-1,-1), 10),
                        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#E2E8F0")),
                        ('VALIGN', (0,0), (-1,-1), 'TOP'),
                        ('LEFTPADDING', (0,0), (-1,-1), 10),
                        ('RIGHTPADDING', (0,0), (-1,-1), 10),
                    ]
                    
                    # Alternate row colors
                    for i in range(1, len(data)):
                        if i % 2 == 0:
                            style_list.append(('BACKGROUND', (0,i), (-1,i), colors.HexColor("#F8FAFC")))
                    
                    table.setStyle(TableStyle(style_list))
                    elements.append(table)
                    elements.append(Spacer(1, 20))

            elif itype == "pros_cons_table":
                pros = item.get("pros", [])
                cons = item.get("cons", [])
                data = [["Pros", "Cons"]]
                for i in range(max(len(pros), len(cons))):
                    p = pros[i] if i < len(pros) else ""
                    c = cons[i] if i < len(cons) else ""
                    data.append([p, c])
                
                table = Table(data, colWidths=[doc.width/2.0]*2)
                table.setStyle(TableStyle([
                    ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#16213E")),
                    ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
                    ('ALIGN', (0,0), (-1,-1), 'LEFT'),
                    ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
                    ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
                    ('PADDING', (0,0), (-1,-1), 6),
                ]))
                elements.append(table)
                elements.append(Spacer(1, 15))

            elif itype == "image_placeholder":
                label = item.get("label", "Screenshot Placeholder")
                desc = item.get("description", "Insert relevant screenshot here")
                
                data = [[Paragraph(f"<b>📷 {label.upper()}</b>", normal_style), ""],
                        [Paragraph(desc, normal_style), ""],
                        [Paragraph(f"<i><b>PRO TIP:</b> {item.get('hint', 'Ensure the screenshot captures the navigation menu and main content stream for full context.')}</i>", normal_style), ""]]
                
                table = Table(data, colWidths=[doc.width, 0])
                table.setStyle(TableStyle([
                    ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#F1F5F9")),
                    ('BOX', (0,0), (-1,-1), 1.5, colors.HexColor("#4F46E5")),
                    ('ALIGN', (0,0), (-1,-1), 'CENTER'),
                    ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
                    ('TOPPADDING', (0,0), (-1,-1), 15),
                    ('BOTTOMPADDING', (0,0), (-1,-1), 15),
                    ('LEFTPADDING', (0,0), (-1,-1), 20),
                    ('RIGHTPADDING', (0,0), (-1,-1), 20),
                ]))
                elements.append(table)
                elements.append(Spacer(1, 15))

            elif itype == "checklist_table":
                data = [["Item", "Completed"]]
                for check in item.get("items", []):
                    data.append([check, "[ ]"])
                
                table = Table(data, colWidths=[4*inch, 1*inch])
                table.setStyle(TableStyle([
                    ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#1A1A2E")),
                    ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
                    ('ALIGN', (0,0), (-1,-1), 'LEFT'),
                    ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
                    ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
                    ('PADDING', (0,0), (-1,-1), 6),
                ]))
                elements.append(table)
                elements.append(Spacer(1, 15))

            elif itype == "influencer_table":
                influencers = item.get("influencers", [])
                if influencers:
                    data = [["Influencer", "Platform", "Handle", "Followers", "Fit Score"]]
                    for inf in influencers:
                        data.append([inf.get("name"), inf.get("platform"), inf.get("handle"), inf.get("followers"), inf.get("fit_score")])
                    
                    table = Table(data, colWidths=[1.2*inch, 0.8*inch, 1*inch, 0.8*inch, 0.8*inch])
                    table.setStyle(TableStyle([
                        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#4F46E5")),
                        ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
                        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
                        ('FONTSIZE', (0,0), (-1,-1), 8),
                        ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
                    ]))
                    elements.append(table)
                    elements.append(Spacer(1, 15))

            elif itype == "outreach_message":
                elements.append(Paragraph(f"<b>OUTREACH MESSAGE ({item.get('platform')}):</b>", normal_style))
                elements.append(Paragraph(f"<b>Subject:</b> {item.get('subject')}", normal_style))
                elements.append(Spacer(1, 4))
                
                msg_style = ParagraphStyle('MsgStyle', parent=normal_style, leftIndent=15, fontName='Helvetica-Oblique', textColor=colors.HexColor("#1E293B"))
                elements.append(Paragraph(item.get("message"), msg_style))
                elements.append(Spacer(1, 15))

    def add_page_elements(canvas, doc):
        canvas.saveState()
        
        # Draw Page Border
        canvas.setStrokeColor(colors.HexColor("#E2E8F0"))
        canvas.setLineWidth(0.5)
        canvas.rect(36, 36, LETTER[0]-72, LETTER[1]-72)
        
        # Header (Top Right)
        canvas.setFont('Helvetica-Bold', 8)
        canvas.setFillColor(colors.HexColor("#64748B"))
        header_text = f"SMALT | {content.get('student_name', 'Student')} | Assignment {content.get('assignment_number', '1')}"
        canvas.drawRightString(LETTER[0]-72, LETTER[1]-50, header_text)
        
        # Footer (Bottom Center)
        canvas.setFont('Helvetica', 8)
        canvas.drawCentredString(LETTER[0]/2.0, 50, f"Page {canvas.getPageNumber()}")
        
        # Branding (Bottom Left)
        canvas.setFont('Helvetica-Oblique', 8)
        canvas.drawString(72, 50, "AssignmentForge Elite - Research Document")
        
        canvas.restoreState()

    doc.build(elements, onFirstPage=add_page_elements, onLaterPages=add_page_elements)
    return output_path

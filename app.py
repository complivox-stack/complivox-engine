import io
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import parse_xml, OxmlElement
from docx.oxml.ns import nsdecls, qn

def set_cell_background(cell, fill_hex):
    """Table cell ko solid background color deta hai"""
    tcPr = cell._tc.get_or_add_tcPr()
    shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{fill_hex}"/>')
    tcPr.append(shd)

def set_cell_margins(cell, top=100, bottom=100, left=150, right=150):
    """Cell ke andar safe padding add karta hai"""
    tcPr = cell._tc.get_or_add_tcPr()
    tcMar = OxmlElement('w:tcMar')
    for m, val in [('top', top), ('bottom', bottom), ('left', left), ('right', right)]:
        node = OxmlElement(f'w:{m}')
        node.set(qn('w:w'), str(val))
        node.set(qn('w:type'), 'dxa')
        tcMar.append(node)
    tcPr.append(tcMar)

def prevent_table_split(table):
    """Table row ko beech mein se split hone se rokta hai"""
    for row in table.rows:
        trPr = row._tr.get_or_add_trPr()
        trPr.append(parse_xml(f'<w:cantSplit {nsdecls("w")}/>'))

def create_styled_dossier(domain, framework, findings, gaps, rtqs):
    """Executive-ready, non-splitting .DOCX dossier generate karta hai"""
    doc = Document()

    # Standard 0.75 inch clean margins
    for section in doc.sections:
        section.top_margin = Inches(0.75)
        section.bottom_margin = Inches(0.75)
        section.left_margin = Inches(0.75)
        section.right_margin = Inches(0.75)

    # Header Title
    title = doc.add_paragraph()
    title_run = title.add_run("COMPLIVOX GLOBAL")
    title_run.font.name = "Arial"
    title_run.font.size = Pt(20)
    title_run.font.bold = True
    title_run.font.color.rgb = RGBColor(14, 116, 144) # Deep Cyan/Slate
    title.paragraph_format.space_after = Pt(2)

    subtitle = doc.add_paragraph()
    sub_run = subtitle.add_run(f"Statutory Pre-Submission Defense Dossier | Framework: {framework} ({domain})")
    sub_run.font.name = "Arial"
    sub_run.font.size = Pt(10)
    sub_run.font.italic = True
    sub_run.font.color.rgb = RGBColor(100, 116, 139)
    subtitle.paragraph_format.space_after = Pt(14)

    # 1. Section: Technical Findings
    h1 = doc.add_paragraph()
    h1_run = h1.add_run("1. Technical Extraction & Compliance Status")
    h1_run.font.bold = True
    h1_run.font.size = Pt(12)
    h1.paragraph_format.keep_with_next = True # Agle content ke sath connect rakhega
    h1.paragraph_format.space_after = Pt(4)

    for item in findings:
        p = doc.add_paragraph(style='List Bullet')
        p_run = p.add_run(item)
        p_run.font.size = Pt(10)
        p.paragraph_format.space_after = Pt(2)

    doc.add_paragraph().paragraph_format.space_after = Pt(8)

    # 2. Section: Statutory Gap Matrix
    h2 = doc.add_paragraph()
    h2_run = h2.add_run("2. Statutory Gap & Deficiency Matrix")
    h2_run.font.bold = True
    h2_run.font.size = Pt(12)
    h2.paragraph_format.keep_with_next = True
    h2.paragraph_format.space_after = Pt(6)

    # Gap Matrix Table
    table = doc.add_table(rows=1, cols=3)
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.autofit = False

    headers = ["Regulatory Requirement", "Status / Deficit", "Risk Level"]
    hdr_cells = table.rows[0].cells
    for i, text in enumerate(headers):
        hdr_cells[i].text = text
        set_cell_background(hdr_cells[i], "1E293B") # Dark Slate Header
        set_cell_margins(hdr_cells[i], top=120, bottom=120, left=150, right=150)
        p = hdr_cells[i].paragraphs[0]
        for run in p.runs:
            run.font.bold = True
            run.font.size = Pt(9.5)
            run.font.color.rgb = RGBColor(255, 255, 255)

    for gap in gaps:
        row_cells = table.add_row().cells
        row_cells[0].text = gap.get("rule", "Statutory Clause")
        row_cells[1].text = gap.get("detail", "Pending technical validation")
        row_cells[2].text = gap.get("risk", "Medium")

        for i, cell in enumerate(row_cells):
            set_cell_background(cell, "F8FAFC")
            set_cell_margins(cell, top=100, bottom=100, left=150, right=150)
            p = cell.paragraphs[0]
            for run in p.runs:
                run.font.size = Pt(9)
                if i == 2:
                    run.font.bold = True
                    if gap.get("risk") == "High":
                        run.font.color.rgb = RGBColor(185, 28, 28)
                    else:
                        run.font.color.rgb = RGBColor(217, 119, 6)

    prevent_table_split(table)
    doc.add_paragraph().paragraph_format.space_after = Pt(12)

    # 3. Section: Pre-Drafted SEC Defense (RTQ Cards)
    h3 = doc.add_paragraph()
    h3_run = h3.add_run("3. Pre-Emptive SEC Objections & Defense Strategy (RTQ)")
    h3_run.font.bold = True
    h3_run.font.size = Pt(12)
    h3.paragraph_format.keep_with_next = True
    h3.paragraph_format.space_after = Pt(6)

    for idx, rtq in enumerate(rtqs, 1):
        card = doc.add_table(rows=1, cols=1)
        card.alignment = WD_TABLE_ALIGNMENT.CENTER
        cell = card.rows[0].cells[0]
        set_cell_background(cell, "F1F5F9") # Soft neutral background
        set_cell_margins(cell, top=140, bottom=140, left=180, right=180)

        cp = cell.paragraphs[0]
        cp.paragraph_format.space_after = Pt(4)
        c_title = cp.add_run(f"Objection #{idx}: {rtq.get('query', '')} [{rtq.get('risk', 'High')}]\n")
        c_title.font.bold = True
        c_title.font.size = Pt(10)
        c_title.font.color.rgb = RGBColor(15, 23, 42)

        c_std = cp.add_run(f"Statutory Standard: {rtq.get('standard', 'Statutory Guidelines')}\n")
        c_std.font.italic = True
        c_std.font.size = Pt(9)
        c_std.font.color.rgb = RGBColor(71, 85, 105)

        c_def = cp.add_run(f"Recommended Defense (RTQ): {rtq.get('defense', '')}")
        c_def.font.size = Pt(9.5)
        c_def.font.bold = True
        c_def.font.color.rgb = RGBColor(30, 41, 59)

        # Card ko toote bina ek saath rakhne ke rules
        prevent_table_split(card)
        
        # Spacer between cards
        sp = doc.add_paragraph()
        sp.paragraph_format.space_after = Pt(6)

    # Save to BytesIO Stream
    target_stream = io.BytesIO()
    doc.save(target_stream)
    target_stream.seek(0)
    return target_stream

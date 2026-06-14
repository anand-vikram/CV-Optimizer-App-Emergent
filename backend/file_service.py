"""CV parsing (PDF/DOCX/TXT) and document generation (PDF/DOCX)."""
import io
from typing import Optional
from pypdf import PdfReader
from docx import Document
from docx.shared import Pt, Inches, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from reportlab.lib.pagesizes import LETTER
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.colors import HexColor, black
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, HRFlowable
from reportlab.lib.enums import TA_LEFT


# --- Parsing ---

def parse_cv_bytes(file_bytes: bytes, filename: str) -> str:
    name = filename.lower()
    if name.endswith(".pdf"):
        return _parse_pdf(file_bytes)
    if name.endswith(".docx"):
        return _parse_docx(file_bytes)
    if name.endswith(".txt"):
        return file_bytes.decode("utf-8", errors="ignore")
    raise ValueError(f"Unsupported file type: {filename}. Use PDF, DOCX, or TXT.")


def _parse_pdf(b: bytes) -> str:
    reader = PdfReader(io.BytesIO(b))
    parts = []
    for page in reader.pages:
        text = page.extract_text() or ""
        parts.append(text)
    return "\n".join(parts).strip()


def _parse_docx(b: bytes) -> str:
    doc = Document(io.BytesIO(b))
    parts = [p.text for p in doc.paragraphs if p.text.strip()]
    for table in doc.tables:
        for row in table.rows:
            for cell in row.cells:
                if cell.text.strip():
                    parts.append(cell.text)
    return "\n".join(parts).strip()


# --- DOCX generation ---

def _add_heading(doc: Document, text: str):
    p = doc.add_paragraph()
    run = p.add_run(text.upper())
    run.bold = True
    run.font.size = Pt(11)
    run.font.color.rgb = RGBColor(0x00, 0x2F, 0xA7)
    p.paragraph_format.space_before = Pt(10)
    p.paragraph_format.space_after = Pt(2)
    # underline rule
    rule = doc.add_paragraph()
    rule_run = rule.add_run("_" * 90)
    rule_run.font.size = Pt(6)
    rule_run.font.color.rgb = RGBColor(0xCC, 0xCC, 0xCC)
    rule.paragraph_format.space_after = Pt(4)


def generate_cv_docx(cv: dict) -> bytes:
    doc = Document()
    for section in doc.sections:
        section.top_margin = Inches(0.6)
        section.bottom_margin = Inches(0.6)
        section.left_margin = Inches(0.7)
        section.right_margin = Inches(0.7)

    # Name
    name_p = doc.add_paragraph()
    name_run = name_p.add_run(cv.get("full_name", "").upper())
    name_run.bold = True
    name_run.font.size = Pt(22)
    name_run.font.color.rgb = RGBColor(0x0A, 0x0A, 0x0A)
    name_p.paragraph_format.space_after = Pt(2)

    if cv.get("headline"):
        h_p = doc.add_paragraph()
        h_run = h_p.add_run(cv["headline"])
        h_run.font.size = Pt(11)
        h_run.font.color.rgb = RGBColor(0x52, 0x52, 0x5B)
        h_p.paragraph_format.space_after = Pt(4)

    # Contact line
    contact = cv.get("contact", {}) or {}
    parts = [contact.get(k, "") for k in ("email", "phone", "location", "linkedin", "website")]
    parts = [p for p in parts if p]
    if parts:
        c_p = doc.add_paragraph()
        c_run = c_p.add_run("  |  ".join(parts))
        c_run.font.size = Pt(9)
        c_run.font.color.rgb = RGBColor(0x52, 0x52, 0x5B)

    # Summary
    if cv.get("professional_summary"):
        _add_heading(doc, "Professional Summary")
        s = doc.add_paragraph(cv["professional_summary"])
        for r in s.runs:
            r.font.size = Pt(10)

    # Skills
    skills = cv.get("core_skills") or []
    if skills:
        _add_heading(doc, "Core Skills")
        s = doc.add_paragraph(" • ".join(skills))
        for r in s.runs:
            r.font.size = Pt(10)

    # Experience
    exp = cv.get("experience") or []
    if exp:
        _add_heading(doc, "Professional Experience")
        for job in exp:
            p = doc.add_paragraph()
            t = p.add_run(f"{job.get('title','')} — {job.get('company','')}")
            t.bold = True
            t.font.size = Pt(11)
            dates = f"{job.get('start_date','')} – {job.get('end_date','')}"
            loc = job.get("location", "")
            sub = doc.add_paragraph()
            sub_run = sub.add_run(f"{loc}  |  {dates}" if loc else dates)
            sub_run.italic = True
            sub_run.font.size = Pt(9)
            sub_run.font.color.rgb = RGBColor(0x52, 0x52, 0x5B)
            for b in job.get("bullets", []):
                bp = doc.add_paragraph(b, style="List Bullet")
                for r in bp.runs:
                    r.font.size = Pt(10)

    # Education
    edu = cv.get("education") or []
    if edu:
        _add_heading(doc, "Education")
        for e in edu:
            p = doc.add_paragraph()
            t = p.add_run(f"{e.get('degree','')} — {e.get('institution','')}")
            t.bold = True
            t.font.size = Pt(11)
            dates = e.get("end_date", "") or ""
            details = e.get("details", "") or ""
            sub_text = "  |  ".join([x for x in [e.get("location", ""), dates, details] if x])
            if sub_text:
                sub = doc.add_paragraph()
                sub_run = sub.add_run(sub_text)
                sub_run.italic = True
                sub_run.font.size = Pt(9)
                sub_run.font.color.rgb = RGBColor(0x52, 0x52, 0x5B)

    # Certifications
    certs = cv.get("certifications") or []
    if certs:
        _add_heading(doc, "Certifications")
        s = doc.add_paragraph(" • ".join(certs))
        for r in s.runs:
            r.font.size = Pt(10)

    # Projects
    projects = cv.get("projects") or []
    if projects:
        _add_heading(doc, "Projects")
        for proj in projects:
            p = doc.add_paragraph()
            t = p.add_run(proj.get("name", ""))
            t.bold = True
            t.font.size = Pt(10)
            desc = doc.add_paragraph(proj.get("description", ""))
            for r in desc.runs:
                r.font.size = Pt(10)

    buf = io.BytesIO()
    doc.save(buf)
    return buf.getvalue()


def generate_cover_letter_docx(text: str, candidate_name: str) -> bytes:
    doc = Document()
    for section in doc.sections:
        section.top_margin = Inches(1.0)
        section.bottom_margin = Inches(1.0)
        section.left_margin = Inches(1.0)
        section.right_margin = Inches(1.0)

    if candidate_name:
        head = doc.add_paragraph()
        run = head.add_run(candidate_name.upper())
        run.bold = True
        run.font.size = Pt(16)
        head.paragraph_format.space_after = Pt(12)

    for para in text.split("\n\n"):
        para = para.strip()
        if not para:
            continue
        p = doc.add_paragraph(para)
        for r in p.runs:
            r.font.size = Pt(11)
        p.paragraph_format.space_after = Pt(10)

    buf = io.BytesIO()
    doc.save(buf)
    return buf.getvalue()


# --- PDF generation ---

def _pdf_styles():
    styles = getSampleStyleSheet()
    blue = HexColor("#002FA7")
    grey = HexColor("#52525B")
    custom = {
        "name": ParagraphStyle("Name", parent=styles["Title"], fontName="Helvetica-Bold",
                                fontSize=22, leading=24, textColor=black, alignment=TA_LEFT, spaceAfter=2),
        "headline": ParagraphStyle("Headline", parent=styles["Normal"], fontName="Helvetica",
                                    fontSize=11, leading=14, textColor=grey, spaceAfter=4),
        "contact": ParagraphStyle("Contact", parent=styles["Normal"], fontName="Helvetica",
                                   fontSize=9, leading=12, textColor=grey, spaceAfter=8),
        "section": ParagraphStyle("Section", parent=styles["Heading2"], fontName="Helvetica-Bold",
                                   fontSize=11, leading=14, textColor=blue, spaceBefore=10,
                                   spaceAfter=4, alignment=TA_LEFT),
        "jobtitle": ParagraphStyle("JobTitle", parent=styles["Normal"], fontName="Helvetica-Bold",
                                    fontSize=11, leading=14, textColor=black, spaceAfter=1),
        "jobsub": ParagraphStyle("JobSub", parent=styles["Normal"], fontName="Helvetica-Oblique",
                                  fontSize=9, leading=12, textColor=grey, spaceAfter=4),
        "body": ParagraphStyle("Body", parent=styles["Normal"], fontName="Helvetica",
                                fontSize=10, leading=13, textColor=black, spaceAfter=3, alignment=TA_LEFT),
        "bullet": ParagraphStyle("Bullet", parent=styles["Normal"], fontName="Helvetica",
                                  fontSize=10, leading=13, textColor=black, leftIndent=14,
                                  bulletIndent=2, spaceAfter=2, alignment=TA_LEFT),
    }
    return custom


def generate_cv_pdf(cv: dict) -> bytes:
    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=LETTER,
                            leftMargin=0.6 * inch, rightMargin=0.6 * inch,
                            topMargin=0.5 * inch, bottomMargin=0.5 * inch)
    s = _pdf_styles()
    story = []

    story.append(Paragraph(cv.get("full_name", "").upper(), s["name"]))
    if cv.get("headline"):
        story.append(Paragraph(cv["headline"], s["headline"]))

    contact = cv.get("contact", {}) or {}
    parts = [contact.get(k, "") for k in ("email", "phone", "location", "linkedin", "website")]
    parts = [p for p in parts if p]
    if parts:
        story.append(Paragraph("  |  ".join(parts), s["contact"]))

    story.append(HRFlowable(width="100%", thickness=0.5, color=HexColor("#E4E4E7"), spaceAfter=4))

    if cv.get("professional_summary"):
        story.append(Paragraph("PROFESSIONAL SUMMARY", s["section"]))
        story.append(Paragraph(cv["professional_summary"], s["body"]))

    skills = cv.get("core_skills") or []
    if skills:
        story.append(Paragraph("CORE SKILLS", s["section"]))
        story.append(Paragraph(" &nbsp;•&nbsp; ".join(skills), s["body"]))

    exp = cv.get("experience") or []
    if exp:
        story.append(Paragraph("PROFESSIONAL EXPERIENCE", s["section"]))
        for job in exp:
            story.append(Paragraph(f"{job.get('title','')} &mdash; {job.get('company','')}", s["jobtitle"]))
            dates = f"{job.get('start_date','')} &ndash; {job.get('end_date','')}"
            loc = job.get("location", "")
            sub = f"{loc} &nbsp;|&nbsp; {dates}" if loc else dates
            story.append(Paragraph(sub, s["jobsub"]))
            for b in job.get("bullets", []):
                story.append(Paragraph(b, s["bullet"], bulletText="•"))
            story.append(Spacer(1, 4))

    edu = cv.get("education") or []
    if edu:
        story.append(Paragraph("EDUCATION", s["section"]))
        for e in edu:
            story.append(Paragraph(f"{e.get('degree','')} &mdash; {e.get('institution','')}", s["jobtitle"]))
            sub_parts = [x for x in [e.get("location", ""), e.get("end_date", ""), e.get("details", "")] if x]
            if sub_parts:
                story.append(Paragraph(" &nbsp;|&nbsp; ".join(sub_parts), s["jobsub"]))

    certs = cv.get("certifications") or []
    if certs:
        story.append(Paragraph("CERTIFICATIONS", s["section"]))
        story.append(Paragraph(" &nbsp;•&nbsp; ".join(certs), s["body"]))

    projects = cv.get("projects") or []
    if projects:
        story.append(Paragraph("PROJECTS", s["section"]))
        for proj in projects:
            story.append(Paragraph(proj.get("name", ""), s["jobtitle"]))
            story.append(Paragraph(proj.get("description", ""), s["body"]))

    doc.build(story)
    return buf.getvalue()


def generate_cover_letter_pdf(text: str, candidate_name: str) -> bytes:
    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=LETTER,
                            leftMargin=1.0 * inch, rightMargin=1.0 * inch,
                            topMargin=1.0 * inch, bottomMargin=1.0 * inch)
    s = _pdf_styles()
    story = []
    if candidate_name:
        story.append(Paragraph(candidate_name.upper(), s["name"]))
        story.append(Spacer(1, 10))
    for para in text.split("\n\n"):
        para = para.strip()
        if not para:
            continue
        para_html = para.replace("\n", "<br/>")
        story.append(Paragraph(para_html, s["body"]))
        story.append(Spacer(1, 8))
    doc.build(story)
    return buf.getvalue()

"""CV parsing (PDF/DOCX/TXT) and document generation (PDF/DOCX) — refined v2."""
import io
from typing import Any
from pypdf import PdfReader
from docx import Document
from docx.shared import Pt, Inches, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from reportlab.lib.pagesizes import LETTER
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.colors import HexColor, black
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, HRFlowable
from reportlab.lib.enums import TA_LEFT, TA_CENTER


# ===================== Parsing =====================

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


# ===================== Normalizers =====================

def _norm_cert(c: Any) -> dict:
    if isinstance(c, dict):
        return {
            "name": (c.get("name") or "").strip(),
            "institute": (c.get("institute") or c.get("issuer") or "").strip(),
            "year": (c.get("year") or c.get("date") or "").strip(),
        }
    return {"name": str(c).strip(), "institute": "", "year": ""}


def _norm_pub(p: Any) -> dict:
    if isinstance(p, dict):
        return {
            "title": (p.get("title") or p.get("name") or "").strip(),
            "publisher": (p.get("publisher") or p.get("journal") or "").strip(),
            "year": (p.get("year") or "").strip(),
            "description": (p.get("description") or "").strip(),
        }
    return {"title": str(p).strip(), "publisher": "", "year": "", "description": ""}


# ===================== DOCX generation =====================

def _add_section_heading(doc: Document, text: str):
    p = doc.add_paragraph()
    run = p.add_run(text.upper())
    run.bold = True
    run.font.size = Pt(11)
    run.font.color.rgb = RGBColor(0x00, 0x2F, 0xA7)
    p.paragraph_format.space_before = Pt(10)
    p.paragraph_format.space_after = Pt(2)
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

    # --- Centered Header ---
    name_p = doc.add_paragraph()
    name_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    name_run = name_p.add_run(cv.get("full_name", "").upper())
    name_run.bold = True
    name_run.font.size = Pt(22)
    name_run.font.color.rgb = RGBColor(0x0A, 0x0A, 0x0A)
    name_p.paragraph_format.space_after = Pt(2)

    if cv.get("headline"):
        h_p = doc.add_paragraph()
        h_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        h_run = h_p.add_run(cv["headline"])
        h_run.font.size = Pt(11)
        h_run.font.color.rgb = RGBColor(0x52, 0x52, 0x5B)
        h_p.paragraph_format.space_after = Pt(4)

    contact = cv.get("contact", {}) or {}
    contact_parts = [contact.get(k, "") for k in ("email", "phone", "location", "linkedin", "website")]
    contact_parts = [p for p in contact_parts if p]
    if contact_parts:
        c_p = doc.add_paragraph()
        c_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        c_run = c_p.add_run("  |  ".join(contact_parts))
        c_run.font.size = Pt(9)
        c_run.font.color.rgb = RGBColor(0x52, 0x52, 0x5B)
        c_p.paragraph_format.space_after = Pt(2)

    # --- Summary ---
    if cv.get("professional_summary"):
        _add_section_heading(doc, "Professional Summary")
        s = doc.add_paragraph(cv["professional_summary"])
        for r in s.runs:
            r.font.size = Pt(10)

    # --- Skills (clean wrapping comma-separated) ---
    skills = cv.get("core_skills") or []
    if skills:
        _add_section_heading(doc, "Core Skills")
        # Use comma separators for cleaner wrap (avoids bullet cramming)
        s = doc.add_paragraph(", ".join(skills))
        s.paragraph_format.line_spacing = 1.25
        for r in s.runs:
            r.font.size = Pt(10)

    # --- Experience ---
    exp = cv.get("experience") or []
    if exp:
        _add_section_heading(doc, "Professional Experience")
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

    # --- Education ---
    edu = cv.get("education") or []
    if edu:
        _add_section_heading(doc, "Education")
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

    # --- Certifications (ONE per line, name — institute, year) ---
    certs = [_norm_cert(c) for c in (cv.get("certifications") or [])]
    certs = [c for c in certs if c["name"]]
    if certs:
        _add_section_heading(doc, "Certifications")
        for c in certs:
            p = doc.add_paragraph()
            p.paragraph_format.space_after = Pt(2)
            name_run = p.add_run(c["name"])
            name_run.bold = True
            name_run.font.size = Pt(10)
            if c["institute"]:
                inst = p.add_run(f"  —  {c['institute']}")
                inst.font.size = Pt(10)
                inst.font.color.rgb = RGBColor(0x52, 0x52, 0x5B)
            if c["year"]:
                yr = p.add_run(f"  ({c['year']})")
                yr.font.size = Pt(9)
                yr.italic = True
                yr.font.color.rgb = RGBColor(0x52, 0x52, 0x5B)

    # --- Projects (hands-on work only) ---
    projects = cv.get("projects") or []
    if projects:
        _add_section_heading(doc, "Projects")
        for proj in projects:
            p = doc.add_paragraph()
            t = p.add_run(proj.get("name", ""))
            t.bold = True
            t.font.size = Pt(10)
            desc = doc.add_paragraph(proj.get("description", ""))
            for r in desc.runs:
                r.font.size = Pt(10)

    # --- Publications (books, papers, articles) ---
    pubs = [_norm_pub(p) for p in (cv.get("publications") or [])]
    pubs = [p for p in pubs if p["title"]]
    if pubs:
        _add_section_heading(doc, "Publications")
        for pub in pubs:
            p = doc.add_paragraph()
            p.paragraph_format.space_after = Pt(2)
            t = p.add_run(pub["title"])
            t.bold = True
            t.font.size = Pt(10)
            meta_bits = [x for x in [pub["publisher"], pub["year"]] if x]
            if meta_bits:
                meta = p.add_run(f"  —  {', '.join(meta_bits)}")
                meta.font.size = Pt(9)
                meta.italic = True
                meta.font.color.rgb = RGBColor(0x52, 0x52, 0x5B)
            if pub["description"]:
                d = doc.add_paragraph(pub["description"])
                d.paragraph_format.space_after = Pt(4)
                for r in d.runs:
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


# ===================== PDF generation =====================

def _pdf_styles():
    styles = getSampleStyleSheet()
    blue = HexColor("#002FA7")
    grey = HexColor("#52525B")
    return {
        "name_center": ParagraphStyle("NameC", parent=styles["Title"], fontName="Helvetica-Bold",
                                       fontSize=22, leading=26, textColor=black, alignment=TA_CENTER, spaceAfter=2),
        "headline_center": ParagraphStyle("HeadC", parent=styles["Normal"], fontName="Helvetica",
                                           fontSize=11, leading=14, textColor=grey, alignment=TA_CENTER, spaceAfter=4),
        "contact_center": ParagraphStyle("ContactC", parent=styles["Normal"], fontName="Helvetica",
                                          fontSize=9, leading=12, textColor=grey, alignment=TA_CENTER, spaceAfter=8),
        "section": ParagraphStyle("Section", parent=styles["Heading2"], fontName="Helvetica-Bold",
                                   fontSize=11, leading=14, textColor=blue, spaceBefore=10,
                                   spaceAfter=4, alignment=TA_LEFT),
        "jobtitle": ParagraphStyle("JobTitle", parent=styles["Normal"], fontName="Helvetica-Bold",
                                    fontSize=11, leading=14, textColor=black, spaceAfter=1),
        "jobsub": ParagraphStyle("JobSub", parent=styles["Normal"], fontName="Helvetica-Oblique",
                                  fontSize=9, leading=12, textColor=grey, spaceAfter=4),
        "body": ParagraphStyle("Body", parent=styles["Normal"], fontName="Helvetica",
                                fontSize=10, leading=14, textColor=black, spaceAfter=3, alignment=TA_LEFT),
        "skills": ParagraphStyle("Skills", parent=styles["Normal"], fontName="Helvetica",
                                  fontSize=10, leading=16, textColor=black, spaceAfter=3, alignment=TA_LEFT),
        "bullet": ParagraphStyle("Bullet", parent=styles["Normal"], fontName="Helvetica",
                                  fontSize=10, leading=13, textColor=black, leftIndent=14,
                                  bulletIndent=2, spaceAfter=2, alignment=TA_LEFT),
        "cert_line": ParagraphStyle("CertLine", parent=styles["Normal"], fontName="Helvetica",
                                     fontSize=10, leading=14, textColor=black, spaceAfter=3, alignment=TA_LEFT),
    }


def generate_cv_pdf(cv: dict) -> bytes:
    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=LETTER,
                            leftMargin=0.6 * inch, rightMargin=0.6 * inch,
                            topMargin=0.5 * inch, bottomMargin=0.5 * inch)
    s = _pdf_styles()
    story = []

    # Centered header (name + headline + contact)
    story.append(Paragraph(cv.get("full_name", "").upper(), s["name_center"]))
    if cv.get("headline"):
        story.append(Paragraph(cv["headline"], s["headline_center"]))

    contact = cv.get("contact", {}) or {}
    contact_parts = [contact.get(k, "") for k in ("email", "phone", "location", "linkedin", "website")]
    contact_parts = [p for p in contact_parts if p]
    if contact_parts:
        story.append(Paragraph("  |  ".join(contact_parts), s["contact_center"]))

    story.append(HRFlowable(width="100%", thickness=0.5, color=HexColor("#E4E4E7"), spaceAfter=6))

    # Summary
    if cv.get("professional_summary"):
        story.append(Paragraph("PROFESSIONAL SUMMARY", s["section"]))
        story.append(Paragraph(cv["professional_summary"], s["body"]))

    # Skills: clean wrapping comma list (more breathing room)
    skills = cv.get("core_skills") or []
    if skills:
        story.append(Paragraph("CORE SKILLS", s["section"]))
        story.append(Paragraph(", ".join(skills), s["skills"]))

    # Experience
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

    # Education
    edu = cv.get("education") or []
    if edu:
        story.append(Paragraph("EDUCATION", s["section"]))
        for e in edu:
            story.append(Paragraph(f"{e.get('degree','')} &mdash; {e.get('institution','')}", s["jobtitle"]))
            sub_parts = [x for x in [e.get("location", ""), e.get("end_date", ""), e.get("details", "")] if x]
            if sub_parts:
                story.append(Paragraph(" &nbsp;|&nbsp; ".join(sub_parts), s["jobsub"]))

    # Certifications — one per line: bold name — institute (year)
    certs = [_norm_cert(c) for c in (cv.get("certifications") or [])]
    certs = [c for c in certs if c["name"]]
    if certs:
        story.append(Paragraph("CERTIFICATIONS", s["section"]))
        for c in certs:
            line = f"<b>{c['name']}</b>"
            if c["institute"]:
                line += f' &nbsp;&mdash;&nbsp; <font color="#52525B">{c["institute"]}</font>'
            if c["year"]:
                line += f' &nbsp;<font color="#52525B"><i>({c["year"]})</i></font>'
            story.append(Paragraph(line, s["cert_line"]))

    # Projects (technical/work projects only)
    projects = cv.get("projects") or []
    if projects:
        story.append(Paragraph("PROJECTS", s["section"]))
        for proj in projects:
            story.append(Paragraph(proj.get("name", ""), s["jobtitle"]))
            story.append(Paragraph(proj.get("description", ""), s["body"]))

    # Publications (books, papers, articles)
    pubs = [_norm_pub(p) for p in (cv.get("publications") or [])]
    pubs = [p for p in pubs if p["title"]]
    if pubs:
        story.append(Paragraph("PUBLICATIONS", s["section"]))
        for pub in pubs:
            meta_bits = [x for x in [pub["publisher"], pub["year"]] if x]
            line = f"<b>{pub['title']}</b>"
            if meta_bits:
                line += f' &nbsp;&mdash;&nbsp; <font color="#52525B"><i>{", ".join(meta_bits)}</i></font>'
            story.append(Paragraph(line, s["cert_line"]))
            if pub["description"]:
                story.append(Paragraph(pub["description"], s["body"]))

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
        story.append(Paragraph(candidate_name.upper(), s["name_center"]))
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

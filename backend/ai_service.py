"""Claude Sonnet 4.5 integration for CV analysis, optimization, and cover letter generation."""
import os
import json
import re
from pathlib import Path
from dotenv import load_dotenv
from emergentintegrations.llm.chat import LlmChat, UserMessage

load_dotenv(Path(__file__).parent / ".env")

EMERGENT_LLM_KEY = os.environ['EMERGENT_LLM_KEY']
MODEL_PROVIDER = "anthropic"
MODEL_NAME = "claude-sonnet-4-5-20250929"


def _new_chat(session_id: str, system_message: str) -> LlmChat:
    return LlmChat(
        api_key=EMERGENT_LLM_KEY,
        session_id=session_id,
        system_message=system_message,
    ).with_model(MODEL_PROVIDER, MODEL_NAME)


def _extract_json(text: str) -> dict:
    """Extract JSON object from Claude's response, even if wrapped in markdown."""
    fence = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text, re.DOTALL)
    raw = fence.group(1) if fence else text
    start = raw.find("{")
    end = raw.rfind("}")
    if start != -1 and end != -1:
        raw = raw[start:end + 1]
    return json.loads(raw)


async def analyze_cv(cv_text: str, job_title: str, company: str, job_description: str, session_id: str) -> dict:
    """Returns: ats_score, matched_keywords, missing_keywords, gaps[], strengths[], section_suggestions{}."""
    system = (
        "You are an elite ATS (Applicant Tracking System) consultant and senior technical recruiter "
        "with 15+ years of experience. You evaluate CVs against job descriptions with surgical precision. "
        "Always respond with strict, valid JSON only — no prose, no markdown fences."
    )
    prompt = f"""Analyze the following CV against the target job and return a JSON object with this exact schema:

{{
  "ats_score": <integer 0-100>,
  "score_breakdown": {{
    "keyword_match": <integer 0-100>,
    "skills_alignment": <integer 0-100>,
    "experience_relevance": <integer 0-100>,
    "formatting_ats_safety": <integer 0-100>
  }},
  "matched_keywords": [<top 15 keywords/skills from JD present in CV>],
  "missing_keywords": [<top 15 critical keywords/skills from JD missing from CV>],
  "gaps": [<5-8 short strings: skill/experience gaps to address>],
  "strengths": [<4-6 short strings: CV strengths for this role>],
  "section_suggestions": {{
    "summary": "<1-2 sentence rewrite suggestion>",
    "experience": "<concrete suggestion for experience section>",
    "skills": "<concrete suggestion for skills section>",
    "education": "<concrete suggestion or 'No changes needed'>"
  }},
  "overall_recommendation": "<2-3 sentence verdict>"
}}

=== TARGET JOB ===
Title: {job_title}
Company: {company}
Description:
{job_description}

=== CANDIDATE CV ===
{cv_text}

Return JSON only."""
    chat = _new_chat(session_id, system)
    response = await chat.send_message(UserMessage(text=prompt))
    return _extract_json(response)


async def optimize_cv(cv_text: str, job_title: str, company: str, job_description: str,
                      missing_keywords: list, session_id: str) -> dict:
    """Returns structured optimized CV: name, contact, summary, skills[], experience[{title, company, dates, bullets[]}], education[], certifications[]."""
    system = (
        "You are an expert CV writer specializing in ATS-optimized resumes. "
        "You rewrite CVs to naturally weave in target keywords WITHOUT fabricating experience. "
        "Output strict JSON only."
    )
    prompt = f"""Rewrite and optimize the following CV for the target job. Rules:
1. Naturally incorporate missing keywords ONLY where truthful (e.g., reframe existing experience using JD terminology).
2. Use strong action verbs and quantified achievements.
3. Keep all dates, companies, and education factual — never invent.
4. Make every bullet ATS-friendly: keyword-rich, concise, measurable.
5. Tailor the professional summary to the target role.

Return JSON with this exact schema:
{{
  "full_name": "<candidate name from CV>",
  "headline": "<short 1-line target role title, e.g. 'Associate Director, Sales & Business Development'>",
  "contact": {{
    "email": "<email or empty>",
    "phone": "<phone or empty>",
    "location": "<location or empty>",
    "linkedin": "<linkedin url or empty>",
    "website": "<website url or empty>"
  }},
  "objective": "<1-2 sentence career objective statement specific to the target role and company industry. Format: 'To <action verb> <impact> as <target role>...'>",
  "professional_summary": "<3-4 sentence summary tailored to target job, naturally using key JD terms>",
  "skill_groups": [
    {{
      "category": "<group name in Title Case, e.g. 'Sales & Strategy', 'Account Management', 'Industry Expertise', 'Business Development'>",
      "items": [<3-6 skill phrases relevant to this category>]
    }}
  ],
  "experience": [
    {{
      "title": "<job title>",
      "company": "<company>",
      "location": "<city, country or empty>",
      "start_date": "<MMM YYYY>",
      "end_date": "<MMM YYYY or 'Present'>",
      "bullets": [<4-6 ATS-optimized achievement bullets>]
    }}
  ],
  "education": [
    {{
      "degree": "<degree>",
      "institution": "<school>",
      "location": "<city, country or empty>",
      "start_date": "<YYYY or empty>",
      "end_date": "<YYYY>",
      "details": "<optional: GPA, honors, or empty>"
    }}
  ],
  "certifications": [
    {{"name": "<certification name>", "institute": "<issuing body or empty>", "year": "<YYYY or empty>"}}
  ],
  "projects": [
    {{"name": "<project name>", "description": "<1-2 sentence keyword-rich description of a hands-on technical/work project>"}}
  ],
  "publications": [
    {{"title": "<publication title>", "publisher": "<publisher, journal, or empty>", "year": "<YYYY or empty>", "description": "<optional 1-line description>"}}
  ]
}}

IMPORTANT classification & formatting rules:
- "skill_groups": ALWAYS return exactly 3 or 4 groups (preferably 4) covering the most relevant skill categories for the target role. Each group MUST have a meaningful "category" name (Title Case) and 3-6 short skill items.
- "projects" = hands-on technical/work projects the candidate built or led (e.g., software systems, deployments, case studies).
- "publications" = books, journal/conference papers, articles, whitepapers AUTHORED by the candidate. NEVER put books or papers in "projects".
- If the source CV has no projects, return projects: [].
- If the source CV has no publications, return publications: [].
- If certifications appear without an institute, leave institute as "".

=== TARGET JOB ===
Title: {job_title}
Company: {company}
Description:
{job_description}

=== KEYWORDS TO INCORPORATE WHERE TRUTHFUL ===
{', '.join(missing_keywords) if missing_keywords else 'None specified'}

=== ORIGINAL CV ===
{cv_text}

Return JSON only."""
    chat = _new_chat(session_id, system)
    response = await chat.send_message(UserMessage(text=prompt))
    return _extract_json(response)


async def generate_cover_letter(cv_text: str, job_title: str, company: str,
                                 job_description: str, candidate_name: str, session_id: str) -> str:
    """Returns a polished cover letter as plain text following a specific professional structure."""
    system = (
        "You are an expert career writer crafting compelling, personalized cover letters. "
        "Write in a confident, professional voice. Return plain text only — no JSON, no markdown, no code fences. "
        "Follow the EXACT block structure specified by the user. Separate every block with a single blank line."
    )
    prompt = f"""Write a professional cover letter following this EXACT structure. Output plain text only. Separate every block below with a single blank line (one empty line between blocks).

BLOCK 1 — Sender header (left-aligned, one item per line):
{candidate_name}
<candidate location from CV, e.g. "Mumbai, India">
<candidate email from CV>

BLOCK 2 — Date (left-aligned, format with ordinal suffix, e.g. "15th June 2026"). Use today's date.

BLOCK 3 — Recipient block (left-aligned, one item per line):
To,
The Hiring Manager
{company}
<company location if mentioned in JD, else leave that line out>

BLOCK 4 — Subject line (left-aligned, single line):
Subject: Application for the position of {job_title}

BLOCK 5 — Salutation:
Dear Hiring Manager,

BLOCK 6 — Opening paragraph (2-3 sentences): State the position being applied for, where it was seen, and a confident one-line hook about why the candidate is a strong fit.

BLOCK 7 — Body paragraph 1 (3-5 sentences): Specific achievements from the CV that map to the JD's most important requirements. Use numbers and impact. Reference the company by name where natural.

BLOCK 8 — Body paragraph 2 with a bulleted list of 3-4 standout achievements. Begin with one introductory sentence like "Some highlights from my career include:" then 3-4 bullets each starting with "• " (bullet character + space). Each bullet should be a concrete, quantified achievement.

BLOCK 9 — Body paragraph 3 (2-3 sentences): Connect candidate's domain expertise / motivation to the company's mission or stated needs. Show research about the company.

BLOCK 10 — Closing paragraph (2 sentences): Express enthusiasm for an interview and gratitude.

BLOCK 11 — Closing phrase:
Yours Sincerely,

BLOCK 12 — Candidate name:
{candidate_name}

Rules:
- Do NOT include any block labels (no "BLOCK 1", "BLOCK 2", etc.) in the output — just the content.
- Do NOT fabricate experience or numbers. Use only what's in the CV.
- Avoid generic clichés like "I am writing to apply for the position of...".
- Left-align everything. No markdown. No JSON.

=== TARGET ROLE ===
Title: {job_title}
Company: {company}
Description:
{job_description}

=== CANDIDATE NAME ===
{candidate_name}

=== CANDIDATE CV ===
{cv_text}

Begin output directly with the candidate's name (no preamble)."""
    chat = _new_chat(session_id, system)
    response = await chat.send_message(UserMessage(text=prompt))
    return response.strip()

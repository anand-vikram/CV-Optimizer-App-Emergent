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
  "headline": "<short 1-line title aligned to target role, e.g. 'Senior Data Engineer'>",
  "contact": {{
    "email": "<email or empty>",
    "phone": "<phone or empty>",
    "location": "<location or empty>",
    "linkedin": "<linkedin url or empty>",
    "website": "<website or empty>"
  }},
  "professional_summary": "<3-4 sentence summary tailored to target job, naturally using key JD terms>",
  "core_skills": [<12-20 skill keywords, prioritizing JD-matched terms>],
  "experience": [
    {{
      "title": "<job title>",
      "company": "<company>",
      "location": "<location or empty>",
      "start_date": "<MMM YYYY>",
      "end_date": "<MMM YYYY or 'Present'>",
      "bullets": [<4-6 ATS-optimized achievement bullets>]
    }}
  ],
  "education": [
    {{
      "degree": "<degree>",
      "institution": "<school>",
      "location": "<location or empty>",
      "start_date": "<YYYY or empty>",
      "end_date": "<YYYY>",
      "details": "<optional: GPA, honors, or empty>"
    }}
  ],
  "certifications": [<list of certifications or empty array>],
  "projects": [
    {{"name": "<name>", "description": "<1-2 sentence keyword-rich description>"}}
  ]
}}

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
    """Returns a polished cover letter as plain text."""
    system = (
        "You are an expert career writer crafting compelling, personalized cover letters. "
        "Write in a confident, professional voice. Return plain text only — no JSON, no markdown."
    )
    prompt = f"""Write a professional 3-4 paragraph cover letter for the candidate.

Structure:
- Opening: hook + the specific role and company
- Middle (1-2 paragraphs): 2-3 specific achievements from CV that map directly to JD requirements (use numbers/impact)
- Closing: enthusiasm + call to action

Tone: confident, specific, not generic. Avoid clichés like "I am writing to apply".
Do NOT fabricate experience. Use today's date format: {{Month Day, Year}}.

=== TARGET ROLE ===
Title: {job_title}
Company: {company}
Description:
{job_description}

=== CANDIDATE ===
Name: {candidate_name}

=== CV ===
{cv_text}

Begin the letter directly with the date, then "Dear Hiring Manager," — no preamble."""
    chat = _new_chat(session_id, system)
    response = await chat.send_message(UserMessage(text=prompt))
    return response.strip()

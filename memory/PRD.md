# CV Optimizer / ATS Enhancer — PRD

## Original Problem Statement
Develop a CV Optimizer/Enhancer app that helps users make their CV ATS-compliant with a professional look and structure. Goal: improve interview shortlisting and hiring chances.

Required features:
1. User registration (name + email)
2. Raw CV upload
3. Target job profile, description, and company input
4. Analyze CV vs JD: identify gaps, optimize for ATS by naturally inserting keywords
5. Output optimized CV in Word + PDF
6. Generate professional cover letter
7. Professional, user-friendly UI
8. Additional quality enhancements

## Architecture
- **Frontend**: React + Tailwind + Shadcn UI (sharp/brutalist), React Router, Sonner toasts, Phosphor icons. Swiss High-Contrast design system from `/app/design_guidelines.json`.
- **Backend**: FastAPI on port 8001 (supervisor), all routes under `/api`. JWT auth (PyJWT + bcrypt). MongoDB via motor.
- **AI**: Claude Sonnet 4.5 (`claude-sonnet-4-5-20250929`) via Emergent Universal LLM Key + `emergentintegrations.llm.chat`.
- **CV parsing**: `pypdf` (PDF), `python-docx` (DOCX), text (TXT).
- **Document generation**: `reportlab` (PDF), `python-docx` (DOCX) for both optimized CV and cover letter.

## User Personas
- **Active job seekers** — want their CV to pass ATS for a specific role.
- **Career switchers** — need keyword reframing across domains.
- **Recent graduates** — need help structuring early-career CVs.

## Core Requirements (Static)
- Email/password auth (JWT, 30-day expiry).
- Upload PDF/DOCX/TXT up to ~5MB.
- Analyze with: ATS score (0-100), breakdown across 4 dimensions, matched/missing keywords, gaps, strengths, section suggestions.
- Optimize produces structured CV (summary, skills, experience bullets, education, certifications, projects) + tailored cover letter.
- Download CV + cover letter as PDF + DOCX (token via query OR header).
- Save & list past analyses per user (dashboard).

## What's Been Implemented — 2026-02 (v1.0)
- ✅ Auth: register, login, /me, JWT bearer protection, logout (frontend).
- ✅ CV upload + parsing (PDF/DOCX/TXT) at `/api/cv/upload`.
- ✅ AI analysis (`/api/analyze`) — Claude Sonnet 4.5 returns structured JSON.
- ✅ AI optimization (`/api/optimize`) — produces structured optimized CV + cover letter.
- ✅ PDF + DOCX generation for CV and cover letter at `/api/optimized/{id}/download`.
- ✅ List analyses + dashboard stats.
- ✅ Landing page (hero + features + how-it-works + CTA), Login, Register, Dashboard, OptimizeFlow (stepper), AnalysisResult (ATS score + breakdown bars + keyword chips + gaps/strengths + section suggestions), OptimizedResult (preview + 4 download buttons + CV/Cover tab).
- ✅ Swiss/brutalist design system: Cabinet Grotesk + Satoshi + IBM Plex Mono fonts, sharp edges, #002FA7 accent, brutalist shadows.
- ✅ Comprehensive `data-testid` coverage.
- ✅ Backend + frontend e2e tested — 100% pass.

## Prioritized Backlog
**P1**
- Run `optimize_cv` and `generate_cover_letter` via `asyncio.gather` to cut latency ~50%.
- Add `Content-Length` guard on `/api/cv/upload` (5MB cap) and friendly error.
- Add rate limiting on `/api/auth/*` (slowapi).

**P2**
- Multiple CV template themes (currently single "modern minimalist" style).
- Interview-prep tips panel based on JD.
- Save/manage multiple optimized versions per analysis with diff view.
- Compare two analyses side-by-side.

**P3**
- Email the optimized CV to user.
- Public sharable link to view (read-only) ATS report.
- Stripe-powered Pro tier (unlimited analyses, premium templates).

## Next Tasks (post-finish)
- User feedback gathering → prioritize P1 latency improvements first.
- Add Stripe Pro tier for monetization.

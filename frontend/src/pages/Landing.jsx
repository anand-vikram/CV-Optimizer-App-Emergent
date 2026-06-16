import React from "react";
import { Link } from "react-router-dom";
import Navbar from "../components/Navbar";
import { ArrowRight, Target, FileText, Sparkle, ChartBar, EnvelopeSimple, ShieldCheck, Timer, ChartLineUp } from "@phosphor-icons/react";
import { useAuth } from "../contexts/AuthContext";

const features = [
  { icon: Target, title: "ATS Score (0–100)", desc: "Hard, objective score plus a breakdown across keywords, skills alignment, and experience relevance." },
  { icon: ChartBar, title: "Keyword Gap Analysis", desc: "See exactly which terms the job description demands — matched, missing, and ready to insert." },
  { icon: Sparkle, title: "AI Rewrite (Claude Sonnet 4.5)", desc: "Bullets reframed with strong verbs, quantified impact, and JD-aligned terminology — no fabrication." },
  { icon: FileText, title: "PDF + DOCX Export", desc: "Recruiter-ready downloads in both Word and PDF, formatted to pass ATS parsers." },
  { icon: EnvelopeSimple, title: "Cover Letter Generator", desc: "A personalized 3-paragraph cover letter mapped to the specific role and company." },
  { icon: ShieldCheck, title: "Section-Level Suggestions", desc: "Concrete edits for Summary, Experience, Skills and Education — not vague advice." },
];

export default function Landing() {
  const { user } = useAuth();
  return (
    <div className="min-h-screen bg-white text-[#0A0A0A]">
      <Navbar />

      {/* HERO */}
      <section className="border-b border-zinc-200 relative overflow-hidden">
        <div className="grid-bg absolute inset-0 opacity-60 pointer-events-none" />
        <div className="max-w-7xl mx-auto px-6 py-20 lg:py-28 grid grid-cols-1 lg:grid-cols-12 gap-12 relative">
          <div className="lg:col-span-7 fade-up">
            <div className="inline-flex items-center gap-2 border border-zinc-300 px-3 py-1 text-xs font-mono-data mb-8" data-testid="hero-badge">
              <span className="w-1.5 h-1.5 bg-[#00C853]" /> ATS-COMPLIANT · CLAUDE SONNET 4.5
            </div>
            <h1 className="font-display font-black text-5xl sm:text-6xl lg:text-7xl tracking-tighter leading-[0.95] mb-6">
              Get past the <span className="text-[#002FA7]">robot.</span><br/>
              Get to the <span className="underline decoration-[6px] underline-offset-[6px] decoration-[#0A0A0A]">interview.</span>
            </h1>
            <p className="text-lg text-zinc-600 max-w-xl mb-10 leading-relaxed">
              Upload your CV. Paste the job description. We score it, fix it, and hand you back a recruiter-ready
              PDF, Word file, and a cover letter — in under sixty seconds.
            </p>
            <div className="flex flex-wrap items-center gap-4">
              <Link to={user ? "/optimize" : "/register"} data-testid="hero-cta-primary"
                className="bg-[#002FA7] text-white px-6 py-4 font-medium flex items-center gap-2 brutalist-shadow-hover transition-all">
                {user ? "Optimize a CV" : "Start free"} <ArrowRight size={18} weight="bold" />
              </Link>
              <Link to="/login" data-testid="hero-cta-secondary"
                className="border border-[#0A0A0A] px-6 py-4 font-medium hover:bg-[#0A0A0A] hover:text-white transition-colors">
                I have an account
              </Link>
            </div>
          </div>

          {/* Right column — Stats panel (replaces previous mini CV preview) */}
          <div className="lg:col-span-5 fade-up flex items-center">
            <div className="w-full bg-white border border-zinc-200 brutalist-shadow">
              <div className="flex items-center justify-between border-b border-zinc-200 px-5 py-3 bg-zinc-50">
                <span className="font-mono-data text-[11px] uppercase text-zinc-500 tracking-wider">// By the numbers</span>
                <span className="font-mono-data text-[11px] text-[#00C853]">● LIVE</span>
              </div>

              <div className="divide-y divide-zinc-200">
                {/* Stat 1 */}
                <div className="flex items-center justify-between px-6 py-5" data-testid="stat-ats">
                  <div className="flex items-baseline gap-3">
                    <span className="font-mono-data text-[10px] text-zinc-400">01</span>
                    <div>
                      <div className="font-mono-data text-[10px] uppercase text-zinc-500 tracking-wider mb-0.5">Avg. ATS uplift</div>
                      <div className="font-display font-black text-4xl lg:text-5xl leading-none tracking-tighter">94<span className="text-[#002FA7]">%</span></div>
                    </div>
                  </div>
                  <ChartLineUp size={24} weight="bold" className="text-zinc-300" />
                </div>

                {/* Stat 2 */}
                <div className="flex items-center justify-between px-6 py-5">
                  <div className="flex items-baseline gap-3">
                    <span className="font-mono-data text-[10px] text-zinc-400">02</span>
                    <div>
                      <div className="font-mono-data text-[10px] uppercase text-zinc-500 tracking-wider mb-0.5">Per analysis</div>
                      <div className="font-display font-black text-4xl lg:text-5xl leading-none tracking-tighter">
                        &lt;<span className="text-[#0A0A0A]">60</span><span className="text-[#52525B] text-3xl lg:text-4xl">s</span>
                      </div>
                    </div>
                  </div>
                  <Timer size={24} weight="bold" className="text-zinc-300" />
                </div>

                {/* Stat 3 */}
                <div className="flex items-center justify-between px-6 py-5">
                  <div className="flex items-baseline gap-3">
                    <span className="font-mono-data text-[10px] text-zinc-400">03</span>
                    <div>
                      <div className="font-mono-data text-[10px] uppercase text-zinc-500 tracking-wider mb-0.5">Exports</div>
                      <div className="font-display font-black text-3xl lg:text-4xl leading-none tracking-tighter">
                        PDF<span className="text-[#002FA7]">+</span>DOCX
                      </div>
                    </div>
                  </div>
                  <FileText size={24} weight="bold" className="text-zinc-300" />
                </div>
              </div>

              <div className="border-t border-zinc-200 px-5 py-3 bg-zinc-50">
                <div className="font-mono-data text-[10px] uppercase tracking-wider text-zinc-500 text-center">
                  ATS-compliant · Claude Sonnet 4.5 · Recruiter-ready output
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* FEATURES */}
      <section className="max-w-7xl mx-auto px-6 py-20 border-b border-zinc-200">
        <div className="grid lg:grid-cols-12 gap-8 mb-12">
          <div className="lg:col-span-5">
            <div className="font-mono-data text-xs uppercase text-zinc-500 mb-4">// 01 — Capabilities</div>
            <h2 className="font-display font-black text-4xl lg:text-5xl tracking-tighter leading-none">
              Built to <span className="text-[#002FA7]">beat</span><br/>
              the parser.
            </h2>
          </div>
          <div className="lg:col-span-7 flex items-end">
            <p className="text-zinc-600 max-w-lg">
              Every modern hiring pipeline runs your resume through an ATS first. We reverse-engineer what those
              systems look for — and rewrite your CV to win.
            </p>
          </div>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-0 border border-zinc-200">
          {features.map((f, i) => (
            <div key={f.title} className={`p-8 ${i % 3 !== 2 ? 'lg:border-r' : ''} ${i % 2 === 0 ? 'md:border-r lg:border-r' : ''} ${i < features.length - (features.length % 3 || 3) ? 'border-b' : ''} border-zinc-200 hover:bg-zinc-50 transition-colors`}>
              <f.icon size={28} weight="bold" className="text-[#002FA7] mb-4" />
              <h3 className="font-display font-bold text-xl mb-2 tracking-tight">{f.title}</h3>
              <p className="text-sm text-zinc-600 leading-relaxed">{f.desc}</p>
            </div>
          ))}
        </div>
      </section>

      {/* HOW IT WORKS */}
      <section className="max-w-7xl mx-auto px-6 py-20 border-b border-zinc-200">
        <div className="font-mono-data text-xs uppercase text-zinc-500 mb-4">// 02 — Process</div>
        <h2 className="font-display font-black text-4xl lg:text-5xl tracking-tighter leading-none mb-12">
          Four steps. One stronger CV.
        </h2>
        <div className="grid md:grid-cols-4 gap-0 border-t border-zinc-200">
          {[
            ["01", "Upload", "PDF, DOCX or TXT — we extract every line."],
            ["02", "Paste JD", "Drop the job title, company, and description."],
            ["03", "Analyze", "Claude scores, gaps, and keyword-maps in seconds."],
            ["04", "Download", "Optimized CV (PDF + DOCX) and a tailored cover letter."],
          ].map((s, i) => (
            <div key={s[0]} className={`p-8 ${i < 3 ? 'md:border-r' : ''} border-zinc-200`}>
              <div className="font-mono-data text-xs text-zinc-400 mb-4">{s[0]}</div>
              <div className="font-display font-black text-2xl mb-3 tracking-tight">{s[1]}</div>
              <p className="text-sm text-zinc-600 leading-relaxed">{s[2]}</p>
            </div>
          ))}
        </div>
      </section>

      {/* CTA */}
      <section className="max-w-7xl mx-auto px-6 py-20">
        <div className="bg-[#0A0A0A] text-white p-12 lg:p-16 relative overflow-hidden">
          <div className="grid-bg absolute inset-0 opacity-10" />
          <div className="relative grid lg:grid-cols-2 gap-8 items-center">
            <div>
              <h2 className="font-display font-black text-4xl lg:text-5xl tracking-tighter leading-none mb-4">
                Stop guessing.<br/><span className="text-[#00C853]">Start interviewing.</span>
              </h2>
            </div>
            <div className="flex lg:justify-end">
              <Link to={user ? "/optimize" : "/register"} data-testid="footer-cta"
                className="bg-white text-[#0A0A0A] px-8 py-5 font-display font-bold text-lg flex items-center gap-3 hover:bg-[#00C853] hover:text-[#0A0A0A] transition-colors">
                {user ? "Optimize a CV" : "Create free account"} <ArrowRight size={22} weight="bold" />
              </Link>
            </div>
          </div>
        </div>
      </section>

      <footer className="border-t border-zinc-200 py-8">
        <div className="max-w-7xl mx-auto px-6 flex flex-wrap items-center justify-between gap-4 font-mono-data text-xs text-zinc-500 uppercase">
          <span>ATS/Optimizer · v1.0</span>
          <span>Built with Claude Sonnet 4.5</span>
        </div>
      </footer>
    </div>
  );
}

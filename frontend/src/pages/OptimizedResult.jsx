import React, { useEffect, useState } from "react";
import { useParams, Link } from "react-router-dom";
import Navbar from "../components/Navbar";
import api, { API_BASE } from "../lib/api";
import { toast } from "sonner";
import { DownloadSimple, FileText, EnvelopeSimple, CheckCircle } from "@phosphor-icons/react";

export default function OptimizedResult() {
  const { id } = useParams();
  const [opt, setOpt] = useState(null);
  const [loading, setLoading] = useState(true);
  const [tab, setTab] = useState("cv");

  useEffect(() => {
    api.get(`/optimized/${id}`)
      .then((r) => setOpt(r.data))
      .catch(() => toast.error("Result not found"))
      .finally(() => setLoading(false));
  }, [id]);

  const downloadUrl = (kind, fmt) => {
    const token = localStorage.getItem("cv_token");
    return `${API_BASE}/optimized/${id}/download?kind=${kind}&fmt=${fmt}&token=${encodeURIComponent(token)}`;
  };

  if (loading) return (
    <div className="min-h-screen bg-white"><Navbar />
      <div className="max-w-7xl mx-auto px-6 py-20 font-mono-data text-sm text-zinc-500">Loading optimized CV…</div>
    </div>
  );
  if (!opt) return null;

  const cv = opt.structured_cv || {};
  const contact = cv.contact || {};
  const contactLine = [contact.email, contact.phone, contact.location, contact.linkedin, contact.website].filter(Boolean).join("  |  ");

  return (
    <div className="min-h-screen bg-white">
      <Navbar />
      <div className="max-w-7xl mx-auto px-6 py-10">
        <div className="flex items-center gap-2 mb-4" data-testid="success-banner">
          <CheckCircle size={20} weight="fill" className="text-[#00C853]" />
          <span className="font-mono-data text-xs uppercase text-[#00C853]">Optimization complete</span>
        </div>
        <h1 className="font-display font-black text-4xl lg:text-5xl tracking-tighter mb-8 leading-none">
          Recruiter-ready.
        </h1>

        {/* Download bar */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-0 border border-zinc-200 mb-8">
          <div className="p-6 border-r border-zinc-200">
            <div className="flex items-center gap-2 mb-3">
              <FileText size={18} weight="bold" />
              <span className="font-display font-bold uppercase tracking-tight text-sm">Optimized CV</span>
            </div>
            <div className="flex gap-3">
              <a href={downloadUrl("cv", "pdf")} data-testid="download-cv-pdf"
                className="flex-1 bg-[#0A0A0A] text-white px-4 py-3 font-medium flex items-center justify-center gap-2 hover:bg-[#002FA7] transition-colors">
                <DownloadSimple size={16} weight="bold" /> PDF
              </a>
              <a href={downloadUrl("cv", "docx")} data-testid="download-cv-docx"
                className="flex-1 border border-[#0A0A0A] px-4 py-3 font-medium flex items-center justify-center gap-2 hover:bg-[#0A0A0A] hover:text-white transition-colors">
                <DownloadSimple size={16} weight="bold" /> Word (DOCX)
              </a>
            </div>
          </div>
          <div className="p-6">
            <div className="flex items-center gap-2 mb-3">
              <EnvelopeSimple size={18} weight="bold" />
              <span className="font-display font-bold uppercase tracking-tight text-sm">Cover letter</span>
            </div>
            <div className="flex gap-3">
              <a href={downloadUrl("cover_letter", "pdf")} data-testid="download-cover-pdf"
                className="flex-1 bg-[#002FA7] text-white px-4 py-3 font-medium flex items-center justify-center gap-2 hover:bg-[#0A0A0A] transition-colors">
                <DownloadSimple size={16} weight="bold" /> PDF
              </a>
              <a href={downloadUrl("cover_letter", "docx")} data-testid="download-cover-docx"
                className="flex-1 border border-[#002FA7] text-[#002FA7] px-4 py-3 font-medium flex items-center justify-center gap-2 hover:bg-[#002FA7] hover:text-white transition-colors">
                <DownloadSimple size={16} weight="bold" /> Word (DOCX)
              </a>
            </div>
          </div>
        </div>

        {/* Tabs */}
        <div className="flex gap-0 border-b border-zinc-200 mb-6">
          <button onClick={()=>setTab("cv")} data-testid="tab-cv"
            className={`px-6 py-3 font-display font-bold uppercase tracking-tight text-sm border-b-2 ${tab==='cv' ? 'border-[#002FA7] text-[#0A0A0A]' : 'border-transparent text-zinc-500 hover:text-[#0A0A0A]'}`}>
            CV preview
          </button>
          <button onClick={()=>setTab("cover")} data-testid="tab-cover"
            className={`px-6 py-3 font-display font-bold uppercase tracking-tight text-sm border-b-2 ${tab==='cover' ? 'border-[#002FA7] text-[#0A0A0A]' : 'border-transparent text-zinc-500 hover:text-[#0A0A0A]'}`}>
            Cover letter
          </button>
        </div>

        {tab === "cv" ? (
          <div className="border border-zinc-200 p-10 max-w-4xl mx-auto" data-testid="cv-preview">
            <div className="font-display font-black text-4xl tracking-tight uppercase">{cv.full_name}</div>
            {cv.headline && <div className="text-zinc-600 mt-1">{cv.headline}</div>}
            {contactLine && <div className="font-mono-data text-xs text-zinc-500 mt-3">{contactLine}</div>}

            <hr className="my-6 border-zinc-200" />

            {cv.professional_summary && (
              <section className="mb-6">
                <h3 className="font-display font-bold text-sm uppercase tracking-tight text-[#002FA7] mb-2">Professional Summary</h3>
                <p className="text-sm leading-relaxed">{cv.professional_summary}</p>
              </section>
            )}

            {cv.core_skills?.length > 0 && (
              <section className="mb-6">
                <h3 className="font-display font-bold text-sm uppercase tracking-tight text-[#002FA7] mb-2">Core Skills</h3>
                <div className="flex flex-wrap gap-2">
                  {cv.core_skills.map((s,i)=>(<span key={i} className="font-mono-data text-xs bg-zinc-100 border border-zinc-200 px-2 py-1">{s}</span>))}
                </div>
              </section>
            )}

            {cv.experience?.length > 0 && (
              <section className="mb-6">
                <h3 className="font-display font-bold text-sm uppercase tracking-tight text-[#002FA7] mb-3">Professional Experience</h3>
                {cv.experience.map((j, i) => (
                  <div key={i} className="mb-5">
                    <div className="font-display font-bold text-sm">{j.title} — {j.company}</div>
                    <div className="font-mono-data text-xs text-zinc-500 italic mb-2">
                      {[j.location, `${j.start_date} – ${j.end_date}`].filter(Boolean).join("  |  ")}
                    </div>
                    <ul className="list-disc pl-5 space-y-1 text-sm">
                      {(j.bullets||[]).map((b,bi)=>(<li key={bi}>{b}</li>))}
                    </ul>
                  </div>
                ))}
              </section>
            )}

            {cv.education?.length > 0 && (
              <section className="mb-6">
                <h3 className="font-display font-bold text-sm uppercase tracking-tight text-[#002FA7] mb-3">Education</h3>
                {cv.education.map((e, i) => (
                  <div key={i} className="mb-2">
                    <div className="font-display font-bold text-sm">{e.degree} — {e.institution}</div>
                    <div className="font-mono-data text-xs text-zinc-500">
                      {[e.location, e.end_date, e.details].filter(Boolean).join("  |  ")}
                    </div>
                  </div>
                ))}
              </section>
            )}

            {cv.certifications?.length > 0 && (
              <section className="mb-6">
                <h3 className="font-display font-bold text-sm uppercase tracking-tight text-[#002FA7] mb-2">Certifications</h3>
                <div className="flex flex-wrap gap-2 text-sm">
                  {cv.certifications.map((c,i)=>(<span key={i} className="font-mono-data text-xs bg-zinc-100 border border-zinc-200 px-2 py-1">{c}</span>))}
                </div>
              </section>
            )}

            {cv.projects?.length > 0 && (
              <section>
                <h3 className="font-display font-bold text-sm uppercase tracking-tight text-[#002FA7] mb-3">Projects</h3>
                {cv.projects.map((p, i) => (
                  <div key={i} className="mb-3">
                    <div className="font-display font-bold text-sm">{p.name}</div>
                    <div className="text-sm text-zinc-700">{p.description}</div>
                  </div>
                ))}
              </section>
            )}
          </div>
        ) : (
          <div className="border border-zinc-200 p-10 max-w-3xl mx-auto whitespace-pre-wrap leading-relaxed text-sm" data-testid="cover-letter-preview">
            {opt.cover_letter}
          </div>
        )}

        <div className="flex justify-center mt-8">
          <Link to="/dashboard" data-testid="optimized-back-dashboard"
            className="border border-[#0A0A0A] px-6 py-3 font-medium hover:bg-[#0A0A0A] hover:text-white transition-colors">
            ← Back to dashboard
          </Link>
        </div>
      </div>
    </div>
  );
}

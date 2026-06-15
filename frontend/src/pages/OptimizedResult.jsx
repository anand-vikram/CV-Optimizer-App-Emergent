import React, { useEffect, useState } from "react";
import { useParams, Link, useNavigate } from "react-router-dom";
import Navbar from "../components/Navbar";
import api, { API_BASE } from "../lib/api";
import { toast } from "sonner";
import { DownloadSimple, FileText, EnvelopeSimple, CheckCircle, ArrowsClockwise } from "@phosphor-icons/react";

export default function OptimizedResult() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [opt, setOpt] = useState(null);
  const [loading, setLoading] = useState(true);
  const [tab, setTab] = useState("cv");
  const [regenerating, setRegenerating] = useState(false);

  useEffect(() => {
    setLoading(true);
    api.get(`/optimized/${id}`)
      .then((r) => setOpt(r.data))
      .catch(() => toast.error("Result not found"))
      .finally(() => setLoading(false));
  }, [id]);

  const onRegenerate = async () => {
    if (!opt?.analysis_id) return;
    setRegenerating(true);
    try {
      const { data } = await api.post("/optimize", { analysis_id: opt.analysis_id });
      toast.success("Regenerated with the latest template");
      navigate(`/optimized/${data.id}`);
    } catch (err) {
      toast.error(err?.response?.data?.detail || "Regeneration failed");
    } finally {
      setRegenerating(false);
    }
  };

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
        <div className="flex items-end justify-between flex-wrap gap-4 mb-8">
          <div>
            <div className="flex items-center gap-2 mb-4" data-testid="success-banner">
              <CheckCircle size={20} weight="fill" className="text-[#00C853]" />
              <span className="font-mono-data text-xs uppercase text-[#00C853]">Optimization complete</span>
            </div>
            <h1 className="font-display font-black text-4xl lg:text-5xl tracking-tighter leading-none">
              Recruiter-ready.
            </h1>
          </div>
          <button onClick={onRegenerate} disabled={regenerating} data-testid="regenerate-button"
            className="border border-[#0A0A0A] px-5 py-3 font-medium flex items-center gap-2 hover:bg-[#0A0A0A] hover:text-white transition-colors disabled:opacity-60">
            <ArrowsClockwise size={16} weight="bold" /> {regenerating ? "Regenerating…" : "Regenerate"}
          </button>
        </div>

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
            {/* Centered header */}
            <div className="text-center">
              <div className="font-display font-black text-5xl tracking-tight uppercase text-[#0A0A0A]">{cv.full_name}</div>
              {contactLine && <div className="text-sm text-[#0A0A0A] mt-3">{contactLine}</div>}
              {cv.contact?.website && <div className="text-sm text-[#0A0A0A] mt-1">{cv.contact.website}</div>}
            </div>

            {/* Objective */}
            {(cv.objective || cv.headline) && (
              <section className="mt-6">
                <h3 className="font-bold text-[12px] uppercase tracking-wider text-[#1F2937] pb-1 border-b border-[#9CA3AF] mb-3">Objective</h3>
                <p className="text-[15px] leading-relaxed text-[#0A0A0A]">{cv.objective || `To contribute as ${cv.headline}.`}</p>
              </section>
            )}

            {/* Summary */}
            {cv.professional_summary && (
              <section className="mt-5">
                <h3 className="font-bold text-[12px] uppercase tracking-wider text-[#1F2937] pb-1 border-b border-[#9CA3AF] mb-3">Professional Summary</h3>
                <p className="text-[15px] leading-relaxed text-[#0A0A0A] text-justify">{cv.professional_summary}</p>
              </section>
            )}

            {/* Core Skills — 4-column grid */}
            {(() => {
              const groups = (cv.skill_groups && cv.skill_groups.length > 0)
                ? cv.skill_groups
                : (cv.core_skills?.length > 0 ? [{ category: "Core Competencies", items: cv.core_skills }] : []);
              if (groups.length === 0) return null;
              const cols = Math.min(4, groups.length);
              return (
                <section className="mt-5">
                  <h3 className="font-bold text-[12px] uppercase tracking-wider text-[#1F2937] pb-1 border-b border-[#9CA3AF] mb-3">Core Skills</h3>
                  <div className={`grid gap-6`} style={{ gridTemplateColumns: `repeat(${cols}, minmax(0, 1fr))` }}>
                    {groups.slice(0, cols).map((g, gi) => (
                      <div key={gi}>
                        <div className="font-bold text-[11px] uppercase tracking-wider text-[#1F2937] mb-2">{g.category}</div>
                        <ul className="space-y-1">
                          {(g.items || []).map((it, ii) => (
                            <li key={ii} className="text-[14px] text-[#0A0A0A] leading-snug">{it}</li>
                          ))}
                        </ul>
                      </div>
                    ))}
                  </div>
                </section>
              );
            })()}

            {/* Experience */}
            {cv.experience?.length > 0 && (
              <section className="mt-5">
                <h3 className="font-bold text-[12px] uppercase tracking-wider text-[#1F2937] pb-1 border-b border-[#9CA3AF] mb-3">Professional Experience</h3>
                {cv.experience.map((j, i) => (
                  <div key={i} className="mb-5 last:mb-0">
                    <div className="flex justify-between items-baseline gap-4">
                      <div className="font-bold text-[15px] text-[#0A0A0A]">{j.title}</div>
                      <div className="text-[14px] text-[#0A0A0A] whitespace-nowrap">{[j.start_date, j.end_date].filter(Boolean).join(" – ")}</div>
                    </div>
                    {j.company && <div className="font-bold text-[14px] text-[#0A0A0A]">{j.company}</div>}
                    {j.location && <div className="text-[14px] text-[#0A0A0A] mb-2">{j.location}</div>}
                    <ul className="list-disc pl-5 space-y-1 text-[14px] text-[#0A0A0A] leading-relaxed">
                      {(j.bullets || []).map((b, bi) => <li key={bi}>{b}</li>)}
                    </ul>
                  </div>
                ))}
              </section>
            )}

            {/* Education */}
            {cv.education?.length > 0 && (
              <section className="mt-5">
                <h3 className="font-bold text-[12px] uppercase tracking-wider text-[#1F2937] pb-1 border-b border-[#9CA3AF] mb-3">Education</h3>
                {cv.education.map((e, i) => (
                  <div key={i} className="mb-3 last:mb-0">
                    <div className="flex justify-between items-baseline gap-4">
                      <div className="font-bold text-[15px] text-[#0A0A0A]">{e.degree}</div>
                      <div className="text-[14px] text-[#0A0A0A] whitespace-nowrap">{e.end_date || e.start_date}</div>
                    </div>
                    <div className="text-[14px] text-[#0A0A0A]">{[e.institution, e.location].filter(Boolean).join(" | ")}</div>
                    {e.details && <div className="text-[14px] text-[#0A0A0A]">{e.details}</div>}
                  </div>
                ))}
              </section>
            )}

            {/* Certifications */}
            {cv.certifications?.length > 0 && (
              <section className="mt-5">
                <h3 className="font-bold text-[12px] uppercase tracking-wider text-[#1F2937] pb-1 border-b border-[#9CA3AF] mb-3">Certifications</h3>
                <div className="space-y-1.5">
                  {cv.certifications.map((c, i) => {
                    const isObj = c && typeof c === "object";
                    const name = isObj ? c.name : c;
                    const institute = isObj ? c.institute : "";
                    const year = isObj ? c.year : "";
                    return (
                      <div key={i} className="flex justify-between items-baseline gap-4">
                        <div className="text-[14px] text-[#0A0A0A]">
                          <span className="font-semibold">{name}</span>
                          {institute && <span> | {institute}</span>}
                        </div>
                        {year && <div className="text-[14px] text-[#0A0A0A] whitespace-nowrap">{year}</div>}
                      </div>
                    );
                  })}
                </div>
              </section>
            )}

            {/* Projects */}
            {cv.projects?.length > 0 && (
              <section className="mt-5">
                <h3 className="font-bold text-[12px] uppercase tracking-wider text-[#1F2937] pb-1 border-b border-[#9CA3AF] mb-3">Projects</h3>
                {cv.projects.map((p, i) => (
                  <div key={i} className="mb-3 last:mb-0">
                    <div className="font-bold text-[14px] text-[#0A0A0A]">{p.name}</div>
                    {p.description && <div className="text-[14px] text-[#0A0A0A]">{p.description}</div>}
                  </div>
                ))}
              </section>
            )}

            {/* Publications */}
            {cv.publications?.length > 0 && (
              <section className="mt-5">
                <h3 className="font-bold text-[12px] uppercase tracking-wider text-[#1F2937] pb-1 border-b border-[#9CA3AF] mb-3">Publications</h3>
                {cv.publications.map((p, i) => {
                  const isObj = p && typeof p === "object";
                  const title = isObj ? p.title : p;
                  const publisher = isObj ? p.publisher : "";
                  const year = isObj ? p.year : "";
                  const desc = isObj ? p.description : "";
                  return (
                    <div key={i} className="mb-3 last:mb-0">
                      <div className="flex justify-between items-baseline gap-4">
                        <div className="font-semibold text-[14px] text-[#0A0A0A]">{title}</div>
                        <div className="text-[14px] text-[#0A0A0A] whitespace-nowrap">{[publisher, year].filter(Boolean).join(", ")}</div>
                      </div>
                      {desc && <div className="text-[14px] text-[#0A0A0A]">{desc}</div>}
                    </div>
                  );
                })}
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

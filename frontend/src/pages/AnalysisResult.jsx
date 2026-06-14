import React, { useEffect, useState } from "react";
import { useParams, Link, useNavigate } from "react-router-dom";
import Navbar from "../components/Navbar";
import api, { API_BASE } from "../lib/api";
import { toast } from "sonner";
import { ArrowRight, CheckCircle, XCircle, Sparkle, FileText, EnvelopeSimple, DownloadSimple } from "@phosphor-icons/react";

function scoreClass(s) {
  if (s >= 80) return "text-[#00C853]";
  if (s >= 60) return "text-[#0A0A0A]";
  return "text-[#FF2A2A]";
}

function Bar({ label, value }) {
  const v = Math.max(0, Math.min(100, value || 0));
  const color = v >= 70 ? "bg-[#00C853]" : v >= 50 ? "bg-[#0A0A0A]" : "bg-[#FF2A2A]";
  return (
    <div className="flex items-center gap-3">
      <div className="w-44 text-xs text-zinc-700">{label}</div>
      <div className="flex-1 h-2 bg-zinc-100">
        <div className={`h-2 ${color}`} style={{ width: `${v}%` }} />
      </div>
      <div className="font-mono-data text-xs w-10 text-right">{v}</div>
    </div>
  );
}

export default function AnalysisResult() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [analysis, setAnalysis] = useState(null);
  const [loading, setLoading] = useState(true);
  const [optimizing, setOptimizing] = useState(false);

  useEffect(() => {
    api.get(`/analyses/${id}`)
      .then((r) => setAnalysis(r.data))
      .catch(() => toast.error("Analysis not found"))
      .finally(() => setLoading(false));
  }, [id]);

  const onOptimize = async () => {
    setOptimizing(true);
    try {
      const { data } = await api.post("/optimize", { analysis_id: id });
      toast.success("Optimized CV ready");
      navigate(`/optimized/${data.id}`);
    } catch (err) {
      toast.error(err?.response?.data?.detail || "Optimization failed");
    } finally {
      setOptimizing(false);
    }
  };

  if (loading) return (
    <div className="min-h-screen bg-white"><Navbar />
      <div className="max-w-7xl mx-auto px-6 py-20 font-mono-data text-sm text-zinc-500">Loading analysis…</div>
    </div>
  );
  if (!analysis) return null;

  const sb = analysis.score_breakdown || {};

  return (
    <div className="min-h-screen bg-white">
      <Navbar />
      <div className="max-w-7xl mx-auto px-6 py-10">
        <div className="flex items-end justify-between flex-wrap gap-4 mb-8">
          <div>
            <div className="font-mono-data text-xs uppercase text-zinc-500 mb-3">// Analysis result</div>
            <h1 className="font-display font-black text-4xl lg:text-5xl tracking-tighter leading-none">
              {analysis.job_title}<br/><span className="text-zinc-500 text-2xl">@ {analysis.company}</span>
            </h1>
          </div>
          <button onClick={onOptimize} disabled={optimizing} data-testid="optimize-button"
            className="bg-[#002FA7] text-white px-6 py-4 font-display font-bold flex items-center gap-2 brutalist-shadow-hover transition-all disabled:opacity-60">
            {optimizing ? "Optimizing CV…" : <>Optimize CV + Cover Letter <Sparkle size={18} weight="fill" /></>}
          </button>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-0 border border-zinc-200 mb-6">
          {/* ATS Score */}
          <div className="lg:col-span-1 p-8 border-r border-zinc-200">
            <div className="font-mono-data text-xs uppercase text-zinc-500 mb-3">ATS score</div>
            <div className={`font-display font-black text-8xl leading-none ${scoreClass(analysis.ats_score)}`} data-testid="ats-score-display">
              {analysis.ats_score}
              <span className="font-mono-data text-2xl text-zinc-400">/100</span>
            </div>
            <p className="mt-4 text-sm text-zinc-600 leading-relaxed">{analysis.overall_recommendation}</p>
          </div>
          {/* Breakdown */}
          <div className="lg:col-span-2 p-8">
            <div className="font-mono-data text-xs uppercase text-zinc-500 mb-4">Score breakdown</div>
            <div className="space-y-3" data-testid="score-breakdown">
              <Bar label="Keyword match" value={sb.keyword_match} />
              <Bar label="Skills alignment" value={sb.skills_alignment} />
              <Bar label="Experience relevance" value={sb.experience_relevance} />
              <Bar label="Formatting / ATS safety" value={sb.formatting_ats_safety} />
            </div>
          </div>
        </div>

        {/* Keywords */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-0 border border-zinc-200 mb-6">
          <div className="p-8 border-r border-zinc-200">
            <div className="flex items-center gap-2 mb-4">
              <CheckCircle size={18} weight="fill" className="text-[#00C853]" />
              <span className="font-mono-data text-xs uppercase text-zinc-500">Matched keywords</span>
              <span className="font-mono-data text-xs text-zinc-400 ml-auto">{analysis.matched_keywords?.length || 0}</span>
            </div>
            <div className="flex flex-wrap gap-2" data-testid="matched-keywords">
              {(analysis.matched_keywords || []).map(k => (
                <span key={k} className="font-mono-data text-xs bg-zinc-100 border border-zinc-200 text-[#0A0A0A] px-2 py-1">{k}</span>
              ))}
              {!analysis.matched_keywords?.length && <span className="text-sm text-zinc-500">None detected.</span>}
            </div>
          </div>
          <div className="p-8">
            <div className="flex items-center gap-2 mb-4">
              <XCircle size={18} weight="fill" className="text-[#FF2A2A]" />
              <span className="font-mono-data text-xs uppercase text-zinc-500">Missing keywords</span>
              <span className="font-mono-data text-xs text-zinc-400 ml-auto">{analysis.missing_keywords?.length || 0}</span>
            </div>
            <div className="flex flex-wrap gap-2" data-testid="missing-keywords">
              {(analysis.missing_keywords || []).map(k => (
                <span key={k} className="font-mono-data text-xs bg-white border border-[#FF2A2A] text-[#FF2A2A] px-2 py-1">{k}</span>
              ))}
              {!analysis.missing_keywords?.length && <span className="text-sm text-zinc-500">None — strong match.</span>}
            </div>
          </div>
        </div>

        {/* Gaps & Strengths */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-0 border border-zinc-200 mb-6">
          <div className="p-8 border-r border-zinc-200">
            <div className="font-mono-data text-xs uppercase text-zinc-500 mb-4">Gaps to address</div>
            <ul className="space-y-2 text-sm" data-testid="gaps-list">
              {(analysis.gaps || []).map((g, i) => (
                <li key={i} className="flex gap-3"><span className="font-mono-data text-[#FF2A2A]">→</span><span>{g}</span></li>
              ))}
            </ul>
          </div>
          <div className="p-8">
            <div className="font-mono-data text-xs uppercase text-zinc-500 mb-4">Strengths</div>
            <ul className="space-y-2 text-sm" data-testid="strengths-list">
              {(analysis.strengths || []).map((g, i) => (
                <li key={i} className="flex gap-3"><span className="font-mono-data text-[#00C853]">✓</span><span>{g}</span></li>
              ))}
            </ul>
          </div>
        </div>

        {/* Section suggestions */}
        <div className="border border-zinc-200 p-8 mb-6">
          <div className="font-mono-data text-xs uppercase text-zinc-500 mb-4">Section-by-section suggestions</div>
          <div className="grid md:grid-cols-2 gap-x-8 gap-y-5" data-testid="section-suggestions">
            {Object.entries(analysis.section_suggestions || {}).map(([k, v]) => (
              <div key={k}>
                <div className="font-display font-bold text-sm uppercase tracking-tight mb-1 text-[#002FA7]">{k.replace(/_/g, " ")}</div>
                <div className="text-sm text-zinc-700 leading-relaxed">{v}</div>
              </div>
            ))}
          </div>
        </div>

        <div className="flex justify-end gap-3">
          <Link to="/dashboard" data-testid="back-to-dashboard"
            className="border border-[#0A0A0A] px-6 py-3 font-medium hover:bg-[#0A0A0A] hover:text-white transition-colors">
            ← Dashboard
          </Link>
          <button onClick={onOptimize} disabled={optimizing} data-testid="optimize-button-bottom"
            className="bg-[#002FA7] text-white px-6 py-3 font-medium flex items-center gap-2 hover:bg-[#0A0A0A] transition-colors disabled:opacity-60">
            {optimizing ? "Optimizing…" : "Optimize CV + Cover Letter"} <Sparkle size={16} weight="fill" />
          </button>
        </div>
      </div>
    </div>
  );
}

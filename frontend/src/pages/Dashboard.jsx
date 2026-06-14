import React, { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import Navbar from "../components/Navbar";
import api from "../lib/api";
import { useAuth } from "../contexts/AuthContext";
import { ArrowRight, FileText, ChartLineUp } from "@phosphor-icons/react";

function scoreColor(s) {
  if (s >= 80) return "text-[#00C853]";
  if (s >= 60) return "text-[#0A0A0A]";
  return "text-[#FF2A2A]";
}

export default function Dashboard() {
  const { user } = useAuth();
  const [analyses, setAnalyses] = useState([]);
  const [cvs, setCvs] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    (async () => {
      try {
        const [a, c] = await Promise.all([api.get("/analyses"), api.get("/cv/list")]);
        setAnalyses(a.data);
        setCvs(c.data);
      } finally { setLoading(false); }
    })();
  }, []);

  return (
    <div className="min-h-screen bg-white">
      <Navbar />
      <div className="max-w-7xl mx-auto px-6 py-12">
        <div className="flex flex-wrap items-end justify-between gap-4 mb-10">
          <div>
            <div className="font-mono-data text-xs uppercase text-zinc-500 mb-3" data-testid="dashboard-greeting">// {user?.name}</div>
            <h1 className="font-display font-black text-5xl tracking-tighter leading-none">Control room.</h1>
          </div>
          <Link to="/optimize" data-testid="dashboard-new-analysis"
            className="bg-[#002FA7] text-white px-6 py-4 font-medium flex items-center gap-2 brutalist-shadow-hover transition-all">
            + New analysis <ArrowRight size={18} weight="bold" />
          </Link>
        </div>

        {/* Stats */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-0 border border-zinc-200 mb-10">
          <div className="p-6 border-r border-zinc-200">
            <div className="font-mono-data text-xs uppercase text-zinc-500 mb-3">CVs uploaded</div>
            <div className="font-display font-black text-4xl" data-testid="stat-cvs">{cvs.length}</div>
          </div>
          <div className="p-6 border-r border-zinc-200">
            <div className="font-mono-data text-xs uppercase text-zinc-500 mb-3">Analyses</div>
            <div className="font-display font-black text-4xl" data-testid="stat-analyses">{analyses.length}</div>
          </div>
          <div className="p-6 border-r border-zinc-200">
            <div className="font-mono-data text-xs uppercase text-zinc-500 mb-3">Avg. ATS</div>
            <div className="font-display font-black text-4xl">
              {analyses.length ? Math.round(analyses.reduce((s,a)=>s+a.ats_score,0)/analyses.length) : "—"}
            </div>
          </div>
          <div className="p-6">
            <div className="font-mono-data text-xs uppercase text-zinc-500 mb-3">Best score</div>
            <div className="font-display font-black text-4xl text-[#002FA7]">
              {analyses.length ? Math.max(...analyses.map(a=>a.ats_score)) : "—"}
            </div>
          </div>
        </div>

        {/* Analyses list */}
        <div className="mb-4 flex items-center justify-between">
          <h2 className="font-display font-black text-2xl tracking-tight">Recent analyses</h2>
          <span className="font-mono-data text-xs text-zinc-500">{analyses.length} TOTAL</span>
        </div>
        {loading ? (
          <div className="border border-zinc-200 p-12 text-center font-mono-data text-sm text-zinc-500">Loading…</div>
        ) : analyses.length === 0 ? (
          <div className="border border-zinc-200 p-12 text-center" data-testid="empty-state">
            <ChartLineUp size={40} weight="thin" className="mx-auto mb-3 text-zinc-400" />
            <p className="text-zinc-600 mb-4">No analyses yet. Run your first one — it takes under a minute.</p>
            <Link to="/optimize" data-testid="empty-cta"
              className="inline-flex items-center gap-2 bg-[#0A0A0A] text-white px-5 py-3 font-medium hover:bg-[#002FA7] transition-colors">
              Start analysis <ArrowRight size={16} weight="bold" />
            </Link>
          </div>
        ) : (
          <div className="border border-zinc-200 divide-y divide-zinc-200" data-testid="analyses-list">
            {analyses.map(a => (
              <Link key={a.id} to={`/analysis/${a.id}`} data-testid={`analysis-row-${a.id}`}
                className="flex items-center gap-6 p-6 hover:bg-zinc-50 transition-colors">
                <div className={`font-display font-black text-4xl w-20 ${scoreColor(a.ats_score)}`}>{a.ats_score}</div>
                <div className="flex-1 min-w-0">
                  <div className="font-display font-bold text-lg tracking-tight truncate">{a.job_title}</div>
                  <div className="text-sm text-zinc-600 truncate">{a.company}</div>
                </div>
                <div className="font-mono-data text-xs text-zinc-500 hidden md:block">
                  {new Date(a.created_at).toLocaleDateString()}
                </div>
                <ArrowRight size={20} weight="bold" className="text-zinc-400" />
              </Link>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

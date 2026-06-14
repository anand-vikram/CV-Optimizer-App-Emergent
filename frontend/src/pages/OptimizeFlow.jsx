import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import Navbar from "../components/Navbar";
import api from "../lib/api";
import { toast } from "sonner";
import { Upload, ArrowRight, FileText, CheckCircle, Circle } from "@phosphor-icons/react";

export default function OptimizeFlow() {
  const navigate = useNavigate();
  const [step, setStep] = useState(1);

  // step 1 - upload
  const [file, setFile] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [cv, setCv] = useState(null);

  // step 2 - JD
  const [jobTitle, setJobTitle] = useState("");
  const [company, setCompany] = useState("");
  const [jd, setJd] = useState("");
  const [analyzing, setAnalyzing] = useState(false);

  const onUpload = async (e) => {
    e.preventDefault();
    if (!file) return;
    setUploading(true);
    try {
      const fd = new FormData();
      fd.append("file", file);
      const { data } = await api.post("/cv/upload", fd, { headers: { "Content-Type": "multipart/form-data" } });
      setCv(data);
      toast.success("CV uploaded & parsed");
      setStep(2);
    } catch (err) {
      toast.error(err?.response?.data?.detail || "Upload failed");
    } finally {
      setUploading(false);
    }
  };

  const onAnalyze = async (e) => {
    e.preventDefault();
    if (!cv) return;
    setAnalyzing(true);
    try {
      const { data } = await api.post("/analyze", {
        cv_id: cv.id, job_title: jobTitle, company, job_description: jd,
      });
      toast.success(`Analysis complete · ATS ${data.ats_score}/100`);
      navigate(`/analysis/${data.id}`);
    } catch (err) {
      toast.error(err?.response?.data?.detail || "Analysis failed");
    } finally {
      setAnalyzing(false);
    }
  };

  const Stepper = ({ step }) => (
    <div className="flex items-center gap-4 mb-10" data-testid="stepper">
      {[
        [1, "Upload CV"],
        [2, "Job description"],
        [3, "Analyze"],
      ].map(([n, label], i) => (
        <React.Fragment key={n}>
          <div className="flex items-center gap-2">
            {step > n ? <CheckCircle size={20} weight="fill" className="text-[#00C853]" />
              : step === n ? <Circle size={20} weight="fill" className="text-[#002FA7]" />
              : <Circle size={20} weight="bold" className="text-zinc-300" />}
            <span className={`font-mono-data text-xs uppercase ${step >= n ? "text-[#0A0A0A]" : "text-zinc-400"}`}>{n}. {label}</span>
          </div>
          {i < 2 && <div className="flex-1 h-px bg-zinc-200" />}
        </React.Fragment>
      ))}
    </div>
  );

  return (
    <div className="min-h-screen bg-white">
      <Navbar />
      <div className="max-w-3xl mx-auto px-6 py-12">
        <div className="font-mono-data text-xs uppercase text-zinc-500 mb-3">// New analysis</div>
        <h1 className="font-display font-black text-5xl tracking-tighter mb-10 leading-none">Optimize a CV.</h1>

        <Stepper step={step} />

        {step === 1 && (
          <form onSubmit={onUpload} className="border border-zinc-200 p-8 brutalist-shadow fade-up">
            <h2 className="font-display font-bold text-2xl mb-2 tracking-tight">Upload your CV</h2>
            <p className="text-sm text-zinc-600 mb-6">PDF, DOCX, or TXT. Max 5MB.</p>
            <label htmlFor="cv-file" data-testid="cv-upload-dropzone"
              className="block border-2 border-dashed border-zinc-300 p-12 text-center hover:border-[#002FA7] hover:bg-zinc-50 transition-colors cursor-pointer">
              <Upload size={32} weight="bold" className="mx-auto mb-3 text-zinc-500" />
              <div className="font-medium mb-1">{file ? file.name : "Click to choose a file"}</div>
              <div className="font-mono-data text-xs text-zinc-500">{file ? `${(file.size/1024).toFixed(1)} KB` : "or drag and drop"}</div>
              <input id="cv-file" type="file" accept=".pdf,.docx,.txt" hidden
                data-testid="cv-file-input"
                onChange={(e)=>setFile(e.target.files?.[0] || null)} />
            </label>
            <button type="submit" disabled={!file || uploading} data-testid="cv-upload-submit"
              className="mt-6 w-full bg-[#0A0A0A] text-white py-4 font-display font-bold flex items-center justify-center gap-2 hover:bg-[#002FA7] transition-colors disabled:opacity-40 disabled:cursor-not-allowed">
              {uploading ? "Parsing CV…" : "Upload & continue"} <ArrowRight size={16} weight="bold" />
            </button>
          </form>
        )}

        {step === 2 && (
          <form onSubmit={onAnalyze} className="border border-zinc-200 p-8 brutalist-shadow fade-up space-y-5">
            <div className="flex items-center gap-3 mb-2 border-b border-zinc-200 pb-3">
              <FileText size={18} weight="bold" className="text-[#00C853]" />
              <span className="font-mono-data text-xs uppercase text-zinc-600" data-testid="parsed-cv-filename">{cv?.filename}</span>
              <span className="font-mono-data text-xs text-zinc-400 ml-auto">{cv?.text_length} chars extracted</span>
            </div>
            <h2 className="font-display font-bold text-2xl tracking-tight">Target job details</h2>
            <div>
              <label className="block font-mono-data text-xs uppercase text-zinc-500 mb-2">Job title</label>
              <input required value={jobTitle} onChange={(e)=>setJobTitle(e.target.value)} data-testid="jd-title-input"
                placeholder="e.g. Senior Data Engineer"
                className="w-full border border-zinc-300 px-4 py-3 focus:border-[#002FA7] focus:outline-none font-medium" />
            </div>
            <div>
              <label className="block font-mono-data text-xs uppercase text-zinc-500 mb-2">Company</label>
              <input required value={company} onChange={(e)=>setCompany(e.target.value)} data-testid="jd-company-input"
                placeholder="e.g. Stripe"
                className="w-full border border-zinc-300 px-4 py-3 focus:border-[#002FA7] focus:outline-none font-medium" />
            </div>
            <div>
              <label className="block font-mono-data text-xs uppercase text-zinc-500 mb-2">Job description</label>
              <textarea required rows={10} value={jd} onChange={(e)=>setJd(e.target.value)} data-testid="jd-description-input"
                placeholder="Paste the full job description here…"
                className="w-full border border-zinc-300 px-4 py-3 focus:border-[#002FA7] focus:outline-none font-medium resize-y" />
              <p className="text-xs text-zinc-500 mt-1 font-mono-data">{jd.length} CHARS · minimum ~200 recommended</p>
            </div>
            <div className="flex gap-3">
              <button type="button" onClick={()=>setStep(1)} data-testid="back-to-upload"
                className="border border-[#0A0A0A] px-6 py-4 font-medium hover:bg-[#0A0A0A] hover:text-white transition-colors">
                ← Back
              </button>
              <button type="submit" disabled={analyzing} data-testid="run-analysis-button"
                className="flex-1 bg-[#002FA7] text-white py-4 font-display font-bold flex items-center justify-center gap-2 hover:bg-[#0A0A0A] transition-colors disabled:opacity-50">
                {analyzing ? "Analyzing with Claude…" : "Run analysis"} <ArrowRight size={16} weight="bold" />
              </button>
            </div>
          </form>
        )}
      </div>
    </div>
  );
}

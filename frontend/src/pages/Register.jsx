import React, { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "../contexts/AuthContext";
import Navbar from "../components/Navbar";
import { toast } from "sonner";
import { ArrowRight } from "@phosphor-icons/react";

export default function Register() {
  const { register } = useAuth();
  const navigate = useNavigate();
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);

  const onSubmit = async (e) => {
    e.preventDefault();
    if (password.length < 6) { toast.error("Password must be at least 6 characters"); return; }
    setLoading(true);
    try {
      await register(name, email, password);
      toast.success("Account created");
      navigate("/dashboard");
    } catch (err) {
      toast.error(err?.response?.data?.detail || "Registration failed");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-white">
      <Navbar />
      <div className="max-w-md mx-auto px-6 py-20">
        <div className="font-mono-data text-xs uppercase text-zinc-500 mb-3">// Create account</div>
        <h1 className="font-display font-black text-5xl tracking-tighter mb-8 leading-none">Start<br/>winning.</h1>
        <form onSubmit={onSubmit} className="border border-zinc-200 p-8 space-y-5 brutalist-shadow">
          <div>
            <label className="block font-mono-data text-xs uppercase text-zinc-500 mb-2">Full name</label>
            <input required value={name} onChange={(e)=>setName(e.target.value)} data-testid="register-name-input"
              className="w-full border border-zinc-300 px-4 py-3 focus:border-[#002FA7] focus:outline-none font-medium" />
          </div>
          <div>
            <label className="block font-mono-data text-xs uppercase text-zinc-500 mb-2">Email</label>
            <input type="email" required value={email} onChange={(e)=>setEmail(e.target.value)} data-testid="register-email-input"
              className="w-full border border-zinc-300 px-4 py-3 focus:border-[#002FA7] focus:outline-none font-medium" />
          </div>
          <div>
            <label className="block font-mono-data text-xs uppercase text-zinc-500 mb-2">Password</label>
            <input type="password" required value={password} onChange={(e)=>setPassword(e.target.value)} data-testid="register-password-input"
              className="w-full border border-zinc-300 px-4 py-3 focus:border-[#002FA7] focus:outline-none font-medium" />
            <p className="text-xs text-zinc-500 mt-1 font-mono-data">Min 6 characters.</p>
          </div>
          <button type="submit" disabled={loading} data-testid="register-submit-button"
            className="w-full bg-[#002FA7] text-white py-4 font-display font-bold flex items-center justify-center gap-2 hover:bg-[#0A0A0A] transition-colors disabled:opacity-50">
            {loading ? "Creating..." : "Create account"} <ArrowRight size={16} weight="bold" />
          </button>
        </form>
        <p className="mt-6 text-sm text-zinc-600">
          Already have an account? <Link to="/login" className="font-medium text-[#002FA7] underline" data-testid="link-to-login">Sign in →</Link>
        </p>
      </div>
    </div>
  );
}

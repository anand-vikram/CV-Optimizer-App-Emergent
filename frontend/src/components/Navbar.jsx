import React from "react";
import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "../contexts/AuthContext";
import { SignOut, User as UserIcon } from "@phosphor-icons/react";

export default function Navbar() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  const onLogout = () => {
    logout();
    navigate("/");
  };

  return (
    <nav className="border-b border-zinc-200 bg-white sticky top-0 z-40" data-testid="navbar">
      <div className="max-w-7xl mx-auto px-6 py-4 flex items-center justify-between">
        <Link to="/" className="flex items-center gap-3" data-testid="nav-logo">
          <div className="w-8 h-8 bg-[#0A0A0A] flex items-center justify-center">
            <span className="font-display font-black text-white text-sm">CV</span>
          </div>
          <span className="font-display font-black text-lg tracking-tight">ATS<span className="text-[#002FA7]">/</span>OPTIMIZER</span>
        </Link>
        <div className="flex items-center gap-6 text-sm">
          {user ? (
            <>
              <Link to="/dashboard" className="font-medium hover:text-[#002FA7] transition-colors" data-testid="nav-dashboard">Dashboard</Link>
              <Link to="/optimize" className="font-medium hover:text-[#002FA7] transition-colors" data-testid="nav-new">+ New Analysis</Link>
              <div className="flex items-center gap-2 font-mono-data text-xs text-zinc-600 border-l border-zinc-200 pl-6">
                <UserIcon size={14} weight="bold" />
                <span data-testid="nav-user-name">{user.name}</span>
              </div>
              <button onClick={onLogout} data-testid="nav-logout" className="flex items-center gap-1 text-sm font-medium hover:text-[#FF2A2A] transition-colors">
                <SignOut size={14} weight="bold" /> Logout
              </button>
            </>
          ) : (
            <>
              <Link to="/login" className="font-medium hover:text-[#002FA7] transition-colors" data-testid="nav-login">Login</Link>
              <Link to="/register" data-testid="nav-register"
                className="bg-[#0A0A0A] text-white px-4 py-2 font-medium hover:bg-[#002FA7] transition-colors brutalist-shadow-hover">
                Get Started →
              </Link>
            </>
          )}
        </div>
      </div>
    </nav>
  );
}

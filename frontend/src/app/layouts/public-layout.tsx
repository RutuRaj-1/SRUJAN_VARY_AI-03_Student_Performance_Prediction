import React, { useState } from 'react';
import { Outlet, Link, useLocation } from 'react-router-dom';
import {
  Menu,
  X,
  ArrowRight,
  ChevronDown,
  Layers,
  Database,
  CheckCircle2,
  Award,
  AlertTriangle,
  BookOpen,
  Briefcase,
  LogIn,
} from 'lucide-react';
import { Button } from '@/components/ui/button';

export const PublicLayout: React.FC = () => {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const [modulesDropdownOpen, setModulesDropdownOpen] = useState(false);
  const location = useLocation();

  const navLinks = [
    { label: 'The Problem', path: '/problem' },
    { label: 'Our Solution', path: '/solution' },
    { label: 'Architecture', path: '/architecture' },
    { label: 'Differentiators', path: '/differentiators' },
    { label: 'Role Ecosystem', path: '/roles' },
  ];

  const modulesList = [
    { num: '01', name: 'AI Syllabus Intelligence', path: '/modules/syllabus', icon: Database },
    { num: '02', name: 'Academic Data Intelligence Hub', path: '/modules/academic-data', icon: Layers },
    { num: '03', name: 'Assessment & Attentiveness Engine', path: '/modules/assessments', icon: CheckCircle2 },
    { num: '04', name: 'Mastery & Performance Analytics', path: '/modules/mastery', icon: Award },
    { num: '05', name: 'Academic Risk Prediction Engine', path: '/modules/risk', icon: AlertTriangle },
    { num: '06', name: 'Personalized Academic Intervention', path: '/modules/interventions', icon: BookOpen },
    { num: '07', name: 'Career Readiness Intelligence', path: '/modules/career', icon: Briefcase },
  ];

  return (
    <div className="min-h-screen flex flex-col bg-[#F7FAF9] text-[#172825] font-sans antialiased">
      {/* 1. PUBLIC TOPBAR NAVIGATION */}
      <header className="sticky top-0 z-40 bg-white/95 backdrop-blur-sm border-b border-[#DCE6E2]">
        <div className="max-w-7xl mx-auto px-6 h-16 flex items-center justify-between">
          {/* Left: Brand */}
          <Link to="/" className="flex items-center gap-3 group">
            <div className="h-9 w-9 rounded-[4px] bg-[#123E40] text-white flex items-center justify-center font-bold text-lg tracking-wider shadow-sm group-hover:bg-[#237277] transition-colors">
              M
            </div>
            <div>
              <div className="flex items-center gap-2">
                <span className="font-bold text-lg text-[#172825] tracking-tight font-sans">MASTERY</span>
                <span className="text-[10px] font-mono bg-[#EEF8F7] text-[#123E40] px-1.5 py-0.5 rounded-[2px] border border-[#BDCEC8]">
                  SRUJAN 2026
                </span>
              </div>
              <p className="text-[11px] text-[#687A75] font-medium leading-none hidden sm:block">
                Beyond Marks. Towards Mastery.
              </p>
            </div>
          </Link>

          {/* Center: Navigation Links */}
          <nav className="hidden lg:flex items-center gap-6 text-xs font-semibold text-[#40524E]">
            <Link
              to="/problem"
              className={`hover:text-[#237277] transition-colors ${
                location.pathname === '/problem' ? 'text-[#237277] font-bold' : ''
              }`}
            >
              The Problem
            </Link>

            <Link
              to="/solution"
              className={`hover:text-[#237277] transition-colors ${
                location.pathname === '/solution' ? 'text-[#237277] font-bold' : ''
              }`}
            >
              Our Solution
            </Link>

            {/* Modules Dropdown */}
            <div className="relative">
              <button
                onClick={() => setModulesDropdownOpen(!modulesDropdownOpen)}
                onMouseEnter={() => setModulesDropdownOpen(true)}
                className={`flex items-center gap-1 hover:text-[#237277] transition-colors ${
                  location.pathname.startsWith('/modules') ? 'text-[#237277] font-bold' : ''
                }`}
              >
                <span>Seven Modules</span>
                <ChevronDown className="h-3 w-3" />
              </button>

              {modulesDropdownOpen && (
                <div
                  onMouseLeave={() => setModulesDropdownOpen(false)}
                  className="absolute top-full left-0 mt-2 w-72 rounded-[6px] bg-white border border-[#DCE6E2] shadow-lg p-2 z-50 animate-in fade-in slide-in-from-top-1 duration-150"
                >
                  <Link
                    to="/modules"
                    onClick={() => setModulesDropdownOpen(false)}
                    className="block px-3 py-2 text-xs font-bold text-[#123E40] hover:bg-[#EEF8F7] rounded-[4px] border-b border-[#DCE6E2] mb-1"
                  >
                    All Seven Modules Overview →
                  </Link>
                  {modulesList.map((m) => {
                    const Icon = m.icon;
                    return (
                      <Link
                        key={m.num}
                        to={m.path}
                        onClick={() => setModulesDropdownOpen(false)}
                        className="flex items-center gap-2.5 px-3 py-2 rounded-[4px] text-xs text-[#40524E] hover:bg-[#EEF8F7] hover:text-[#172825] transition-colors"
                      >
                        <span className="font-mono text-[10px] font-bold text-[#237277] w-5">M{m.num}</span>
                        <Icon className="h-3.5 w-3.5 text-[#687A75]" />
                        <span className="truncate">{m.name}</span>
                      </Link>
                    );
                  })}
                </div>
              )}
            </div>

            <Link
              to="/architecture"
              className={`hover:text-[#237277] transition-colors ${
                location.pathname === '/architecture' ? 'text-[#237277] font-bold' : ''
              }`}
            >
              Architecture
            </Link>

            <Link
              to="/differentiators"
              className={`hover:text-[#237277] transition-colors ${
                location.pathname === '/differentiators' ? 'text-[#237277] font-bold' : ''
              }`}
            >
              Differentiators
            </Link>

            <Link
              to="/roles"
              className={`hover:text-[#237277] transition-colors ${
                location.pathname === '/roles' ? 'text-[#237277] font-bold' : ''
              }`}
            >
              Role Ecosystem
            </Link>
          </nav>

          {/* Right: Actions */}
          <div className="flex items-center gap-3">
            <Link to="/login" className="hidden sm:inline-block">
              <Button variant="outline" size="sm" className="text-xs border-[#BDCEC8]">
                <LogIn className="h-3.5 w-3.5 mr-1 text-[#237277]" />
                <span>Institutional Login</span>
              </Button>
            </Link>

            <Link to="/app/dashboard">
              <Button variant="primary" size="sm" className="gap-1.5 text-xs shadow-sm">
                <span>Enter Workspace</span>
                <ArrowRight className="h-3.5 w-3.5" />
              </Button>
            </Link>

            {/* Mobile Hamburger Toggle */}
            <button
              onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
              className="lg:hidden p-2 text-[#40524E] hover:text-[#172825]"
              title="Toggle Navigation Menu"
            >
              {mobileMenuOpen ? <X className="h-5 w-5" /> : <Menu className="h-5 w-5" />}
            </button>
          </div>
        </div>

        {/* Mobile Navigation Drawer */}
        {mobileMenuOpen && (
          <div className="lg:hidden border-t border-[#DCE6E2] bg-white px-6 py-4 space-y-3 text-sm">
            {navLinks.map((link) => (
              <Link
                key={link.path}
                to={link.path}
                onClick={() => setMobileMenuOpen(false)}
                className="block py-1 text-[#40524E] hover:text-[#237277] font-medium"
              >
                {link.label}
              </Link>
            ))}

            <Link
              to="/modules"
              onClick={() => setMobileMenuOpen(false)}
              className="block py-1 text-[#40524E] hover:text-[#237277] font-medium"
            >
              Seven Modules Overview
            </Link>

            <div className="pt-3 border-t border-[#DCE6E2] space-y-2">
              <Link to="/login" onClick={() => setMobileMenuOpen(false)} className="block">
                <Button variant="outline" size="sm" className="w-full text-xs">
                  Institutional Login
                </Button>
              </Link>
              <Link to="/app/dashboard" onClick={() => setMobileMenuOpen(false)} className="block">
                <Button variant="primary" size="sm" className="w-full text-xs">
                  Enter Platform Workspace
                </Button>
              </Link>
            </div>
          </div>
        )}
      </header>

      {/* 2. MAIN PAGE CONTENT */}
      <main className="flex-1">
        <Outlet />
      </main>

      {/* 3. PUBLIC INSTITUTIONAL FOOTER */}
      <footer className="bg-[#0C2D2F] text-slate-300 border-t border-[#18575A] text-xs">
        <div className="max-w-7xl mx-auto px-6 py-12">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-8 mb-8">
            {/* Col 1: Platform Info */}
            <div className="space-y-3">
              <div className="flex items-center gap-2">
                <div className="h-7 w-7 rounded-[3px] bg-[#237277] text-white flex items-center justify-center font-bold text-sm">
                  M
                </div>
                <span className="font-bold text-white text-base font-sans tracking-tight">MASTERY</span>
              </div>
              <p className="text-slate-400 text-xs leading-relaxed">
                An evidence-driven student academic performance prediction and mastery intelligence ecosystem.
              </p>
              <div className="text-[11px] font-mono text-[#BDCEC8]">
                SRUJAN 2026 · Problem Statement AI-03<br />
                Track: AI, CyberSecurity and Digital Trust
              </div>
            </div>

            {/* Col 2: Public Pages */}
            <div className="space-y-2">
              <h4 className="font-bold text-white uppercase text-[11px] tracking-wider font-mono">Platform Overview</h4>
              <ul className="space-y-1.5 text-slate-400">
                <li><Link to="/problem" className="hover:text-white transition-colors">The Problem</Link></li>
                <li><Link to="/solution" className="hover:text-white transition-colors">Our Solution Workflow</Link></li>
                <li><Link to="/modules" className="hover:text-white transition-colors">Seven Business Modules</Link></li>
                <li><Link to="/architecture" className="hover:text-white transition-colors">System Architecture</Link></li>
                <li><Link to="/differentiators" className="hover:text-white transition-colors">Technical Differentiators</Link></li>
                <li><Link to="/roles" className="hover:text-white transition-colors">Role-Based Ecosystem</Link></li>
              </ul>
            </div>

            {/* Col 3: Modules Suite */}
            <div className="space-y-2">
              <h4 className="font-bold text-white uppercase text-[11px] tracking-wider font-mono">Business Modules</h4>
              <ul className="space-y-1.5 text-slate-400 text-[11px]">
                <li><Link to="/modules/syllabus" className="hover:text-white">M01: AI Syllabus Intelligence</Link></li>
                <li><Link to="/modules/academic-data" className="hover:text-white">M02: Academic Data Hub</Link></li>
                <li><Link to="/modules/assessments" className="hover:text-white">M03: Assessment Engine</Link></li>
                <li><Link to="/modules/mastery" className="hover:text-white">M04: Mastery Analytics</Link></li>
                <li><Link to="/modules/risk" className="hover:text-white">M05: Academic Risk Engine</Link></li>
                <li><Link to="/modules/interventions" className="hover:text-white">M06: Personalized Interventions</Link></li>
                <li><Link to="/modules/career" className="hover:text-white">M07: Career Readiness</Link></li>
              </ul>
            </div>

            {/* Col 4: Ethical AI Charter & Workspace */}
            <div className="space-y-3">
              <h4 className="font-bold text-white uppercase text-[11px] tracking-wider font-mono">Digital Trust & Access</h4>
              <p className="text-slate-400 text-xs leading-relaxed">
                MASTERY enforces strict algorithmic firewalls to prevent recruitment discrimination and temporal data leakage.
              </p>
              <Link to="/app/dashboard" className="inline-block">
                <Button variant="primary" size="sm" className="bg-[#237277] hover:bg-[#18575A] text-white text-xs">
                  Launch Application Workspace →
                </Button>
              </Link>
            </div>
          </div>

          <div className="pt-6 border-t border-[#18575A] flex flex-col md:flex-row items-center justify-between gap-4 text-[11px] text-slate-400">
            <div>
              © 2026 MASTERY · Team VARY · Beyond Marks. Towards Mastery.
            </div>
            <div className="font-mono">
              Designed for Higher Education Institutions
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
};

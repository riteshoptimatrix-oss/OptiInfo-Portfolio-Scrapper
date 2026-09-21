'use client';

import { useState, useEffect, useSyncExternalStore } from 'react';
import { createPortal } from 'react-dom';
import { WebsiteAnalysis, TechItem, PrimaryTechnology } from '@/lib/types';

interface AnalysisModalProps {
  analysis: WebsiteAnalysis | null;
  isOpen: boolean;
  onClose: () => void;
}

const emptySubscribe = () => () => {};

export default function AnalysisModal({ analysis, isOpen, onClose }: AnalysisModalProps) {
  const isClient = useSyncExternalStore(emptySubscribe, () => true, () => false);
  const [activeTab, setActiveTab] = useState<'overview' | 'techstack' | 'infra' | 'evidence' | 'meta'>('overview');
  const [copiedUrl, setCopiedUrl] = useState(false);
  const [evidenceSearch, setEvidenceSearch] = useState('');

  // Close on ESC key and prevent body background scrolling
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Escape') {
        onClose();
      }
    };
    if (isOpen) {
      window.addEventListener('keydown', handleKeyDown);
      document.body.style.overflow = 'hidden';
    }
    return () => {
      window.removeEventListener('keydown', handleKeyDown);
      document.body.style.overflow = 'unset';
    };
  }, [isOpen, onClose]);

  if (!isOpen || !analysis || !isClient) return null;

  const techStack = analysis.technology_stack || {};
  const infra = analysis.infrastructure || {};
  const performance = (analysis.performance_metrics || {}) as {
    http_response_time_ms?: number;
    script_count?: number;
    stylesheet_count?: number;
    image_count?: number;
  };
  const metadata = analysis.metadata_info || {};
  const backend = techStack.backend;
  const hosting = infra.hosting_provider;
  const dns = infra.dns;
  const ssl = infra.ssl;

  const primary: PrimaryTechnology = analysis.primary_technology || {
    name: analysis.primary_technology_name || 'HTML / CSS / JavaScript',
    type: analysis.primary_technology_type || 'static',
    confidence: analysis.primary_technology_confidence || 90,
    confidence_label: 'High',
    evidence: analysis.primary_technology_evidence || ['HTML5 document structure', 'CSS stylesheets', 'JavaScript assets loaded'],
  };

  const getConfidenceBadge = (conf: number) => {
    if (conf >= 90) {
      return 'bg-emerald-50 text-emerald-800 border-emerald-200 font-bold';
    }
    if (conf >= 75) {
      return 'bg-teal-50 text-teal-800 border-teal-200 font-bold';
    }
    if (conf >= 60) {
      return 'bg-amber-50 text-amber-800 border-amber-200 font-bold';
    }
    return 'bg-stone-100 text-stone-700 border-stone-300 font-medium';
  };

  const getPrimaryTypeLabel = (typeStr: string) => {
    switch (typeStr?.toLowerCase()) {
      case 'cms':
        return 'CMS Platform';
      case 'ecommerce':
        return 'E-Commerce Platform';
      case 'framework':
        return 'Web Application Framework';
      case 'static':
        return 'Static / Traditional Website';
      default:
        return 'Website Platform';
    }
  };

  // Safely extract frontend frameworks vs libraries
  const frontendFws: TechItem[] =
    techStack.frontend_frameworks ||
    (techStack.frontend || []).filter(
      (f) =>
        f.category === 'Core Language' ||
        f.category === 'SPA Framework' ||
        f.category === 'SSR Framework' ||
        ['React', 'Vue.js', 'Angular', 'Svelte', 'Next.js', 'Nuxt.js', 'Astro', 'Remix'].includes(f.name)
    );

  const jsLibs: TechItem[] =
    techStack.javascript_libraries ||
    (techStack.javascript || []).concat(
      (techStack.frontend || []).filter(
        (f) =>
          f.category === 'JavaScript Library' ||
          ['jQuery', 'Lodash', 'GSAP', 'Swiper', 'Axios', 'Moment.js', 'Alpine.js'].includes(f.name)
      )
    );

  const cssFws: TechItem[] = techStack.css_frameworks || techStack.css || [];

  // Count total detected technologies
  const totalDetectedTech = [
    techStack.cms?.name,
    techStack.ecommerce?.name,
    ...(frontendFws.map((t) => t.name) || []),
    ...(jsLibs.map((t) => t.name) || []),
    ...(cssFws.map((t) => t.name) || []),
    backend?.language,
    backend?.framework,
    techStack.server?.name,
    techStack.cdn?.name,
    hosting?.name,
  ].filter(Boolean).length;

  const handleCopyUrl = async () => {
    if (analysis.website_url) {
      await navigator.clipboard.writeText(analysis.website_url);
      setCopiedUrl(true);
      setTimeout(() => setCopiedUrl(false), 2000);
    }
  };

  // Filter evidence list
  const filteredEvidence = (analysis.evidence || []).filter((ev) => {
    if (!evidenceSearch.trim()) return true;
    const q = evidenceSearch.toLowerCase();
    return (
      ev.technology.toLowerCase().includes(q) ||
      (ev.category && ev.category.toLowerCase().includes(q)) ||
      ev.evidence.toLowerCase().includes(q)
    );
  });

  const modalContent = (
    <div
      className="fixed inset-0 z-[99999] flex items-center justify-center p-0 sm:p-4 md:p-6 bg-stone-900/60 backdrop-blur-md transition-opacity duration-200"
      onClick={onClose}
    >
      {/* Off-White Aesthetic Modal Box */}
      <div
        className="w-full h-full sm:max-w-6xl xl:max-w-7xl sm:max-h-[96vh] bg-[#fbfbfa] sm:rounded-2xl shadow-2xl flex flex-col border border-stone-200/90 overflow-hidden text-stone-900"
        onClick={(e) => e.stopPropagation()}
      >
        {/* ===================== OFF-WHITE STICKY HEADER ===================== */}
        <header className="px-5 sm:px-7 py-4 bg-[#fafaf9] text-stone-900 flex flex-col md:flex-row md:items-center justify-between border-b border-stone-200/90 shrink-0 gap-3 shadow-2xs z-30">
          <div className="flex items-center gap-3.5 min-w-0">
            <div className="w-11 h-11 rounded-xl bg-stone-100 border border-stone-200 text-stone-900 flex items-center justify-center font-black text-2xl shadow-xs shrink-0">
              ⚡
            </div>
            <div className="min-w-0 flex-1">
              <div className="flex items-center gap-2.5 flex-wrap">
                <h2 className="text-base sm:text-lg font-black text-stone-900 truncate max-w-lg lg:max-w-2xl tracking-tight">
                  {analysis.page_title || 'Website Technology Analysis'}
                </h2>
                <span className="px-2.5 py-0.5 rounded-full text-xs font-bold bg-emerald-50 text-emerald-800 border border-emerald-200 font-mono">
                  {analysis.http_status ? `${analysis.http_status} OK` : 'Analyzed'}
                </span>
              </div>
              <div className="flex items-center gap-2 mt-1 flex-wrap">
                <a
                  href={analysis.website_url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-xs text-stone-500 hover:text-emerald-700 font-mono truncate max-w-sm sm:max-w-lg transition underline decoration-stone-300"
                >
                  {analysis.website_url}
                </a>
                <button
                  onClick={handleCopyUrl}
                  title="Copy Target URL"
                  className="text-xs px-2.5 py-0.5 rounded-md bg-stone-100 text-stone-700 hover:text-stone-900 hover:bg-stone-200 transition font-mono shrink-0 border border-stone-200"
                >
                  {copiedUrl ? '✓ Copied' : '📋 Copy URL'}
                </button>
              </div>
            </div>
          </div>

          <div className="flex items-center gap-2.5 self-end md:self-auto shrink-0">
            <div className="hidden sm:flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-stone-100 border border-stone-200 text-xs">
              <span className="text-stone-500 font-mono">Engine:</span>
              <span className="font-bold text-stone-800 font-mono">v{analysis.analyzer_version || '2.0'}</span>
            </div>

            <a
              href={analysis.website_url}
              target="_blank"
              rel="noopener noreferrer"
              className="px-3.5 py-2 rounded-xl bg-emerald-600 hover:bg-emerald-700 text-white font-bold text-xs flex items-center gap-1.5 transition shadow-2xs"
            >
              <span>Visit Site</span>
              <span className="text-xs">↗</span>
            </a>

            <button
              onClick={onClose}
              className="px-3.5 py-2 rounded-xl bg-stone-100 hover:bg-rose-50 text-stone-600 hover:text-rose-700 flex items-center gap-1.5 text-xs font-bold transition shadow-2xs border border-stone-200 hover:border-rose-200"
              title="Close Modal (Escape)"
            >
              <span>✕</span>
              <span className="hidden sm:inline">Close</span>
            </button>
          </div>
        </header>

        {/* ===================== OFF-WHITE TAB NAVIGATION ===================== */}
        <nav className="flex items-center gap-1 px-5 sm:px-7 pt-2.5 bg-[#f5f5f4] border-b border-stone-200 shrink-0 overflow-x-auto z-20">
          <button
            onClick={() => setActiveTab('overview')}
            className={`px-4 py-2.5 text-xs sm:text-sm font-bold uppercase tracking-wider border-b-2 transition-all whitespace-nowrap flex items-center gap-1.5 ${
              activeTab === 'overview'
                ? 'border-emerald-600 text-emerald-800 bg-[#fbfbfa] rounded-t-xl shadow-2xs'
                : 'border-transparent text-stone-500 hover:text-stone-800 hover:bg-stone-200/50 rounded-t-xl'
            }`}
          >
            <span>📊</span> Overview
          </button>
          <button
            onClick={() => setActiveTab('techstack')}
            className={`px-4 py-2.5 text-xs sm:text-sm font-bold uppercase tracking-wider border-b-2 transition-all whitespace-nowrap flex items-center gap-1.5 ${
              activeTab === 'techstack'
                ? 'border-emerald-600 text-emerald-800 bg-[#fbfbfa] rounded-t-xl shadow-2xs'
                : 'border-transparent text-stone-500 hover:text-stone-800 hover:bg-stone-200/50 rounded-t-xl'
            }`}
          >
            <span>📦</span> Tech Stack
            <span className="ml-1 px-2 py-0.5 rounded-full text-[11px] bg-stone-200 text-stone-800 font-mono font-bold">
              {totalDetectedTech}
            </span>
          </button>
          <button
            onClick={() => setActiveTab('infra')}
            className={`px-4 py-2.5 text-xs sm:text-sm font-bold uppercase tracking-wider border-b-2 transition-all whitespace-nowrap flex items-center gap-1.5 ${
              activeTab === 'infra'
                ? 'border-emerald-600 text-emerald-800 bg-[#fbfbfa] rounded-t-xl shadow-2xs'
                : 'border-transparent text-stone-500 hover:text-stone-800 hover:bg-stone-200/50 rounded-t-xl'
            }`}
          >
            <span>🔒</span> DNS & SSL
          </button>
          <button
            onClick={() => setActiveTab('evidence')}
            className={`px-4 py-2.5 text-xs sm:text-sm font-bold uppercase tracking-wider border-b-2 transition-all whitespace-nowrap flex items-center gap-1.5 ${
              activeTab === 'evidence'
                ? 'border-emerald-600 text-emerald-800 bg-[#fbfbfa] rounded-t-xl shadow-2xs'
                : 'border-transparent text-stone-500 hover:text-stone-800 hover:bg-stone-200/50 rounded-t-xl'
            }`}
          >
            <span>🔎</span> Evidence Log
            <span className="ml-1 px-2 py-0.5 rounded-full text-[11px] bg-stone-200 text-stone-800 font-mono font-bold">
              {(analysis.evidence || []).length}
            </span>
          </button>
          <button
            onClick={() => setActiveTab('meta')}
            className={`px-4 py-2.5 text-xs sm:text-sm font-bold uppercase tracking-wider border-b-2 transition-all whitespace-nowrap flex items-center gap-1.5 ${
              activeTab === 'meta'
                ? 'border-emerald-600 text-emerald-800 bg-[#fbfbfa] rounded-t-xl shadow-2xs'
                : 'border-transparent text-stone-500 hover:text-stone-800 hover:bg-stone-200/50 rounded-t-xl'
            }`}
          >
            <span>📄</span> Page Meta & Resources
          </button>
        </nav>

        {/* ===================== SCROLLABLE CONTENT BODY ===================== */}
        <main className="flex-1 overflow-y-auto overscroll-contain p-5 sm:p-7 text-stone-800 bg-[#fbfbfa]">
          <div className="space-y-6">

            {/* ==================== TAB 1: OVERVIEW ==================== */}
            {activeTab === 'overview' && (
              <div className="space-y-6">
                {/* Primary Tech Banner (Off-White Premium Theme) */}
                <div className="p-6 sm:p-7 rounded-2xl bg-gradient-to-br from-white via-stone-50 to-stone-100/90 text-stone-900 border border-stone-200/90 shadow-sm relative overflow-hidden">
                  <div className="flex flex-col md:flex-row md:items-center justify-between gap-6 relative z-10">
                    <div className="space-y-2">
                      <div className="flex items-center gap-2">
                        <span className="text-xs uppercase tracking-wider text-emerald-800 font-bold font-mono px-3 py-0.5 rounded-full bg-emerald-100/80 border border-emerald-200">
                          Primary Website Platform
                        </span>
                      </div>
                      <h3 className="text-2xl sm:text-3xl lg:text-4xl font-black tracking-tight text-stone-900">
                        {primary.name}
                      </h3>
                      <p className="text-xs sm:text-sm text-stone-600 font-medium">
                        Architecture Category:{' '}
                        <span className="text-stone-900 font-semibold font-mono bg-stone-200/70 px-2.5 py-0.5 rounded-md border border-stone-300">
                          {getPrimaryTypeLabel(primary.type)}
                        </span>
                      </p>
                    </div>

                    <div className="flex flex-col items-start md:items-end gap-2 bg-white p-4 sm:p-5 rounded-2xl border border-stone-200 shadow-2xs shrink-0">
                      <span className={`px-4 py-1.5 rounded-xl text-xs sm:text-sm font-black border ${getConfidenceBadge(primary.confidence || 0)}`}>
                        {primary.confidence || 0}% Confidence ({primary.confidence_label || 'High'})
                      </span>
                      <span className="text-xs text-stone-500 font-mono flex items-center gap-2 mt-0.5">
                        <span className="w-2.5 h-2.5 rounded-full bg-emerald-500"></span>
                        Verified Fingerprint Signals
                      </span>
                    </div>
                  </div>

                  {primary.evidence && primary.evidence.length > 0 && (
                    <div className="mt-5 pt-4 border-t border-stone-200 flex flex-wrap items-center gap-2 text-xs font-mono text-stone-700">
                      <span className="text-stone-500 font-bold uppercase text-xs">Verified Signals:</span>
                      {primary.evidence.map((ev, i) => (
                        <span key={i} className="px-3 py-1 rounded-lg bg-white text-emerald-800 border border-stone-200 shadow-2xs text-xs font-semibold">
                          ✓ {ev}
                        </span>
                      ))}
                    </div>
                  )}
                </div>

                {/* Quick Metrics Cards */}
                <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
                  <div className="p-4 sm:p-5 rounded-2xl bg-white border border-stone-200 shadow-2xs hover:border-stone-300 transition">
                    <span className="text-xs text-stone-500 font-bold uppercase tracking-wider block mb-1">
                      HTTP Status
                    </span>
                    <span className="text-base sm:text-lg font-black text-emerald-700 flex items-center gap-2">
                      <span className="w-2.5 h-2.5 rounded-full bg-emerald-500"></span>
                      {analysis.http_status || 200} OK
                    </span>
                  </div>

                  <div className="p-4 sm:p-5 rounded-2xl bg-white border border-stone-200 shadow-2xs hover:border-stone-300 transition">
                    <span className="text-xs text-stone-500 font-bold uppercase tracking-wider block mb-1">
                      Response Speed
                    </span>
                    <span className="text-base sm:text-lg font-black text-stone-900">
                      {performance.http_response_time_ms !== undefined ? `${performance.http_response_time_ms} ms` : 'Fast'}
                    </span>
                  </div>

                  <div className="p-4 sm:p-5 rounded-2xl bg-white border border-stone-200 shadow-2xs hover:border-stone-300 transition">
                    <span className="text-xs text-stone-500 font-bold uppercase tracking-wider block mb-1">
                      SSL Security
                    </span>
                    <span className="text-base sm:text-lg font-black text-emerald-700 flex items-center gap-2 truncate">
                      <span>🔒</span>
                      <span className="truncate">{ssl?.enabled ? (ssl.version || 'TLS Secured') : 'Non-SSL'}</span>
                    </span>
                  </div>

                  <div className="p-4 sm:p-5 rounded-2xl bg-white border border-stone-200 shadow-2xs hover:border-stone-300 transition">
                    <span className="text-xs text-stone-500 font-bold uppercase tracking-wider block mb-1">
                      Analysis Timestamp
                    </span>
                    <span className="text-xs font-bold text-stone-800 truncate block mt-1">
                      {analysis.analyzed_at ? new Date(analysis.analyzed_at).toLocaleString() : 'Recent'}
                    </span>
                  </div>
                </div>

                {/* Architecture Summary Cards */}
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  {/* CMS / Framework */}
                  <div className="p-4 sm:p-5 rounded-2xl bg-white border border-stone-200 shadow-2xs space-y-2.5">
                    <div className="flex items-center justify-between border-b border-stone-100 pb-2">
                      <span className="text-xs font-black text-stone-900 uppercase tracking-wider flex items-center gap-2">
                        <span>📦</span> CMS & Framework
                      </span>
                      <span className="text-xs font-bold text-stone-500 font-mono">Frontend</span>
                    </div>
                    <div className="space-y-2">
                      <div>
                        <p className="text-xs text-stone-500 font-medium">CMS Platform:</p>
                        <p className="font-bold text-stone-900 text-sm">{techStack.cms?.name || 'None detected'}</p>
                      </div>
                      <div>
                        <p className="text-xs text-stone-500 font-medium">Frameworks:</p>
                        <p className="font-bold text-stone-900 text-sm">
                          {frontendFws.length > 0 ? frontendFws.map((f) => f.name).join(', ') : 'Standard HTML/JS'}
                        </p>
                      </div>
                    </div>
                  </div>

                  {/* Server & Backend */}
                  <div className="p-4 sm:p-5 rounded-2xl bg-white border border-stone-200 shadow-2xs space-y-2.5">
                    <div className="flex items-center justify-between border-b border-stone-100 pb-2">
                      <span className="text-xs font-black text-stone-900 uppercase tracking-wider flex items-center gap-2">
                        <span>⚙️</span> Backend & Server
                      </span>
                      <span className="text-xs font-bold text-stone-500 font-mono">Backend</span>
                    </div>
                    <div className="space-y-2">
                      <div>
                        <p className="text-xs text-stone-500 font-medium">Backend Language:</p>
                        <p className="font-bold text-stone-900 text-sm">
                          {backend && backend.confidence > 0 ? `${backend.language} ${backend.framework ? `(${backend.framework})` : ''}` : 'Hidden / Client-Side'}
                        </p>
                      </div>
                      <div>
                        <p className="text-xs text-stone-500 font-medium">Web Server:</p>
                        <p className="font-bold text-stone-900 text-sm">{techStack.server?.name || 'Standard Proxy / Cloud'}</p>
                      </div>
                    </div>
                  </div>

                  {/* Cloud & CDN */}
                  <div className="p-4 sm:p-5 rounded-2xl bg-white border border-stone-200 shadow-2xs space-y-2.5">
                    <div className="flex items-center justify-between border-b border-stone-100 pb-2">
                      <span className="text-xs font-black text-stone-900 uppercase tracking-wider flex items-center gap-2">
                        <span>☁️</span> Cloud & CDN
                      </span>
                      <span className="text-xs font-bold text-stone-500 font-mono">Network</span>
                    </div>
                    <div className="space-y-2">
                      <div>
                        <p className="text-xs text-stone-500 font-medium">Hosting Provider:</p>
                        <p className="font-bold text-stone-900 text-sm">{hosting?.name || 'Cloud / Edge Network'}</p>
                      </div>
                      <div>
                        <p className="text-xs text-stone-500 font-medium">CDN / Proxy:</p>
                        <p className="font-bold text-stone-900 text-sm">{techStack.cdn?.name || 'Direct / None detected'}</p>
                      </div>
                    </div>
                  </div>
                </div>

                {/* Google Search Snippet Preview */}
                {metadata.title && (
                  <div className="p-4 sm:p-5 rounded-2xl bg-white border border-stone-200 shadow-2xs space-y-1.5">
                    <span className="text-xs font-black text-stone-900 uppercase tracking-wider block border-b border-stone-100 pb-2">
                      🌐 Search Engine Snippet Preview
                    </span>
                    <div className="pt-1">
                      <p className="text-xs font-mono text-emerald-800 truncate">{analysis.website_url}</p>
                      <h4 className="text-base font-bold text-blue-700 hover:underline cursor-pointer mt-0.5">
                        {metadata.title}
                      </h4>
                      <p className="text-xs text-stone-600 leading-relaxed line-clamp-2 mt-1">
                        {metadata.description || 'No meta description provided by the website.'}
                      </p>
                    </div>
                  </div>
                )}
              </div>
            )}

            {/* ==================== TAB 2: FULL TECH STACK ==================== */}
            {activeTab === 'techstack' && (
              <div className="space-y-5">
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                  {/* 1. CMS Platform */}
                  <div className="p-4 sm:p-5 rounded-2xl bg-white border border-stone-200 shadow-2xs space-y-3 flex flex-col hover:border-stone-300 transition">
                    <div className="flex items-center justify-between border-b border-stone-100 pb-2">
                      <span className="text-xs font-black text-stone-900 uppercase tracking-wider flex items-center gap-2">
                        <span className="text-base">📦</span> CMS Platform
                      </span>
                      <span className="text-xs font-bold text-stone-500">Content Platform</span>
                    </div>
                    {techStack.cms ? (
                      <div className="flex-1 bg-emerald-50/60 p-3.5 rounded-xl border border-emerald-200">
                        <div className="flex items-start justify-between gap-2">
                          <div>
                            <span className="font-black text-stone-900 text-base block">{techStack.cms.name}</span>
                            <span className="text-xs text-emerald-800 font-semibold">{techStack.cms.category || 'Content Platform'}</span>
                          </div>
                          <span className={`px-2.5 py-1 rounded-md text-xs font-black border ${getConfidenceBadge(techStack.cms.confidence)}`}>
                            {techStack.cms.confidence}%
                          </span>
                        </div>
                      </div>
                    ) : (
                      <div className="flex-1 flex items-center justify-center bg-stone-50 rounded-xl border border-dashed border-stone-200 py-6">
                        <span className="text-stone-500 italic text-xs">No CMS detected</span>
                      </div>
                    )}
                  </div>

                  {/* 2. E-Commerce Platform */}
                  <div className="p-4 sm:p-5 rounded-2xl bg-white border border-stone-200 shadow-2xs space-y-3 flex flex-col hover:border-stone-300 transition">
                    <div className="flex items-center justify-between border-b border-stone-100 pb-2">
                      <span className="text-xs font-black text-stone-900 uppercase tracking-wider flex items-center gap-2">
                        <span className="text-base">🛒</span> E-Commerce Platform
                      </span>
                      <span className="text-xs font-bold text-stone-500">Store Engine</span>
                    </div>
                    {techStack.ecommerce ? (
                      <div className="flex-1 bg-blue-50/60 p-3.5 rounded-xl border border-blue-200">
                        <div className="flex items-start justify-between gap-2">
                          <div>
                            <span className="font-black text-stone-900 text-base block">{techStack.ecommerce.name}</span>
                            <span className="text-xs text-blue-800 font-semibold">{techStack.ecommerce.category || 'E-Commerce'}</span>
                          </div>
                          <span className={`px-2.5 py-1 rounded-md text-xs font-black border ${getConfidenceBadge(techStack.ecommerce.confidence)}`}>
                            {techStack.ecommerce.confidence}%
                          </span>
                        </div>
                      </div>
                    ) : (
                      <div className="flex-1 flex items-center justify-center bg-stone-50 rounded-xl border border-dashed border-stone-200 py-6">
                        <span className="text-stone-500 italic text-xs">No E-Commerce platform</span>
                      </div>
                    )}
                  </div>

                  {/* 3. Frontend Frameworks */}
                  <div className="p-4 sm:p-5 rounded-2xl bg-white border border-stone-200 shadow-2xs space-y-3 flex flex-col hover:border-stone-300 transition">
                    <div className="flex items-center justify-between border-b border-stone-100 pb-2">
                      <span className="text-xs font-black text-stone-900 uppercase tracking-wider flex items-center gap-2">
                        <span className="text-base">⚛️</span> Frontend Frameworks
                      </span>
                      <span className="text-xs font-bold text-stone-500">UI Architecture</span>
                    </div>
                    <div className="flex-1 space-y-2">
                      {frontendFws.map((item, idx) => (
                        <div key={idx} className="flex items-center justify-between p-2.5 rounded-lg bg-stone-50 border border-stone-200">
                          <div>
                            <span className="font-bold text-stone-900 text-sm block">{item.name}</span>
                            <span className="text-xs text-stone-500">{item.category || 'Framework'}</span>
                          </div>
                          <span className={`px-2.5 py-0.5 rounded-md text-xs font-bold border ${getConfidenceBadge(item.confidence)}`}>
                            {item.confidence}%
                          </span>
                        </div>
                      ))}
                      {frontendFws.length === 0 && (
                        <div className="h-full min-h-[60px] flex items-center justify-center bg-stone-50 rounded-xl border border-dashed border-stone-200">
                          <span className="text-stone-500 italic text-xs">Standard HTML / JS</span>
                        </div>
                      )}
                    </div>
                  </div>

                  {/* 4. CSS / UI Frameworks */}
                  <div className="p-4 sm:p-5 rounded-2xl bg-white border border-stone-200 shadow-2xs space-y-3 flex flex-col hover:border-stone-300 transition">
                    <div className="flex items-center justify-between border-b border-stone-100 pb-2">
                      <span className="text-xs font-black text-stone-900 uppercase tracking-wider flex items-center gap-2">
                        <span className="text-base">🎨</span> CSS / UI Frameworks
                      </span>
                      <span className="text-xs font-bold text-stone-500">Styling System</span>
                    </div>
                    <div className="flex-1 space-y-2">
                      {cssFws.map((item, idx) => (
                        <div key={idx} className="flex items-center justify-between p-2.5 rounded-lg bg-stone-50 border border-stone-200">
                          <div>
                            <span className="font-bold text-stone-900 text-sm block">{item.name}</span>
                            <span className="text-xs text-stone-500">{item.category || 'CSS Framework'}</span>
                          </div>
                          <span className={`px-2.5 py-0.5 rounded-md text-xs font-bold border ${getConfidenceBadge(item.confidence)}`}>
                            {item.confidence}%
                          </span>
                        </div>
                      ))}
                      {cssFws.length === 0 && (
                        <div className="h-full min-h-[60px] flex items-center justify-center bg-stone-50 rounded-xl border border-dashed border-stone-200">
                          <span className="text-stone-500 italic text-xs">Standard CSS / Custom</span>
                        </div>
                      )}
                    </div>
                  </div>

                  {/* 5. JavaScript Libraries */}
                  <div className="p-4 sm:p-5 rounded-2xl bg-white border border-stone-200 shadow-2xs space-y-3 flex flex-col hover:border-stone-300 transition lg:col-span-2">
                    <div className="flex items-center justify-between border-b border-stone-100 pb-2">
                      <span className="text-xs font-black text-stone-900 uppercase tracking-wider flex items-center gap-2">
                        <span className="text-base">📜</span> JavaScript Libraries & Utilities
                      </span>
                      <span className="text-xs font-bold text-stone-500">{jsLibs.length} Detected</span>
                    </div>
                    <div className="flex-1 grid grid-cols-1 sm:grid-cols-2 gap-2">
                      {jsLibs.map((item, idx) => (
                        <div key={idx} className="flex items-center justify-between p-2.5 rounded-lg bg-stone-50 border border-stone-200">
                          <div>
                            <span className="font-bold text-stone-900 text-sm block">{item.name}</span>
                            <span className="text-xs text-stone-500">JS Library</span>
                          </div>
                          <span className={`px-2.5 py-0.5 rounded-md text-xs font-bold border ${getConfidenceBadge(item.confidence)}`}>
                            {item.confidence}%
                          </span>
                        </div>
                      ))}
                      {jsLibs.length === 0 && (
                        <div className="col-span-full min-h-[60px] flex items-center justify-center bg-stone-50 rounded-xl border border-dashed border-stone-200">
                          <span className="text-stone-500 italic text-xs">Vanilla JavaScript</span>
                        </div>
                      )}
                    </div>
                  </div>

                  {/* 6. Backend Technology */}
                  <div className="p-4 sm:p-5 rounded-2xl bg-white border border-stone-200 shadow-2xs space-y-3 flex flex-col hover:border-stone-300 transition">
                    <div className="flex items-center justify-between border-b border-stone-100 pb-2">
                      <span className="text-xs font-black text-stone-900 uppercase tracking-wider flex items-center gap-2">
                        <span className="text-base">⚙️</span> Backend Technology
                      </span>
                      <span className="text-xs font-bold text-stone-500">Server-Side</span>
                    </div>
                    {backend && backend.confidence > 0 ? (
                      <div className="flex-1 bg-stone-50 p-3 rounded-xl border border-stone-200 space-y-1.5">
                        <div className="flex items-start justify-between">
                          <div>
                            <span className="font-black text-stone-900 text-base block">{backend.language}</span>
                            {backend.framework && (
                              <span className="text-xs font-semibold text-stone-600">Framework: {backend.framework}</span>
                            )}
                          </div>
                          <span className={`px-2.5 py-0.5 rounded-md text-xs font-bold border ${getConfidenceBadge(backend.confidence)}`}>
                            {backend.confidence}%
                          </span>
                        </div>
                        <div className="pt-1">
                          <span className="text-xs text-stone-500 font-mono">Detection: {backend.status}</span>
                        </div>
                      </div>
                    ) : (
                      <div className="flex-1 flex items-center justify-center bg-stone-50 rounded-xl border border-dashed border-stone-200 py-6">
                        <span className="text-stone-500 italic text-xs">Not publicly detectable</span>
                      </div>
                    )}
                  </div>

                  {/* 7. Web Server & CDN */}
                  <div className="p-4 sm:p-5 rounded-2xl bg-white border border-stone-200 shadow-2xs space-y-3 flex flex-col hover:border-stone-300 transition">
                    <div className="flex items-center justify-between border-b border-stone-100 pb-2">
                      <span className="text-xs font-black text-stone-900 uppercase tracking-wider flex items-center gap-2">
                        <span className="text-base">🖥️</span> Web Server & CDN Layer
                      </span>
                      <span className="text-xs font-bold text-stone-500">Edge & HTTP</span>
                    </div>
                    <div className="flex-1 space-y-2">
                      {techStack.server ? (
                        <div className="flex items-center justify-between p-2.5 rounded-lg bg-stone-50 border border-stone-200">
                          <span className="font-bold text-stone-900 text-sm">{techStack.server.name} <span className="text-xs text-stone-500 font-normal">(Server)</span></span>
                          <span className="text-xs font-bold text-stone-700 bg-stone-200 px-2 py-0.5 rounded-md">{techStack.server.confidence}%</span>
                        </div>
                      ) : (
                        <div className="p-2.5 rounded-lg bg-stone-50 border border-dashed border-stone-200 text-center">
                          <span className="text-stone-500 italic text-xs">Server: Hidden / Unknown</span>
                        </div>
                      )}
                      {techStack.cdn ? (
                        <div className="flex items-center justify-between p-2.5 rounded-lg bg-purple-50/60 border border-purple-200">
                          <span className="font-bold text-purple-950 text-sm">{techStack.cdn.name} <span className="text-xs text-purple-700 font-normal">(CDN)</span></span>
                          <span className="text-xs font-bold text-purple-800 bg-purple-200 px-2 py-0.5 rounded-md">{techStack.cdn.confidence}%</span>
                        </div>
                      ) : (
                        <div className="p-2.5 rounded-lg bg-stone-50 border border-dashed border-stone-200 text-center">
                          <span className="text-stone-500 italic text-xs">CDN: Direct origin</span>
                        </div>
                      )}
                    </div>
                  </div>

                  {/* 8. Hosting Infrastructure */}
                  <div className="p-4 sm:p-5 rounded-2xl bg-white border border-stone-200 shadow-2xs space-y-3 flex flex-col hover:border-stone-300 transition">
                    <div className="flex items-center justify-between border-b border-stone-100 pb-2">
                      <span className="text-xs font-black text-stone-900 uppercase tracking-wider flex items-center gap-2">
                        <span className="text-base">🏢</span> Hosting Infrastructure
                      </span>
                      <span className="text-xs font-bold text-stone-500">Cloud Host</span>
                    </div>
                    {hosting && hosting.confidence > 0 ? (
                      <div className="flex-1 bg-stone-50 p-3 rounded-xl border border-stone-200 flex flex-col justify-between">
                        <div className="flex items-start justify-between">
                          <div>
                            <span className="font-black text-stone-900 text-base block">{hosting.name}</span>
                            <span className="text-xs text-stone-600 font-medium">{hosting.status || 'Verified Cloud Host'}</span>
                          </div>
                          <span className={`px-2.5 py-1 rounded-md text-xs font-black border ${getConfidenceBadge(hosting.confidence)}`}>
                            {hosting.confidence}%
                          </span>
                        </div>
                      </div>
                    ) : (
                      <div className="flex-1 flex items-center justify-center bg-stone-50 rounded-xl border border-dashed border-stone-200 py-6">
                        <span className="text-stone-500 italic text-xs">Protected / Hidden host</span>
                      </div>
                    )}
                  </div>
                </div>
              </div>
            )}

            {/* ==================== TAB 3: INFRASTRUCTURE & SSL ==================== */}
            {activeTab === 'infra' && (
              <div className="space-y-5">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
                  {/* DNS Records */}
                  <div className="p-5 sm:p-6 rounded-2xl bg-white border border-stone-200 shadow-2xs space-y-4">
                    <div className="flex items-center justify-between border-b border-stone-100 pb-3">
                      <span className="text-sm font-black text-stone-900 uppercase tracking-wider flex items-center gap-2">
                        <span className="text-blue-600 text-lg">🌐</span> DNS Configuration
                      </span>
                      <span className="text-xs font-mono font-bold text-stone-500">Domain Records</span>
                    </div>

                    <div className="space-y-3 font-mono text-xs">
                      <div>
                        <span className="text-xs text-stone-500 font-bold uppercase tracking-wider font-sans block mb-1">
                          Domain Name
                        </span>
                        <div className="p-2.5 rounded-xl bg-stone-50 border border-stone-200 font-semibold text-stone-800">
                          {dns?.domain || new URL(analysis.website_url).hostname}
                        </div>
                      </div>

                      <div>
                        <span className="text-xs text-stone-500 font-bold uppercase tracking-wider font-sans block mb-1">
                          Resolved IP Addresses (A Records)
                        </span>
                        <div className="p-2.5 rounded-xl bg-stone-50 border border-stone-200 font-semibold text-stone-800 space-y-1">
                          {dns?.a_records && dns.a_records.length > 0 ? (
                            dns.a_records.map((ip, i) => (
                              <div key={i} className="flex items-center justify-between">
                                <span>{ip}</span>
                                <span className="text-[10px] text-emerald-800 font-bold bg-emerald-100/80 px-2 py-0.5 rounded font-sans">IPv4</span>
                              </div>
                            ))
                          ) : (
                            <span className="text-stone-400 italic">No A-Records captured</span>
                          )}
                        </div>
                      </div>

                      <div>
                        <span className="text-xs text-stone-500 font-bold uppercase tracking-wider font-sans block mb-1">
                          Authoritative Nameservers
                        </span>
                        <div className="p-2.5 rounded-xl bg-stone-50 border border-stone-200 font-semibold text-stone-800 space-y-1">
                          {dns?.nameservers && dns.nameservers.length > 0 ? (
                            dns.nameservers.map((ns, i) => (
                              <div key={i} className="text-stone-700">
                                • {ns}
                              </div>
                            ))
                          ) : (
                            <span className="text-stone-400 italic">No Nameservers recorded</span>
                          )}
                        </div>
                      </div>
                    </div>
                  </div>

                  {/* SSL / TLS Certificate */}
                  <div className="p-5 sm:p-6 rounded-2xl bg-white border border-stone-200 shadow-2xs space-y-4">
                    <div className="flex items-center justify-between border-b border-stone-100 pb-3">
                      <span className="text-sm font-black text-stone-900 uppercase tracking-wider flex items-center gap-2">
                        <span className="text-emerald-700 text-lg">🔒</span> SSL / TLS Certificate
                      </span>
                      <span className={`px-2.5 py-0.5 rounded-full text-xs font-bold ${ssl?.enabled ? 'bg-emerald-50 text-emerald-800 border border-emerald-200' : 'bg-rose-50 text-rose-800 border border-rose-200'}`}>
                        {ssl?.enabled ? 'Valid & Encrypted' : 'Not Encrypted'}
                      </span>
                    </div>

                    <div className="space-y-3 font-mono text-xs">
                      <div>
                        <span className="text-xs text-stone-500 font-bold uppercase tracking-wider font-sans block mb-1">
                          Certificate Authority (Issuer)
                        </span>
                        <div className="p-2.5 rounded-xl bg-stone-50 border border-stone-200 font-semibold text-stone-800">
                          {ssl?.issuer || 'Let\'s Encrypt / Standard CA'}
                        </div>
                      </div>

                      <div>
                        <span className="text-xs text-stone-500 font-bold uppercase tracking-wider font-sans block mb-1">
                          Cipher & Protocol Version
                        </span>
                        <div className="p-2.5 rounded-xl bg-stone-50 border border-stone-200 font-semibold text-stone-800">
                          {ssl?.version || 'TLS 1.3'} {ssl?.cipher ? `(${ssl.cipher})` : ''}
                        </div>
                      </div>

                      {ssl?.subject && (
                        <div>
                          <span className="text-xs text-stone-500 font-bold uppercase tracking-wider font-sans block mb-1">
                            Certificate Subject
                          </span>
                          <div className="p-2.5 rounded-xl bg-stone-50 border border-stone-200 font-semibold text-stone-800">
                            {ssl.subject}
                          </div>
                        </div>
                      )}

                      {(ssl?.not_before || ssl?.not_after) && (
                        <div className="grid grid-cols-2 gap-2">
                          <div>
                            <span className="text-[10px] text-stone-500 font-bold uppercase tracking-wider font-sans block mb-1">
                              Valid From
                            </span>
                            <div className="p-2 rounded-xl bg-stone-50 border border-stone-200 text-stone-700 text-xs">
                              {ssl?.not_before ? new Date(ssl.not_before).toLocaleDateString() : 'Active'}
                            </div>
                          </div>
                          <div>
                            <span className="text-[10px] text-stone-500 font-bold uppercase tracking-wider font-sans block mb-1">
                              Valid Until
                            </span>
                            <div className="p-2 rounded-xl bg-stone-50 border border-stone-200 text-stone-700 text-xs">
                              {ssl?.not_after ? new Date(ssl.not_after).toLocaleDateString() : 'Current'}
                            </div>
                          </div>
                        </div>
                      )}
                    </div>
                  </div>
                </div>
              </div>
            )}

            {/* ==================== TAB 4: EVIDENCE LOG ==================== */}
            {activeTab === 'evidence' && (
              <div className="space-y-4">
                <div className="bg-white rounded-2xl p-5 sm:p-6 border border-stone-200 shadow-2xs space-y-4">
                  <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-stone-100 pb-3">
                    <div className="flex items-center gap-2">
                      <span className="text-xl">🔎</span>
                      <div>
                        <h3 className="text-sm font-black uppercase tracking-wider text-stone-900">
                          Signal & Evidence Inspector
                        </h3>
                        <p className="text-xs text-stone-500">
                          Raw technological fingerprints captured during automated crawl
                        </p>
                      </div>
                    </div>

                    <div className="relative">
                      <input
                        type="text"
                        value={evidenceSearch}
                        onChange={(e) => setEvidenceSearch(e.target.value)}
                        placeholder="Filter evidence..."
                        className="w-full sm:w-64 pl-8 pr-3 py-1.5 text-xs bg-stone-50 border border-stone-300 rounded-xl focus:ring-2 focus:ring-emerald-500/20 focus:border-emerald-600 outline-none text-stone-800"
                      />
                      <span className="absolute left-2.5 top-2 text-stone-400 text-xs">🔍</span>
                    </div>
                  </div>

                  <div className="space-y-2.5">
                    {filteredEvidence.map((ev, idx) => (
                      <div
                        key={idx}
                        className="p-3.5 rounded-xl bg-stone-50 border border-stone-200 flex flex-col sm:flex-row sm:items-start gap-3 hover:border-stone-300 hover:bg-stone-100/70 transition"
                      >
                        <div className="shrink-0 flex sm:flex-col items-start gap-1">
                          <span className="px-2.5 py-1 rounded-md bg-stone-200 text-stone-900 font-bold font-mono text-xs border border-stone-300">
                            {ev.technology}
                          </span>
                          {ev.category && (
                            <span className="text-[10px] text-stone-500 font-semibold uppercase tracking-wider font-mono">
                              {ev.category}
                            </span>
                          )}
                        </div>

                        <div className="flex-1 font-mono text-xs text-stone-800 bg-white p-2.5 rounded-lg border border-stone-200 break-words leading-relaxed">
                          {ev.evidence}
                        </div>

                        <div className="shrink-0 self-start sm:self-center">
                          <span className={`px-2.5 py-1 rounded-md text-xs font-bold border font-mono ${getConfidenceBadge(ev.confidence)}`}>
                            {ev.confidence}% Conf.
                          </span>
                        </div>
                      </div>
                    ))}

                    {filteredEvidence.length === 0 && (
                      <div className="p-8 text-center border border-dashed border-stone-300 rounded-2xl bg-stone-50">
                        <p className="text-stone-500 text-xs font-semibold">
                          {evidenceSearch ? 'No evidence matching your search filter.' : 'No detailed raw evidence signals available.'}
                        </p>
                      </div>
                    )}
                  </div>
                </div>
              </div>
            )}

            {/* ==================== TAB 5: PAGE META & RESOURCES ==================== */}
            {activeTab === 'meta' && (
              <div className="space-y-5">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
                  {/* Meta Information */}
                  <div className="p-5 sm:p-6 rounded-2xl bg-white border border-stone-200 shadow-2xs space-y-4">
                    <div className="border-b border-stone-100 pb-3">
                      <span className="text-sm font-black text-stone-900 uppercase tracking-wider flex items-center gap-2">
                        <span>📄</span> Document Head Metadata
                      </span>
                    </div>

                    <div className="space-y-3 text-xs">
                      <div>
                        <span className="text-[11px] text-stone-500 font-bold uppercase tracking-wider block mb-1">
                          Document Title (&lt;title&gt;)
                        </span>
                        <div className="p-2.5 rounded-xl bg-stone-50 border border-stone-200 font-bold text-stone-900">
                          {metadata.title || analysis.page_title || 'N/A'}
                        </div>
                      </div>

                      <div>
                        <span className="text-[11px] text-stone-500 font-bold uppercase tracking-wider block mb-1">
                          Meta Description
                        </span>
                        <div className="p-2.5 rounded-xl bg-stone-50 border border-stone-200 text-stone-700 leading-relaxed">
                          {metadata.description || 'No description provided'}
                        </div>
                      </div>

                      {metadata.canonical_url && (
                        <div>
                          <span className="text-[11px] text-stone-500 font-bold uppercase tracking-wider block mb-1">
                            Canonical URL
                          </span>
                          <div className="p-2.5 rounded-xl bg-stone-50 border border-stone-200 font-mono text-stone-700 truncate">
                            {metadata.canonical_url}
                          </div>
                        </div>
                      )}

                      {metadata.keywords && (
                        <div>
                          <span className="text-[11px] text-stone-500 font-bold uppercase tracking-wider block mb-1">
                            Meta Keywords
                          </span>
                          <div className="p-2.5 rounded-xl bg-stone-50 border border-stone-200 text-stone-700">
                            {metadata.keywords}
                          </div>
                        </div>
                      )}
                    </div>
                  </div>

                  {/* Resource Element Statistics */}
                  <div className="p-5 sm:p-6 rounded-2xl bg-white border border-stone-200 shadow-2xs space-y-4">
                    <div className="border-b border-stone-100 pb-3">
                      <span className="text-sm font-black text-stone-900 uppercase tracking-wider flex items-center gap-2">
                        <span>📊</span> DOM Assets & Element Breakdown
                      </span>
                    </div>

                    <div className="grid grid-cols-2 gap-3.5">
                      <div className="p-3.5 rounded-xl bg-stone-50 border border-stone-200 text-center">
                        <span className="text-2xl font-black text-stone-900 block">
                          {performance.script_count || metadata.element_counts?.script_tags || 0}
                        </span>
                        <span className="text-xs font-semibold text-stone-500 mt-1 block">
                          JavaScript Scripts
                        </span>
                      </div>

                      <div className="p-3.5 rounded-xl bg-stone-50 border border-stone-200 text-center">
                        <span className="text-2xl font-black text-stone-900 block">
                          {performance.stylesheet_count || metadata.element_counts?.stylesheet_tags || 0}
                        </span>
                        <span className="text-xs font-semibold text-stone-500 mt-1 block">
                          CSS Stylesheets
                        </span>
                      </div>

                      <div className="p-3.5 rounded-xl bg-stone-50 border border-stone-200 text-center">
                        <span className="text-2xl font-black text-stone-900 block">
                          {performance.image_count || metadata.element_counts?.images || 0}
                        </span>
                        <span className="text-xs font-semibold text-stone-500 mt-1 block">
                          Images Loaded
                        </span>
                      </div>

                      <div className="p-3.5 rounded-xl bg-stone-50 border border-stone-200 text-center">
                        <span className="text-2xl font-black text-stone-900 block">
                          {metadata.element_counts?.iframes || 0}
                        </span>
                        <span className="text-xs font-semibold text-stone-500 mt-1 block">
                          Embedded IFrames
                        </span>
                      </div>
                    </div>

                    <div className="p-3 rounded-xl bg-emerald-50/70 border border-emerald-200">
                      <div className="flex items-center justify-between text-xs">
                        <span className="font-bold text-emerald-900">HTTP Response Time:</span>
                        <span className="font-mono font-black text-emerald-800">
                          {performance.http_response_time_ms ? `${performance.http_response_time_ms} ms` : 'N/A'}
                        </span>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            )}

          </div>
        </main>

        {/* ===================== OFF-WHITE STICKY FOOTER ===================== */}
        <footer className="px-5 sm:px-7 py-3.5 bg-[#fafaf9] border-t border-stone-200 flex flex-col sm:flex-row sm:justify-between sm:items-center gap-3 shrink-0 shadow-xs z-30">
          <div className="flex items-center gap-3 text-xs text-stone-600 font-medium">
            <span>Overall Confidence: <strong className="text-stone-900 font-mono font-bold">{analysis.overall_confidence || 90}%</strong></span>
            <span>•</span>
            <span>Detected Technologies: <strong className="text-stone-900 font-mono font-bold">{totalDetectedTech}</strong></span>
          </div>

          <div className="flex items-center gap-2.5">
            <a
              href={analysis.website_url}
              target="_blank"
              rel="noopener noreferrer"
              className="px-4 py-2 bg-stone-100 hover:bg-stone-200 text-stone-800 rounded-xl text-xs font-bold transition flex items-center gap-1.5 border border-stone-200"
            >
              <span>Visit Target Website</span>
              <span>↗</span>
            </a>

            <button
              onClick={onClose}
              className="px-6 py-2 bg-stone-900 hover:bg-stone-800 text-white rounded-xl text-xs font-bold hover:shadow-md active:scale-95 transition-all shadow-2xs"
            >
              Close Analysis
            </button>
          </div>
        </footer>
      </div>
    </div>
  );

  return createPortal(modalContent, document.body);
}

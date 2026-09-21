'use client';

import { useState, useEffect, useCallback, useMemo } from 'react';
import { PortfolioWebsite, AnalysisStats, WebsiteAnalysis } from '@/lib/types';
import {
  fetchAnalysisStats,
  triggerAnalysis,
  triggerBulkAnalysis,
  stopBulkAnalysis,
  fetchAnalysis,
  fetchAnalysesList,
  API_BASE_URL,
} from '@/lib/api';
import AnalysisModal from './AnalysisModal';
import Pagination from '../dashboard/Pagination';

interface AnalysisTabProps {
  portfolios: PortfolioWebsite[];
  totalItems: number;
  totalPages: number;
  currentPage: number;
  pageSize: number;
  onPageChange: (page: number) => void;
  onPageSizeChange: (size: number) => void;
  onRefreshPortfolios: () => void;
}

export default function AnalysisTab({
  portfolios,
  totalItems,
  totalPages,
  currentPage,
  pageSize,
  onPageChange,
  onPageSizeChange,
  onRefreshPortfolios,
}: AnalysisTabProps) {
  const [stats, setStats] = useState<AnalysisStats | null>(null);
  const [selectedAnalysis, setSelectedAnalysis] = useState<WebsiteAnalysis | null>(null);
  const [isModalOpen, setIsModalOpen] = useState<boolean>(false);
  const [analyzingIds, setAnalyzingIds] = useState<Record<number, boolean>>({});
  const [isBulkRunning, setIsBulkRunning] = useState<boolean>(false);
  const [isStopping, setIsStopping] = useState<boolean>(false);
  const [analysesMap, setAnalysesMap] = useState<Record<number, WebsiteAnalysis>>({});

  // Real-Time Filter States
  const [searchQuery, setSearchQuery] = useState<string>('');
  const [categoryFilter, setCategoryFilter] = useState<string>('all');
  const [techFilter, setTechFilter] = useState<string>('all');
  const [statusFilter, setStatusFilter] = useState<string>('all');

  const loadAnalysisData = useCallback(async () => {
    const fetchedStats = await fetchAnalysisStats();
    setStats(fetchedStats);

    // Persist bulk running state based on pending items in backend
    if (fetchedStats && fetchedStats.pending_count > 0) {
      setIsBulkRunning(true);
    } else {
      setIsBulkRunning(false);
    }

    const analyses = await fetchAnalysesList(0, 200);
    const map: Record<number, WebsiteAnalysis> = {};
    analyses.forEach((a: WebsiteAnalysis) => {
      map[a.portfolio_id] = a;
    });
    setAnalysesMap(map);
  }, []);

  useEffect(() => {
    loadAnalysisData();
  }, [loadAnalysisData]);

  // Poll progress when bulk analysis is running
  useEffect(() => {
    let interval: NodeJS.Timeout;
    if (isBulkRunning) {
      interval = setInterval(() => {
        loadAnalysisData();
      }, 3000);
    }
    return () => clearInterval(interval);
  }, [isBulkRunning, loadAnalysisData]);

  // Extract unique categories for dropdown filter options
  const uniqueCategories = useMemo(() => {
    const cats = new Set<string>();
    portfolios.forEach((p) => {
      if (p.category) cats.add(p.category);
    });
    return Array.from(cats).sort();
  }, [portfolios]);

  // Real-Time Filtering Logic
  const filteredPortfolios = useMemo(() => {
    return portfolios.filter((p) => {
      const analysisRecord = analysesMap[p.id];
      const primaryName = (
        analysisRecord?.primary_technology_name ||
        analysisRecord?.primary_technology?.name ||
        (analysisRecord?.status === 'completed' ? 'HTML / CSS / JavaScript' : '')
      ).toLowerCase();

      // 1. Text Search Filter (Business name, URL, Category, or Technology)
      if (searchQuery.trim()) {
        const q = searchQuery.toLowerCase().trim();
        const nameMatch = p.business_name.toLowerCase().includes(q);
        const urlMatch = (p.website_url || '').toLowerCase().includes(q);
        const catMatch = (p.category || '').toLowerCase().includes(q);
        const techMatch = primaryName.includes(q);
        if (!nameMatch && !urlMatch && !catMatch && !techMatch) return false;
      }

      // 2. Category Filter
      if (categoryFilter !== 'all') {
        if (p.category !== categoryFilter) return false;
      }

      // 3. Primary Technology Filter
      if (techFilter !== 'all') {
        if (techFilter === 'Not Analyzed') {
          if (analysisRecord?.status === 'completed') return false;
        } else {
          const expectedTech = techFilter.toLowerCase();
          if (!primaryName.includes(expectedTech)) return false;
        }
      }

      // 4. Analysis Status Filter
      if (statusFilter !== 'all') {
        const isCompleted = analysisRecord?.status === 'completed';
        const isFailed = analysisRecord?.status === 'failed';
        const isAnalyzing = analyzingIds[p.id] || analysisRecord?.status === 'analyzing';

        if (statusFilter === 'completed' && !isCompleted) return false;
        if (statusFilter === 'pending' && (isCompleted || isFailed || isAnalyzing)) return false;
        if (statusFilter === 'analyzing' && !isAnalyzing) return false;
        if (statusFilter === 'failed' && !isFailed) return false;
      }

      return true;
    });
  }, [portfolios, analysesMap, analyzingIds, searchQuery, categoryFilter, techFilter, statusFilter]);

  const hasActiveFilters = searchQuery !== '' || categoryFilter !== 'all' || techFilter !== 'all' || statusFilter !== 'all';

  const handleClearFilters = () => {
    setSearchQuery('');
    setCategoryFilter('all');
    setTechFilter('all');
    setStatusFilter('all');
  };

  // Handle single website analysis trigger
  const handleSingleAnalyze = async (portfolioId: number) => {
    setAnalyzingIds((prev) => ({ ...prev, [portfolioId]: true }));
    const res = await triggerAnalysis(portfolioId);
    if (res.success) {
      setTimeout(() => {
        loadAnalysisData();
        setAnalyzingIds((prev) => ({ ...prev, [portfolioId]: false }));
      }, 3000);
    } else {
      alert(res.message);
      setAnalyzingIds((prev) => ({ ...prev, [portfolioId]: false }));
    }
  };

  // Handle bulk analysis trigger
  const handleBulkAnalyze = async () => {
    if (confirm('Start bulk website analysis for all portfolio items?')) {
      setIsBulkRunning(true);
      const res = await triggerBulkAnalysis();
      if (!res.success) {
        alert(res.message);
        setIsBulkRunning(false);
      } else {
        loadAnalysisData();
      }
    }
  };

  // Handle stopping analysis
  const handleStopAnalysis = async () => {
    setIsStopping(true);
    const res = await stopBulkAnalysis();
    alert(res.message || 'Analysis stopped.');
    await loadAnalysisData();
    setIsBulkRunning(false);
    setIsStopping(false);
  };

  // Handle view analysis detail modal
  const handleViewAnalysis = async (portfolioId: number) => {
    const data = await fetchAnalysis(portfolioId);
    if (data) {
      setSelectedAnalysis(data);
      setIsModalOpen(true);
    } else {
      alert('Analysis record not found.');
    }
  };

  return (
    <div className="space-y-6 w-full animate-fadeIn">
      {/* Top Overview Banner */}
      <div className="bg-white border border-stone-200/90 rounded-2xl p-6 shadow-sm flex flex-col md:flex-row items-start md:items-center justify-between gap-6">
        <div>
          <div className="flex items-center gap-2.5">
            <h2 className="text-xl font-extrabold text-stone-900 tracking-tight">
              Website Technology Analysis Engine
            </h2>

          </div>
          <p className="text-xs text-stone-500 mt-1 max-w-2xl leading-relaxed">
            Identifies Primary Website Platform (WordPress, Next.js, React, Vue, HTML/CSS/JS) with evidence verification. Places libraries such as jQuery & Bootstrap in dedicated secondary categories.
          </p>
        </div>

        <div className="flex items-center gap-3">
          <a
            href={`${API_BASE_URL}/api/export?format=excel`}
            className="px-4 py-2.5 rounded-xl font-bold text-xs border border-emerald-300 bg-emerald-50 text-emerald-800 hover:bg-emerald-100 hover:border-emerald-400 transition-all flex items-center gap-1.5 shadow-sm"
          >
            <span>📊</span> Export Excel
          </a>
          <a
            href={`${API_BASE_URL}/api/export?format=json`}
            className="px-4 py-2.5 rounded-xl font-bold text-xs border border-stone-300 bg-white text-stone-700 hover:bg-stone-50 hover:border-stone-400 transition-all flex items-center gap-1.5 shadow-sm"
          >
            <span>📄</span> Export JSON
          </a>

          {isBulkRunning ? (
            <>
              {/* Active Analyzing state button layout */}
              <button
                disabled
                className="px-5 py-2.5 rounded-xl font-extrabold text-xs shadow-md bg-stone-900 text-white flex flex-col items-center justify-center gap-0.5 border border-stone-700 min-w-[210px] cursor-wait"
              >
                <div className="flex items-center gap-1.5 text-xs font-extrabold tracking-tight">
                  <span className="animate-bounce">⚡</span>
                  <span>Analyze All Portfolios</span>
                </div>
                <div className="flex items-center gap-1 text-[11px] font-bold text-amber-400 tracking-wider">
                  <span className="inline-block w-1.5 h-1.5 rounded-full bg-amber-400 animate-ping"></span>
                  <span>Analyzing....</span>
                </div>
              </button>

              {/* Stop button right beside it */}
              <button
                onClick={handleStopAnalysis}
                disabled={isStopping}
                className="px-4 py-3 rounded-xl font-extrabold text-xs shadow-md transition-all flex items-center gap-2 bg-rose-600 hover:bg-rose-700 text-white active:scale-95 border border-rose-500 hover:shadow-rose-200"
              >
                <span className="text-sm">🛑</span>
                <span>{isStopping ? 'Stopping...' : 'Stop'}</span>
              </button>
            </>
          ) : (
            <button
              onClick={handleBulkAnalyze}
              className="px-5 py-3 rounded-xl font-extrabold text-xs shadow-md transition-all flex items-center gap-2 bg-stone-900 text-white hover:bg-stone-800 hover:shadow-lg active:scale-98"
            >
              <span>⚡</span>
              <span>Analyze All Portfolios</span>
            </button>
          )}
        </div>
      </div>

      {/* Statistics Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5">
        <div className="bg-white border border-stone-200/90 rounded-2xl p-5 shadow-xs transition hover:shadow-md">
          <span className="text-[10px] uppercase font-bold font-mono text-stone-400 block tracking-wider">Total Websites</span>
          <span className="text-2xl font-black text-stone-900 mt-1 block tracking-tight">{stats?.total_websites || totalItems}</span>
        </div>

        <div className="bg-emerald-50/40 border border-emerald-200/90 rounded-2xl p-5 shadow-xs transition hover:shadow-md">
          <span className="text-[10px] uppercase font-bold font-mono text-emerald-700 block tracking-wider">Analyzed Websites</span>
          <span className="text-2xl font-black text-emerald-900 mt-1 block tracking-tight">{stats?.analyzed_count || 0}</span>
        </div>

        <div className="bg-amber-50/40 border border-amber-200/90 rounded-2xl p-5 shadow-xs transition hover:shadow-md">
          <span className="text-[10px] uppercase font-bold font-mono text-amber-700 block tracking-wider">Pending Analysis</span>
          <span className="text-2xl font-black text-amber-900 mt-1 block tracking-tight">{stats?.pending_count || 0}</span>
        </div>

        <div className="bg-rose-50/40 border border-rose-200/90 rounded-2xl p-5 shadow-xs transition hover:shadow-md">
          <span className="text-[10px] uppercase font-bold font-mono text-rose-700 block tracking-wider">Failed Analysis</span>
          <span className="text-2xl font-black text-rose-900 mt-1 block tracking-tight">{stats?.failed_count || 0}</span>
        </div>
      </div>

      {/* Top Technologies & CMS Distribution Summary */}
      {stats && (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div className="bg-white border border-stone-200/90 rounded-2xl p-6 shadow-xs space-y-3">
            <h3 className="text-xs font-black uppercase tracking-wider text-stone-500 font-mono">Top Primary Technologies</h3>
            <div className="space-y-2">
              {(stats.top_technologies || []).map((t, idx) => (
                <div key={idx} className="flex items-center justify-between p-2.5 rounded-xl bg-stone-50/80 border border-stone-200/80 text-xs">
                  <span className="font-extrabold text-stone-800">{t.name}</span>
                  <span className="font-mono font-bold text-emerald-700">{t.count} site(s)</span>
                </div>
              ))}
              {(!stats.top_technologies || stats.top_technologies.length === 0) && (
                <p className="text-xs text-stone-400 italic py-2">No technology analysis records yet. Click "Analyze All Portfolios" to start.</p>
              )}
            </div>
          </div>

          <div className="bg-white border border-stone-200/90 rounded-2xl p-6 shadow-xs space-y-3">
            <h3 className="text-xs font-black uppercase tracking-wider text-stone-500 font-mono">CMS & Platform Distribution</h3>
            <div className="space-y-2">
              {Object.entries(stats.cms_distribution || {}).map(([cmsName, count], idx) => (
                <div key={idx} className="flex items-center justify-between p-2.5 rounded-xl bg-stone-50/80 border border-stone-200/80 text-xs">
                  <span className="font-extrabold text-stone-800">{cmsName}</span>
                  <span className="font-mono font-bold text-stone-900">{count} site(s)</span>
                </div>
              ))}
              {Object.keys(stats.cms_distribution || {}).length === 0 && (
                <p className="text-xs text-stone-400 italic py-2">No CMS platforms detected yet.</p>
              )}
            </div>
          </div>
        </div>
      )}

      {/* REAL-TIME SEARCH & FILTERS MODULE */}
      <div className="bg-white border border-stone-200/90 rounded-2xl p-5 shadow-xs space-y-4">
        <div className="flex items-center justify-between">
          <h3 className="text-xs font-black uppercase tracking-wider text-stone-700 flex items-center gap-2 font-mono">
            <span>🔎 Real-Time Search & Technology Filters</span>
            {hasActiveFilters && (
              <span className="px-2.5 py-0.5 rounded-full bg-emerald-100 text-emerald-800 text-[10px] font-bold font-mono border border-emerald-200">
                {filteredPortfolios.length} Match(es)
              </span>
            )}
          </h3>

          {hasActiveFilters && (
            <button
              onClick={handleClearFilters}
              className="text-xs font-bold text-rose-600 hover:text-rose-800 flex items-center gap-1 bg-rose-50/80 px-3 py-1 rounded-xl border border-rose-200/80 transition"
            >
              <span>✕</span> Clear Filters
            </button>
          )}
        </div>

        {/* Filter Controls Row */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3 text-xs">
          
          {/* Search Box */}
          <div className="relative">
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Search business, URL, tech..."
              className="w-full pl-9 pr-3 py-2 bg-stone-50 border border-stone-300 rounded-xl font-medium focus:ring-2 focus:ring-emerald-500/20 focus:border-emerald-600 outline-none transition"
            />
            <span className="absolute left-3 top-2.5 text-stone-400 font-bold">🔍</span>
          </div>

          {/* Category Dropdown */}
          <div>
            <select
              value={categoryFilter}
              onChange={(e) => setCategoryFilter(e.target.value)}
              className="w-full px-3 py-2 bg-stone-50 border border-stone-300 rounded-xl font-medium focus:ring-2 focus:ring-emerald-500/20 focus:border-emerald-600 outline-none transition text-stone-700"
            >
              <option value="all">📁 All Categories ({uniqueCategories.length})</option>
              {uniqueCategories.map((cat, i) => (
                <option key={i} value={cat}>{cat}</option>
              ))}
            </select>
          </div>

          {/* Primary Technology Dropdown */}
          <div>
            <select
              value={techFilter}
              onChange={(e) => setTechFilter(e.target.value)}
              className="w-full px-3 py-2 bg-stone-50 border border-stone-300 rounded-xl font-medium focus:ring-2 focus:ring-emerald-500/20 focus:border-emerald-600 outline-none transition text-stone-700"
            >
              <option value="all">⚡ All Primary Technologies</option>
              <option value="WordPress">WordPress</option>
              <option value="Webflow">Webflow</option>
              <option value="Next.js">Next.js</option>
              <option value="React">React</option>
              <option value="Vue">Vue.js</option>
              <option value="HTML / CSS / JavaScript">HTML / CSS / JavaScript</option>
              <option value="Shopify">Shopify</option>
              <option value="Not Analyzed">Pending / Not Analyzed</option>
            </select>
          </div>

          {/* Analysis Status Dropdown */}
          <div>
            <select
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value)}
              className="w-full px-3 py-2 bg-stone-50 border border-stone-300 rounded-xl font-medium focus:ring-2 focus:ring-emerald-500/20 focus:border-emerald-600 outline-none transition text-stone-700"
            >
              <option value="all">📊 All Analysis Statuses</option>
              <option value="completed">✓ Completed</option>
              <option value="pending">⏳ Pending / Not Analyzed</option>
              <option value="analyzing">⚡ Currently Analyzing</option>
              <option value="failed">✕ Failed</option>
            </select>
          </div>

        </div>
      </div>

      {/* Portfolio Website Analysis Table with Server-Side Pagination & Real-time Filter Results */}
      <div className="bg-white border border-stone-200 rounded-2xl shadow-sm overflow-hidden space-y-4">
        <div className="px-6 py-4 bg-stone-50 border-b border-stone-200 flex items-center justify-between">
          <div>
            <h3 className="text-xs font-black uppercase tracking-wider text-stone-700">
              Portfolio Websites Technology Analysis ({hasActiveFilters ? `${filteredPortfolios.length} of ${portfolios.length} Filtered` : `${totalItems} Total`})
            </h3>
            <p className="text-[11px] text-stone-500 mt-0.5">
              Showing page {currentPage} of {totalPages} ({pageSize} websites per page)
            </p>
          </div>

          <button
            onClick={() => {
              onRefreshPortfolios();
              loadAnalysisData();
            }}
            className="text-xs font-bold text-stone-600 hover:text-stone-900 flex items-center gap-1 bg-stone-200/60 px-3 py-1.5 rounded-lg border border-stone-300/80 transition"
          >
            <span>↻</span> Refresh List
          </button>
        </div>

        <div className="overflow-x-auto px-2">
          <table className="w-full text-left text-xs text-stone-700">
            <thead className="bg-stone-100/70 border-b border-stone-200 text-[10px] uppercase font-bold text-stone-500">
              <tr>
                <th className="py-3 px-4">#</th>
                <th className="py-3 px-4">Business Name</th>
                <th className="py-3 px-4">Category</th>
                <th className="py-3 px-4">Primary Technology</th>
                <th className="py-3 px-4">Status</th>
                <th className="py-3 px-4">Confidence</th>
                <th className="py-3 px-4 text-right">Action</th>
              </tr>
            </thead>

            <tbody className="divide-y divide-stone-200 font-medium">
              {filteredPortfolios.map((p, idx) => {
                const analysisRecord = analysesMap[p.id];
                const isAnalyzing = analyzingIds[p.id] || analysisRecord?.status === 'analyzing';
                const isCompleted = analysisRecord?.status === 'completed';
                const isFailed = analysisRecord?.status === 'failed';
                const primaryName = analysisRecord?.primary_technology_name || analysisRecord?.primary_technology?.name || (isCompleted ? 'HTML / CSS / JavaScript' : 'Not Analyzed');

                return (
                  <tr key={p.id} className="hover:bg-stone-50/80 transition">
                    <td className="py-3.5 px-4 font-mono text-stone-400 text-[11px]">
                      {(currentPage - 1) * pageSize + idx + 1}
                    </td>

                    <td className="py-3.5 px-4 font-bold text-stone-900">{p.business_name}</td>

                    <td className="py-3.5 px-4">
                      <span className="px-2 py-0.5 rounded-md bg-stone-100 text-stone-700 border border-stone-200 text-[10px] font-semibold">
                        {p.category}
                      </span>
                    </td>

                    <td className="py-3.5 px-4">
                      {isCompleted ? (
                        <span className="font-bold text-stone-900 flex items-center gap-1.5">
                          <span className="w-2 h-2 rounded-full bg-emerald-500" />
                          <span>{primaryName}</span>
                        </span>
                      ) : (
                        <span className="text-stone-400 italic text-[11px]">Pending Analysis</span>
                      )}
                    </td>

                    <td className="py-3.5 px-4">
                      {isAnalyzing ? (
                        <span className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full bg-amber-50 text-amber-800 border border-amber-300 font-bold text-[10px]">
                          <span className="w-1.5 h-1.5 rounded-full bg-amber-500 animate-ping" />
                          Analyzing...
                        </span>
                      ) : isCompleted ? (
                        <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full bg-emerald-50 text-emerald-800 border border-emerald-300 font-bold text-[10px]">
                          ✓ Completed
                        </span>
                      ) : isFailed ? (
                        <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full bg-rose-50 text-rose-800 border border-rose-300 font-bold text-[10px]">
                          ✕ Failed
                        </span>
                      ) : (
                        <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full bg-stone-100 text-stone-600 border border-stone-300 font-bold text-[10px]">
                          Not Analyzed
                        </span>
                      )}
                    </td>

                    <td className="py-3.5 px-4 font-mono font-bold">
                      {isCompleted ? (
                        <span className="text-emerald-700">{analysisRecord.overall_confidence || 90}%</span>
                      ) : (
                        <span className="text-stone-400">-</span>
                      )}
                    </td>

                    <td className="py-3.5 px-4 text-right">
                      {isCompleted ? (
                        <button
                          onClick={() => handleViewAnalysis(p.id)}
                          className="px-3 py-1.5 rounded-lg bg-stone-900 text-white font-bold text-[11px] hover:bg-stone-800 shadow-2xs transition"
                        >
                          View Analysis ↗
                        </button>
                      ) : (
                        <button
                          onClick={() => handleSingleAnalyze(p.id)}
                          disabled={isAnalyzing || !p.website_url}
                          className={`px-3 py-1.5 rounded-lg text-[11px] font-bold transition shadow-2xs ${
                            isAnalyzing || !p.website_url
                              ? 'bg-stone-200 text-stone-500 cursor-not-allowed'
                              : 'bg-emerald-600 text-white hover:bg-emerald-700'
                          }`}
                        >
                          {isAnalyzing ? 'Analyzing...' : 'Analyze Website ⚡'}
                        </button>
                      )}
                    </td>
                  </tr>
                );
              })}

              {filteredPortfolios.length === 0 && (
                <tr>
                  <td colSpan={7} className="py-8 text-center text-stone-400">
                    <p className="text-sm font-semibold">No portfolio websites match your selected search & filter criteria.</p>
                    <button
                      onClick={handleClearFilters}
                      className="mt-2 text-xs text-emerald-600 font-bold hover:underline"
                    >
                      Clear search filters
                    </button>
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>

        {/* Pagination Controls */}
        <div className="p-4 border-t border-stone-200">
          <Pagination
            currentPage={currentPage}
            totalPages={totalPages}
            totalItems={hasActiveFilters ? filteredPortfolios.length : totalItems}
            pageSize={pageSize}
            onPageChange={onPageChange}
            onPageSizeChange={onPageSizeChange}
          />
        </div>
      </div>

      {/* Analysis Detail Modal */}
      <AnalysisModal
        analysis={selectedAnalysis}
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
      />
    </div>
  );
}

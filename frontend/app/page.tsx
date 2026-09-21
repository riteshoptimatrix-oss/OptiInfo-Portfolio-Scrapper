'use client';

import { useState, useEffect, useCallback, useRef } from 'react';
import Navbar from '@/components/layout/Navbar';
import StatsCards from '@/components/dashboard/StatsCards';
import SearchBar from '@/components/dashboard/SearchBar';
import CategoryFilter from '@/components/dashboard/CategoryFilter';
import PortfolioTable from '@/components/dashboard/PortfolioTable';
import Pagination from '@/components/dashboard/Pagination';
import ScrapeProgress from '@/components/dashboard/ScrapeProgress';
import EmptyState from '@/components/dashboard/EmptyState';
import LoadingState from '@/components/dashboard/LoadingState';
import ErrorState from '@/components/dashboard/ErrorState';
import AnalysisTab from '@/components/analysis/AnalysisTab';
import { HealthStatus, PortfolioWebsite, ScrapeStatus, Stats } from '@/lib/types';
import {
  fetchHealth,
  fetchPortfolios,
  fetchStats,
  fetchScrapeStatus,
  startScraping,
  deletePortfolioItem,
} from '@/lib/api';

export default function DashboardPage() {
  const [activeTab, setActiveTab] = useState<'dashboard' | 'scraped-data' | 'analysis'>('dashboard');
  const [health, setHealth] = useState<HealthStatus | null>(null);
  const [stats, setStats] = useState<Stats | null>(null);

  // Server-side State
  const [portfolios, setPortfolios] = useState<PortfolioWebsite[]>([]);
  const [totalItems, setTotalItems] = useState<number>(0);
  const [totalPages, setTotalPages] = useState<number>(1);
  const [scrapeStatus, setScrapeStatus] = useState<ScrapeStatus | null>(null);

  // Filter, Search, Sorting, and Pagination State
  const [searchQuery, setSearchQuery] = useState<string>('');
  const [selectedCategory, setSelectedCategory] = useState<string>('All');
  const [currentPage, setCurrentPage] = useState<number>(1);
  const [pageSize, setPageSize] = useState<number>(25);
  const [sortBy, setSortBy] = useState<string>('id');
  const [sortOrder, setSortOrder] = useState<'asc' | 'desc'>('asc');
  const [viewMode, setViewMode] = useState<'table' | 'grid'>('table');

  // UI States
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [isBannerDismissed, setIsBannerDismissed] = useState<boolean>(false);

  // Polling Refs
  const pollIntervalRef = useRef<NodeJS.Timeout | null>(null);
  const consecutiveErrorCount = useRef<number>(0);

  // Initialize filters from URL search parameters on mount
  useEffect(() => {
    if (typeof window !== 'undefined') {
      const urlParams = new URLSearchParams(window.location.search);
      const urlTab = urlParams.get('tab');
      const urlSearch = urlParams.get('search');
      const urlCategory = urlParams.get('category');
      const urlPage = urlParams.get('page');
      const urlSortBy = urlParams.get('sort_by');
      const urlSortOrder = urlParams.get('sort_order');

      if (urlTab === 'scraped-data' || urlTab === 'analysis' || urlTab === 'dashboard') {
        setActiveTab(urlTab);
      }
      if (urlSearch) setSearchQuery(urlSearch);
      if (urlCategory) setSelectedCategory(urlCategory);
      if (urlPage && !isNaN(Number(urlPage))) setCurrentPage(Number(urlPage));
      if (urlSortBy) setSortBy(urlSortBy);
      if (urlSortOrder === 'asc' || urlSortOrder === 'desc') setSortOrder(urlSortOrder);
    }
  }, []);

  // Synchronize state with browser URL search query
  useEffect(() => {
    if (typeof window !== 'undefined') {
      const urlParams = new URLSearchParams();
      if (activeTab !== 'dashboard') urlParams.set('tab', activeTab);
      if (searchQuery) urlParams.set('search', searchQuery);
      if (selectedCategory && selectedCategory !== 'All') urlParams.set('category', selectedCategory);
      if (currentPage > 1) urlParams.set('page', currentPage.toString());
      if (sortBy !== 'id') urlParams.set('sort_by', sortBy);
      if (sortOrder !== 'asc') urlParams.set('sort_order', sortOrder);

      const newUrl = urlParams.toString()
        ? `${window.location.pathname}?${urlParams.toString()}`
        : window.location.pathname;

      window.history.replaceState(null, '', newUrl);
    }
  }, [activeTab, searchQuery, selectedCategory, currentPage, sortBy, sortOrder]);

  // Load Health Status
  const loadHealth = useCallback(async () => {
    const status = await fetchHealth();
    setHealth(status);
  }, []);

  // Load Paginated Portfolios & Stats from Backend
  const loadData = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    try {
      const [paginatedData, fetchedStats, currentScrapeStatus] = await Promise.all([
        fetchPortfolios(searchQuery, selectedCategory, currentPage, pageSize, sortBy, sortOrder),
        fetchStats(),
        fetchScrapeStatus(),
      ]);

      setPortfolios(paginatedData.items);
      setTotalItems(paginatedData.total);
      setTotalPages(paginatedData.pages);
      setStats(fetchedStats);
      setScrapeStatus(currentScrapeStatus);
    } catch (err) {
      setError('Failed to connect to FastAPI backend API.');
    } finally {
      setIsLoading(false);
    }
  }, [searchQuery, selectedCategory, currentPage, pageSize, sortBy, sortOrder]);

  // Handle Start Scrape Action
  const handleStartScrape = async () => {
    setIsBannerDismissed(false);
    const res = await startScraping();
    if (res.success) {
      setScrapeStatus({
        status: 'running',
        total: 0,
        processed: 0,
        successful: 0,
        failed: 0,
        progress: 0,
        logs: [],
        error: null,
      });
      setActiveTab('dashboard');
    } else {
      alert(res.message);
    }
  };

  // Dismiss Scrape Progress Banner
  const handleDismissProgress = () => {
    setIsBannerDismissed(true);
    setScrapeStatus((prev) => (prev ? { ...prev, status: 'idle' } : null));
  };

  // Delete Portfolio Record
  const handleDelete = async (id: number) => {
    if (confirm('Are you sure you want to delete this portfolio record?')) {
      const success = await deletePortfolioItem(id);
      if (success) {
        loadData();
      }
    }
  };

  // Reset page to 1 whenever search query or category changes
  const handleSearchChange = (query: string) => {
    setSearchQuery(query);
    setCurrentPage(1);
  };

  const handleCategorySelect = (category: string) => {
    setSelectedCategory(category);
    setCurrentPage(1);
  };

  // Real-time Non-blocking Polling for Scraper Progress
  useEffect(() => {
    if (scrapeStatus?.status === 'running') {
      setIsBannerDismissed(false);
      pollIntervalRef.current = setInterval(async () => {
        try {
          const status = await fetchScrapeStatus();
          setScrapeStatus(status);
          consecutiveErrorCount.current = 0;

          if (status.status === 'completed' || status.status === 'failed') {
            if (pollIntervalRef.current) clearInterval(pollIntervalRef.current);
            loadData();
          }
        } catch (err) {
          consecutiveErrorCount.current += 1;
          if (consecutiveErrorCount.current >= 5) {
            if (pollIntervalRef.current) clearInterval(pollIntervalRef.current);
            setScrapeStatus((prev) =>
              prev ? { ...prev, status: 'failed', error: 'Backend status polling failed' } : null
            );
          }
        }
      }, 1200);
    } else {
      if (pollIntervalRef.current) clearInterval(pollIntervalRef.current);
    }

    return () => {
      if (pollIntervalRef.current) clearInterval(pollIntervalRef.current);
    };
  }, [scrapeStatus?.status, loadData]);

  // Periodic Backend Health Check Polling (Every 5 Seconds)
  useEffect(() => {
    loadHealth();
    const interval = setInterval(() => {
      loadHealth();
    }, 5000);

    return () => clearInterval(interval);
  }, [loadHealth]);

  // Initial Data Load
  useEffect(() => {
    loadData();
  }, [loadData]);

  return (
    <div className="min-h-screen bg-[#f8f9fa] text-stone-900 font-sans flex flex-col antialiased">
      {/* Top Navbar with Multi-Page Navigation Tabs */}
      <Navbar
        activeTab={activeTab}
        onTabChange={setActiveTab}
        health={health}
        isScraping={scrapeStatus?.status === 'running'}
        onStartScrape={handleStartScrape}
        onRefreshHealth={loadHealth}
      />

      {/* Main Container - Full Width Fluid Layout */}
      <main className="flex-1 w-full max-w-[1920px] mx-auto px-6 lg:px-10 py-8 space-y-6">
        {/* TAB 1: DASHBOARD OVERVIEW */}
        {activeTab === 'dashboard' && (
          <div className="space-y-6 animate-fadeIn">
            <section>
              <StatsCards stats={stats} isLoading={isLoading} />
            </section>

            {!isBannerDismissed && (
              <ScrapeProgress status={scrapeStatus} onDismiss={handleDismissProgress} />
            )}

            <section className="bg-white border border-stone-200/90 rounded-2xl p-6 shadow-sm space-y-4">
              <h2 className="text-lg font-black text-stone-900 tracking-tight">Platform Quick Actions & Overview</h2>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
                <button
                  onClick={() => setActiveTab('scraped-data')}
                  className="p-6 rounded-2xl border border-stone-200/90 bg-stone-50/70 hover:bg-white hover:border-stone-300 hover:shadow-md transition-all text-left space-y-2 group"
                >
                  <div className="text-3xl">🗃️</div>
                  <h3 className="font-extrabold text-stone-900 group-hover:text-emerald-700 transition text-base">
                    Explore Scraped Portfolios
                  </h3>
                  <p className="text-xs text-stone-500 leading-relaxed">
                    View, search, filter, and manage all {stats?.total_portfolios || 122} scraped portfolio items across 11 categories in fluid table or grid card views.
                  </p>
                </button>

                <button
                  onClick={() => setActiveTab('analysis')}
                  className="p-6 rounded-2xl border border-emerald-200/90 bg-emerald-50/40 hover:bg-emerald-50/80 hover:border-emerald-300 hover:shadow-md transition-all text-left space-y-2 group"
                >
                  <div className="text-3xl">⚡</div>
                  <h3 className="font-extrabold text-emerald-950 group-hover:text-emerald-700 transition text-base">
                    Run Website Technology Analysis Engine
                  </h3>
                  <p className="text-xs text-stone-600 leading-relaxed">
                    Analyze technology stacks, CMS, frameworks, backend language, web servers, DNS, and SSL certificates with evidence verification.
                  </p>
                </button>
              </div>
            </section>
          </div>
        )}

        {/* TAB 2: SCRAPED DATA TABLE & CARDS */}
        {activeTab === 'scraped-data' && (
          <div className="space-y-6">
            {/* Category Filters */}
            <section className="bg-white border border-stone-200 rounded-xl p-5 shadow-sm">
              <CategoryFilter
                selectedCategory={selectedCategory}
                onSelectCategory={handleCategorySelect}
                categoriesSummary={stats?.categories_summary || []}
              />
            </section>

            {/* Search Bar, Sorting Controls, & View Mode Controls */}
            <section className="bg-white border border-stone-200 rounded-xl p-4 shadow-sm flex flex-col md:flex-row items-center justify-between gap-4">
              <div className="flex-1 w-full">
                <SearchBar
                  initialValue={searchQuery}
                  onSearchChange={handleSearchChange}
                />
              </div>

              <div className="flex flex-wrap items-center gap-3 shrink-0">
                {/* Sort Controls */}
                <div className="flex items-center gap-1.5 text-xs text-stone-600 bg-stone-50 border border-stone-200 px-2.5 py-1.5 rounded-lg">
                  <span className="text-stone-400">Sort:</span>
                  <select
                    value={sortBy}
                    onChange={(e) => setSortBy(e.target.value)}
                    className="bg-transparent font-medium text-stone-800 focus:outline-none cursor-pointer"
                  >
                    <option value="id">ID</option>
                    <option value="business_name">Business Name</option>
                    <option value="category">Category</option>
                    <option value="country">Country</option>
                    <option value="created_at">Date Added</option>
                  </select>

                  <button
                    onClick={() => setSortOrder((prev) => (prev === 'asc' ? 'desc' : 'asc'))}
                    title={`Sort order: ${sortOrder.toUpperCase()}`}
                    className="font-bold text-stone-700 hover:text-stone-900 ml-1 px-1 rounded bg-stone-200/60"
                  >
                    {sortOrder === 'asc' ? '↑ ASC' : '↓ DESC'}
                  </button>
                </div>

                {/* View Mode Toggle */}
                <div className="flex items-center bg-stone-100 p-1 rounded-lg border border-stone-200">
                  <button
                    onClick={() => setViewMode('table')}
                    className={`px-3 py-1.5 rounded-md text-xs font-semibold transition ${
                      viewMode === 'table'
                        ? 'bg-white text-stone-900 shadow-sm'
                        : 'text-stone-600 hover:text-stone-900'
                    }`}
                  >
                    📋 Table
                  </button>
                  <button
                    onClick={() => setViewMode('grid')}
                    className={`px-3 py-1.5 rounded-md text-xs font-semibold transition ${
                      viewMode === 'grid'
                        ? 'bg-white text-stone-900 shadow-sm'
                        : 'text-stone-600 hover:text-stone-900'
                    }`}
                  >
                    🎴 Cards
                  </button>
                </div>

                <button
                  onClick={loadData}
                  title="Refresh Portfolio Data"
                  className="p-2 text-xs text-stone-600 hover:text-stone-900 rounded-lg bg-stone-100 hover:bg-stone-200/80 border border-stone-200 transition font-medium"
                >
                  ↻ Refresh
                </button>
              </div>
            </section>

            {/* Live Scrape Progress Bar Tracker */}
            {!isBannerDismissed && (
              <ScrapeProgress status={scrapeStatus} onDismiss={handleDismissProgress} />
            )}

            {/* Main Content Area */}
            <section>
              {error ? (
                <ErrorState message={error} onRetry={loadData} />
              ) : isLoading ? (
                <LoadingState viewMode={viewMode} />
              ) : portfolios.length === 0 ? (
                <EmptyState
                  searchQuery={searchQuery}
                  selectedCategory={selectedCategory}
                  onClearFilters={() => {
                    setSearchQuery('');
                    setSelectedCategory('All');
                    setCurrentPage(1);
                  }}
                  onStartScrape={handleStartScrape}
                />
              ) : (
                <div className="space-y-4">
                  <PortfolioTable
                    items={portfolios}
                    viewMode={viewMode}
                    onDelete={handleDelete}
                  />

                  <Pagination
                    currentPage={currentPage}
                    totalPages={totalPages}
                    totalItems={totalItems}
                    pageSize={pageSize}
                    onPageChange={setCurrentPage}
                    onPageSizeChange={(newSize) => {
                      setPageSize(newSize);
                      setCurrentPage(1);
                    }}
                  />
                </div>
              )}
            </section>
          </div>
        )}

        {/* TAB 3: WEBSITE ANALYSIS ENGINE */}
        {activeTab === 'analysis' && (
          <AnalysisTab
            portfolios={portfolios}
            totalItems={totalItems}
            totalPages={totalPages}
            currentPage={currentPage}
            pageSize={pageSize}
            onPageChange={setCurrentPage}
            onPageSizeChange={(newSize) => {
              setPageSize(newSize);
              setCurrentPage(1);
            }}
            onRefreshPortfolios={loadData}
          />
        )}
      </main>

      {/* Footer */}
      <footer className="border-t border-stone-200 bg-white py-6 text-center text-xs text-stone-500">
        OptiInfo Portfolio Scraper & Website Analysis Platform • Evidence-Based Technology Fingerprinting
      </footer>
    </div>
  );
}

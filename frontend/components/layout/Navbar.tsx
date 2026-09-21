'use client';

import { HealthStatus } from '@/lib/types';
import ScrapeButton from '../dashboard/ScrapeButton';

interface NavbarProps {
  activeTab: 'dashboard' | 'scraped-data' | 'analysis';
  onTabChange: (tab: 'dashboard' | 'scraped-data' | 'analysis') => void;
  health: HealthStatus | null;
  isScraping: boolean;
  onStartScrape: () => void;
  onRefreshHealth: () => void;
}

export default function Navbar({
  activeTab,
  onTabChange,
  health,
  isScraping,
  onStartScrape,
  onRefreshHealth,
}: NavbarProps) {
  const isHealthy = health?.status === 'healthy';

  return (
    <header className="sticky top-0 z-40 bg-white/90 backdrop-blur-md text-stone-900 border-b border-stone-200/80 shadow-xs transition-all">
      <div className="w-full max-w-[1920px] mx-auto px-6 lg:px-10">
        <div className="flex flex-col md:flex-row items-center justify-between gap-4 py-3.5">
          {/* Left Side: Brand & Title */}
          <div className="flex items-center gap-3 w-full md:w-auto">
            <div className="w-9 h-9 rounded-xl bg-gradient-to-tr from-stone-900 to-stone-800 text-white flex items-center justify-center font-black text-xl shadow-md">
              P
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h1 className="text-lg font-extrabold tracking-tight text-stone-900">
                  Portfolio Scraper
                </h1>
              </div>
              <p className="text-[11px] text-stone-500 font-medium">
                OptiInfo Portfolio Scraper & Tech Fingerprinting Platform
              </p>
            </div>
          </div>

          {/* Navigation Tabs */}
          <nav className="flex items-center bg-stone-100/80 p-1 rounded-xl border border-stone-200/80">
            <button
              onClick={() => onTabChange('dashboard')}
              className={`flex items-center gap-2 px-4 py-2 rounded-lg text-xs font-bold transition-all ${activeTab === 'dashboard'
                ? 'bg-white text-stone-900 shadow-sm border border-stone-200/80'
                : 'text-stone-600 hover:text-stone-900 hover:bg-stone-200/50'
                }`}
            >
              <span>📊</span>
              <span>Dashboard</span>
            </button>

            <button
              onClick={() => onTabChange('scraped-data')}
              className={`flex items-center gap-2 px-4 py-2 rounded-lg text-xs font-bold transition-all ${activeTab === 'scraped-data'
                ? 'bg-white text-stone-900 shadow-sm border border-stone-200/80'
                : 'text-stone-600 hover:text-stone-900 hover:bg-stone-200/50'
                }`}
            >
              <span>🗃️</span>
              <span>Scraped Data</span>
            </button>

            <button
              onClick={() => onTabChange('analysis')}
              className={`flex items-center gap-2 px-4 py-2 rounded-lg text-xs font-bold transition-all ${activeTab === 'analysis'
                ? 'bg-white text-stone-900 shadow-sm border border-stone-200/80'
                : 'text-stone-600 hover:text-stone-900 hover:bg-stone-200/50'
                }`}
            >
              <span>⚡</span>
              <span>Website Analysis</span>
            </button>
          </nav>

          {/* Right Side: FastAPI Health Indicator & Primary Action */}
          <div className="flex items-center gap-3 w-full md:w-auto justify-between md:justify-end">
            <div
              onClick={onRefreshHealth}
              title="Click to re-check API status"
              className={`cursor-pointer flex items-center gap-2 px-3.5 py-1.5 rounded-full text-xs font-bold border transition ${health === null
                ? 'bg-amber-50 text-amber-800 border-amber-200 hover:bg-amber-100'
                : isHealthy
                  ? 'bg-emerald-50 text-emerald-800 border-emerald-200 hover:bg-emerald-100'
                  : 'bg-rose-50 text-rose-800 border-rose-200 hover:bg-rose-100'
                }`}
            >
              <span
                className={`w-2 h-2 rounded-full ${health === null
                  ? 'bg-amber-500 animate-ping'
                  : isHealthy
                    ? 'bg-emerald-500 animate-pulse'
                    : 'bg-rose-500'
                  }`}
              />
              <span>
                FastAPI: {health === null ? 'Connecting...' : isHealthy ? 'Online' : 'Offline'}
              </span>
            </div>

            <ScrapeButton
              isScraping={isScraping}
              isBackendHealthy={isHealthy}
              onStartScrape={onStartScrape}
            />
          </div>
        </div>
      </div>
    </header>
  );
}

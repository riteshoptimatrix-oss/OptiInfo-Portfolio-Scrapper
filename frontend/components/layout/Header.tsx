'use client';

import { HealthStatus } from '@/lib/types';
import ScrapeButton from '../dashboard/ScrapeButton';

interface HeaderProps {
  health: HealthStatus | null;
  isScraping: boolean;
  onStartScrape: () => void;
  onRefreshHealth: () => void;
}

export default function Header({
  health,
  isScraping,
  onStartScrape,
  onRefreshHealth,
}: HeaderProps) {
  const isHealthy = health?.status === 'healthy';

  return (
    <header className="sticky top-0 z-40 bg-stone-50/90 backdrop-blur-md border-b border-stone-200 text-stone-900 px-6 py-4 transition-all">
      <div className="max-w-7xl mx-auto flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
        {/* Brand & Subtitle */}
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-stone-900 text-stone-50 flex items-center justify-center font-bold text-xl shadow-md">
            P
          </div>
          <div>
            <div className="flex items-center gap-2.5">
              <h1 className="text-xl font-extrabold tracking-tight text-stone-900">
                Portfolio Scraper
              </h1>
              <span className="text-[10px] font-mono font-medium px-2 py-0.5 rounded-full bg-stone-200/70 text-stone-700 border border-stone-300">
                OptiInfo Engine
              </span>
            </div>
            <p className="text-xs text-stone-500 mt-0.5">
              Production Admin Dashboard • Playwright + FastAPI + SQLite
            </p>
          </div>
        </div>

        {/* Backend Status & Primary Scrape Button */}
        <div className="flex items-center gap-3 w-full md:w-auto justify-between md:justify-end">
          {/* Status Badge */}
          <div
            onClick={onRefreshHealth}
            title="Click to re-check API status"
            className={`cursor-pointer flex items-center gap-2 px-3 py-1.5 rounded-full text-xs font-medium border transition ${
              isHealthy
                ? 'bg-emerald-50 text-emerald-800 border-emerald-200 hover:bg-emerald-100/60'
                : 'bg-rose-50 text-rose-800 border-rose-200 hover:bg-rose-100/60'
            }`}
          >
            <span
              className={`w-2 h-2 rounded-full ${
                isHealthy ? 'bg-emerald-500 animate-pulse' : 'bg-rose-500'
              }`}
            />
            <span>FastAPI: {isHealthy ? 'Online' : 'Offline'}</span>
          </div>

          {/* Primary Action Button */}
          <ScrapeButton
            isScraping={isScraping}
            isBackendHealthy={isHealthy}
            onStartScrape={onStartScrape}
          />
        </div>
      </div>
    </header>
  );
}

'use client';

interface ScraperControlsProps {
  searchQuery: string;
  onSearchChange: (query: string) => void;
  onRefreshData: () => void;
  isBackendHealthy: boolean;
}

export default function ScraperControls({
  searchQuery,
  onSearchChange,
  onRefreshData,
  isBackendHealthy,
}: ScraperControlsProps) {
  return (
    <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 shadow-xl flex flex-col md:flex-row items-stretch md:items-center justify-between gap-4">
      {/* Search Input */}
      <div className="relative flex-1">
        <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none text-slate-500 text-sm">
          🔍
        </div>
        <input
          type="text"
          value={searchQuery}
          onChange={(e) => onSearchChange(e.target.value)}
          placeholder="Search by Business Name..."
          className="w-full pl-9 pr-4 py-2.5 bg-slate-950 border border-slate-800 rounded-lg text-sm text-slate-200 placeholder-slate-500 focus:outline-none focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 transition"
        />
      </div>

      {/* Control Actions */}
      <div className="flex items-center gap-3">
        <button
          onClick={onRefreshData}
          className="px-4 py-2.5 bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 rounded-lg text-xs font-semibold flex items-center gap-2 transition"
        >
          <span>↻</span> Refresh List
        </button>

        <button
          disabled={!isBackendHealthy}
          title={isBackendHealthy ? 'Trigger Scraper (Phase 2)' : 'Backend API offline'}
          className={`px-5 py-2.5 rounded-lg text-xs font-bold uppercase tracking-wider flex items-center gap-2 transition shadow-lg ${
            isBackendHealthy
              ? 'bg-indigo-600 hover:bg-indigo-500 text-white shadow-indigo-600/25 cursor-pointer'
              : 'bg-slate-800 text-slate-500 border border-slate-700 cursor-not-allowed'
          }`}
        >
          <span>⚡</span> Start Playwright Scraper
        </button>
      </div>
    </div>
  );
}

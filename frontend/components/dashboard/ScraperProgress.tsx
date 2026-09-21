'use client';

import { ScrapeStatus } from '@/lib/types';

interface ScrapeProgressProps {
  status: ScrapeStatus | null;
}

export default function ScraperProgress({ status }: ScrapeProgressProps) {
  if (!status || status.status === 'idle') return null;

  const isRunning = status.status === 'running';
  const isFailed = status.status === 'failed';
  const progressPercent = Math.min(100, Math.max(0, status.progress || 0));

  return (
    <div className="bg-white border border-stone-200 rounded-xl p-5 shadow-sm space-y-3">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
        <div className="flex items-center gap-2.5">
          <span
            className={`w-3 h-3 rounded-full ${
              isRunning
                ? 'bg-amber-500 animate-ping'
                : isFailed
                ? 'bg-rose-500'
                : 'bg-emerald-500'
            }`}
          />
          <h3 className="text-sm font-bold text-stone-900">
            Scraper Engine Status:{' '}
            <span
              className={`uppercase tracking-wider ${
                isRunning
                  ? 'text-amber-700'
                  : isFailed
                  ? 'text-rose-700'
                  : 'text-emerald-700'
              }`}
            >
              {status.status}
            </span>
          </h3>
        </div>

        <div className="text-xs font-mono text-stone-600 flex items-center gap-4">
          <span>Processed: {status.processed} / {status.total}</span>
          <span className="text-emerald-700 font-semibold">Success: {status.successful}</span>
          <span className="text-rose-700 font-semibold">Failed: {status.failed}</span>
        </div>
      </div>

      {/* Progress Bar */}
      <div className="w-full bg-stone-100 rounded-full h-2.5 overflow-hidden border border-stone-200">
        <div
          className={`h-full rounded-full transition-all duration-300 ${
            isFailed
              ? 'bg-rose-500'
              : isRunning
              ? 'bg-stone-800'
              : 'bg-emerald-600'
          }`}
          style={{ width: `${progressPercent}%` }}
        />
      </div>

      <div className="flex justify-between items-center text-[11px] text-stone-500">
        <span>
          {isRunning
            ? 'Running direct Python Playwright Chromium DOM inspection...'
            : isFailed
            ? `Scraper Error: ${status.error || 'Unknown error'}`
            : 'All available portfolio items extracted successfully.'}
        </span>
        <span className="font-mono font-semibold text-stone-700">{progressPercent}%</span>
      </div>
    </div>
  );
}

'use client';

import { useEffect, useRef } from 'react';
import { ScrapeStatus } from '@/lib/types';

interface ScrapeProgressProps {
  status: ScrapeStatus | null;
  onDismiss?: () => void;
}

export default function ScrapeProgress({ status, onDismiss }: ScrapeProgressProps) {
  const logsEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (logsEndRef.current) {
      logsEndRef.current.scrollTop = logsEndRef.current.scrollHeight;
    }
  }, [status?.logs]);

  if (!status || status.status === 'idle') return null;

  const isRunning = status.status === 'running';
  const isCompleted = status.status === 'completed';
  const isFailed = status.status === 'failed';
  const progressPercent = Math.min(100, Math.max(0, status.progress || 0));

  // Generate ASCII block progress bar indicator: ████████████░░░░░░
  const totalBlocks = 20;
  const filledBlocks = Math.round((progressPercent / 100) * totalBlocks);
  const progressBarAscii = '█'.repeat(filledBlocks) + '░'.repeat(totalBlocks - filledBlocks);

  return (
    <div
      className={`border rounded-xl p-5 shadow-sm space-y-3.5 transition-all duration-300 ${
        isRunning
          ? 'bg-amber-50/40 border-amber-200/80'
          : isFailed
          ? 'bg-rose-50/40 border-rose-200/80'
          : 'bg-emerald-50/40 border-emerald-200/80'
      }`}
    >
      {/* Status Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
        <div className="flex items-center gap-3">
          <span
            className={`w-3.5 h-3.5 rounded-full ${
              isRunning
                ? 'bg-amber-500 animate-ping'
                : isFailed
                ? 'bg-rose-500'
                : 'bg-emerald-500'
            }`}
          />
          <div>
            <div className="flex items-center gap-2">
              <h3 className="text-sm font-extrabold text-stone-900">
                {isRunning ? 'Scraping...' : isFailed ? 'Scrape Failed' : 'Scrape Completed'}
              </h3>
              <span
                className={`text-[10px] font-bold uppercase tracking-wider px-2 py-0.5 rounded-md border ${
                  isRunning
                    ? 'bg-amber-100 text-amber-800 border-amber-300'
                    : isFailed
                    ? 'bg-rose-100 text-rose-800 border-rose-300'
                    : 'bg-emerald-100 text-emerald-800 border-emerald-300'
                }`}
              >
                {status.status}
              </span>
            </div>
            <p className="text-xs text-stone-500 mt-0.5">
              {isRunning
                ? 'Extracting portfolio cards using Python Playwright direct DOM inspection...'
                : isFailed
                ? `Error: ${status.error || 'Scraper process failed'}`
                : 'All target portfolio items extracted and saved to database.'}
            </p>
          </div>
        </div>

        {/* Count Breakdown Metrics */}
        <div className="flex items-center gap-4 text-xs font-mono bg-white/80 p-2.5 rounded-lg border border-stone-200 shadow-2xs">
          <div>
            <span className="text-stone-400 block text-[10px] uppercase font-sans">Processed</span>
            <span className="font-bold text-stone-900">{status.processed} / {status.total}</span>
          </div>
          <div className="h-6 w-px bg-stone-200" />
          <div>
            <span className="text-stone-400 block text-[10px] uppercase font-sans">Successful</span>
            <span className="font-bold text-emerald-700">{status.successful}</span>
          </div>
          <div className="h-6 w-px bg-stone-200" />
          <div>
            <span className="text-stone-400 block text-[10px] uppercase font-sans">Failed</span>
            <span className="font-bold text-rose-700">{status.failed}</span>
          </div>
        </div>
      </div>

      {/* Progress Bar Component */}
      <div className="space-y-1.5">
        <div className="flex items-center justify-between text-xs font-mono text-stone-700">
          <span className="font-mono text-stone-500 tracking-widest">{progressBarAscii}</span>
          <span className="font-bold text-stone-900">{progressPercent}%</span>
        </div>

        <div className="w-full bg-stone-200/80 rounded-full h-3 overflow-hidden border border-stone-300/60">
          <div
            className={`h-full rounded-full transition-all duration-300 ${
              isFailed
                ? 'bg-rose-600'
                : isRunning
                ? 'bg-amber-600'
                : 'bg-emerald-600'
            }`}
            style={{ width: `${progressPercent}%` }}
          />
        </div>
      </div>

      {/* Real-time Logs Terminal */}
      {status.logs && status.logs.length > 0 && (
        <div className="bg-stone-900 rounded-lg overflow-hidden border border-stone-700 shadow-inner mt-4">
          <div className="bg-stone-800 px-3 py-1.5 flex items-center gap-2 border-b border-stone-700">
            <div className="flex gap-1.5">
              <span className="w-2.5 h-2.5 rounded-full bg-rose-500"></span>
              <span className="w-2.5 h-2.5 rounded-full bg-amber-500"></span>
              <span className="w-2.5 h-2.5 rounded-full bg-emerald-500"></span>
            </div>
            <span className="text-[10px] text-stone-400 font-mono tracking-widest font-bold ml-2 uppercase">Execution Logs</span>
          </div>
          <div className="p-3 text-xs font-mono text-stone-300 h-40 overflow-y-auto" ref={logsEndRef}>
            {status.logs.map((log, idx) => (
              <div key={idx} className="mb-1 opacity-90 break-all whitespace-pre-wrap">
                {log}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Dismiss / Close Action for completed or failed states */}
      {(isCompleted || isFailed) && onDismiss && (
        <div className="pt-2 flex justify-end">
          <button
            onClick={onDismiss}
            className="text-xs text-stone-500 hover:text-stone-800 underline font-medium"
          >
            Dismiss Status Banner
          </button>
        </div>
      )}
    </div>
  );
}

'use client';

import { PortfolioWebsite } from '@/lib/types';

interface PortfolioCardProps {
  item: PortfolioWebsite;
  onDelete?: (id: number) => void;
}

export default function PortfolioCard({ item, onDelete }: PortfolioCardProps) {
  return (
    <div className="bg-white border border-stone-200/90 rounded-2xl p-5 shadow-xs hover:shadow-md transition-all duration-200 flex flex-col justify-between space-y-4 group">
      <div>
        {/* Header: Business Name & Status */}
        <div className="flex items-start justify-between gap-3">
          <h3 className="text-base font-extrabold text-stone-900 group-hover:text-stone-950 transition line-clamp-1">
            {item.business_name}
          </h3>
          <span className="px-2.5 py-0.5 rounded-full text-[10px] font-bold font-mono uppercase tracking-wider bg-emerald-100/80 text-emerald-800 border border-emerald-200 shrink-0">
            {item.status || 'Scraped'}
          </span>
        </div>

        {/* Category & Country Badges */}
        <div className="mt-2.5 flex flex-wrap items-center gap-2 text-xs">
          <span className="px-2.5 py-1 rounded-lg bg-stone-100 text-stone-700 font-semibold border border-stone-200/80">
            {item.category}
          </span>
          <span className="px-2.5 py-1 rounded-lg bg-stone-50 text-stone-600 font-semibold border border-stone-200/80 flex items-center gap-1">
            📍 {item.country || 'Not Specified'}
          </span>
        </div>

        {/* Website URL display */}
        <div className="mt-3 text-xs font-mono text-stone-500 truncate">
          {item.website_url ? (
            <span title={item.website_url}>{item.website_url}</span>
          ) : (
            <span className="italic text-stone-400">No URL Available</span>
          )}
        </div>
      </div>

      {/* Footer: Visit Website Button & Delete Option */}
      <div className="pt-3 border-t border-stone-100 flex items-center justify-between gap-2">
        {item.website_url ? (
          <a
            href={item.website_url}
            target="_blank"
            rel="noopener noreferrer"
            className="w-full text-center px-4 py-2 rounded-xl bg-stone-900 text-white hover:bg-stone-800 text-xs font-bold shadow-xs transition flex items-center justify-center gap-1.5"
          >
            <span>Visit Website</span>
            <span className="text-[10px]">↗</span>
          </a>
        ) : (
          <button
            disabled
            className="w-full text-center px-4 py-2 rounded-xl bg-stone-100 text-stone-400 text-xs font-semibold cursor-not-allowed border border-stone-200/80"
          >
            No Link
          </button>
        )}

        {onDelete && (
          <button
            onClick={() => onDelete(item.id)}
            title="Delete portfolio item"
            className="p-2 rounded-xl text-stone-400 hover:text-rose-600 hover:bg-rose-50 transition border border-transparent hover:border-rose-200"
          >
            🗑️
          </button>
        )}
      </div>
    </div>
  );
}

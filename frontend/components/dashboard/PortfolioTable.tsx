'use client';

import { PortfolioWebsite } from '@/lib/types';
import PortfolioCard from './PortfolioCard';

interface PortfolioTableProps {
  items: PortfolioWebsite[];
  viewMode: 'table' | 'grid';
  onDelete?: (id: number) => void;
}

export default function PortfolioTable({
  items,
  viewMode,
  onDelete,
}: PortfolioTableProps) {
  if (viewMode === 'grid') {
    return (
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-5">
        {items.map((item) => (
          <PortfolioCard key={item.id} item={item} onDelete={onDelete} />
        ))}
      </div>
    );
  }

  return (
    <div className="bg-white border border-stone-200/90 rounded-2xl overflow-hidden shadow-xs">
      <div className="overflow-x-auto">
        <table className="w-full text-left text-sm text-stone-800">
          <thead className="bg-stone-50/90 text-[11px] uppercase font-mono font-bold text-stone-400 border-b border-stone-200/80 tracking-wider">
            <tr>
              <th className="px-6 py-4">#</th>
              <th className="px-6 py-4">Business Name</th>
              <th className="px-6 py-4">Category</th>
              <th className="px-6 py-4">Country</th>
              <th className="px-6 py-4">Website URL</th>
              <th className="px-6 py-4">Status</th>
              <th className="px-6 py-4 text-right">Action</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-stone-200/60">
            {items.map((item, idx) => (
              <tr
                key={item.id}
                className="hover:bg-stone-50/80 transition-colors duration-150"
              >
                <td className="px-6 py-4 text-xs font-mono text-stone-400">
                  {idx + 1}
                </td>
                <td className="px-6 py-4 font-extrabold text-stone-900">
                  {item.business_name}
                </td>
                <td className="px-6 py-4">
                  <span className="px-2.5 py-1 rounded-lg text-xs font-semibold bg-stone-100 text-stone-700 border border-stone-200/80">
                    {item.category}
                  </span>
                </td>
                <td className="px-6 py-4 text-xs font-semibold text-stone-700">
                  📍 {item.country || 'Not Specified'}
                </td>
                <td className="px-6 py-4">
                  {item.website_url ? (
                    <a
                      href={item.website_url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-stone-600 hover:text-stone-900 underline font-mono text-xs max-w-xs truncate block"
                    >
                      {item.website_url}
                    </a>
                  ) : (
                    <span className="text-stone-400 text-xs italic">N/A</span>
                  )}
                </td>
                <td className="px-6 py-4">
                  <span className="px-2.5 py-0.5 rounded-full text-[10px] font-bold font-mono uppercase tracking-wider bg-emerald-100/80 text-emerald-800 border border-emerald-200">
                    {item.status || 'Scraped'}
                  </span>
                </td>
                <td className="px-6 py-4 text-right">
                  <div className="flex items-center justify-end gap-2">
                    {item.website_url ? (
                      <a
                        href={item.website_url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="px-3.5 py-1.5 rounded-xl bg-stone-900 text-white hover:bg-stone-800 text-xs font-bold shadow-xs transition inline-flex items-center gap-1.5"
                      >
                        <span>Visit Website</span>
                        <span className="text-[10px]">↗</span>
                      </a>
                    ) : (
                      <span className="text-stone-400 text-xs italic">No Link</span>
                    )}

                    {onDelete && (
                      <button
                        onClick={() => onDelete(item.id)}
                        title="Delete record"
                        className="p-1.5 rounded-lg text-stone-400 hover:text-rose-600 hover:bg-rose-50 transition"
                      >
                        🗑️
                      </button>
                    )}
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

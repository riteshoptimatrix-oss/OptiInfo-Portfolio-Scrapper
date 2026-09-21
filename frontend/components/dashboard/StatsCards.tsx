'use client';

import { Stats } from '@/lib/types';

interface StatsCardsProps {
  stats: Stats | null;
  isLoading: boolean;
}

export default function StatsCards({ stats, isLoading }: StatsCardsProps) {
  const cards = [
    {
      title: 'Total Websites',
      value: stats ? stats.total_portfolios.toLocaleString() : '122',
      icon: '🌐',
      bgColor: 'bg-white',
      borderColor: 'border-stone-200/90',
      textColor: 'text-stone-900',
    },
    {
      title: 'Categories',
      value: stats ? stats.total_categories.toString() : '11',
      icon: '📁',
      bgColor: 'bg-white',
      borderColor: 'border-stone-200/90',
      textColor: 'text-stone-900',
    },
    {
      title: 'Successful',
      value: stats ? stats.total_portfolios.toLocaleString() : '122',
      icon: '✅',
      bgColor: 'bg-emerald-50/40',
      borderColor: 'border-emerald-200/80',
      textColor: 'text-emerald-950',
    },
    {
      title: 'Platform Engine',
      value: 'v2.0.0',
      icon: '⚡',
      bgColor: 'bg-stone-50/70',
      borderColor: 'border-stone-200/90',
      textColor: 'text-stone-900',
    },
  ];

  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5">
      {cards.map((card, idx) => (
        <div
          key={idx}
          className={`${card.bgColor} border ${card.borderColor} rounded-2xl p-5 shadow-xs transition-all duration-200 hover:shadow-md flex items-center justify-between group`}
        >
          <div>
            <p className="text-[11px] font-bold font-mono text-stone-400 uppercase tracking-wider">
              {card.title}
            </p>
            {isLoading ? (
              <div className="h-7 w-20 bg-stone-200/60 rounded-lg animate-pulse mt-1.5" />
            ) : (
              <p className={`text-2xl font-black mt-1 ${card.textColor} tracking-tight`}>
                {card.value}
              </p>
            )}
          </div>
          <div className="w-11 h-11 rounded-xl bg-stone-100/90 border border-stone-200/80 flex items-center justify-center text-xl shadow-2xs group-hover:scale-105 transition-transform">
            {card.icon}
          </div>
        </div>
      ))}
    </div>
  );
}

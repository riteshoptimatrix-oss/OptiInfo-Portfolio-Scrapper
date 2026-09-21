'use client';

interface LoadingStateProps {
  viewMode?: 'table' | 'grid';
}

export default function LoadingState({ viewMode = 'table' }: LoadingStateProps) {
  if (viewMode === 'grid') {
    return (
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {Array.from({ length: 6 }).map((_, idx) => (
          <div
            key={idx}
            className="bg-white border border-stone-200 rounded-xl p-5 shadow-sm space-y-4 animate-pulse"
          >
            <div className="flex items-center justify-between">
              <div className="h-5 bg-stone-200/80 rounded w-36" />
              <div className="h-4 bg-stone-200/60 rounded-full w-14" />
            </div>
            <div className="flex gap-2">
              <div className="h-6 bg-stone-200/60 rounded w-24" />
              <div className="h-6 bg-stone-200/60 rounded w-16" />
            </div>
            <div className="h-4 bg-stone-200/60 rounded w-48" />
            <div className="pt-3 border-t border-stone-100">
              <div className="h-9 bg-stone-200/80 rounded-lg w-full" />
            </div>
          </div>
        ))}
      </div>
    );
  }

  return (
    <div className="bg-white border border-stone-200 rounded-xl overflow-hidden shadow-sm">
      <div className="p-4 border-b border-stone-200 bg-stone-100/50">
        <div className="h-4 bg-stone-200/80 rounded w-48 animate-pulse" />
      </div>
      <div className="divide-y divide-stone-200/80">
        {Array.from({ length: 5 }).map((_, idx) => (
          <div key={idx} className="p-4 flex items-center justify-between animate-pulse">
            <div className="flex items-center gap-4">
              <div className="h-4 bg-stone-200/80 rounded w-6" />
              <div className="h-5 bg-stone-200/80 rounded w-40" />
            </div>
            <div className="h-6 bg-stone-200/60 rounded w-28" />
            <div className="h-4 bg-stone-200/60 rounded w-20" />
            <div className="h-4 bg-stone-200/60 rounded w-48" />
            <div className="h-8 bg-stone-200/80 rounded-lg w-28" />
          </div>
        ))}
      </div>
    </div>
  );
}

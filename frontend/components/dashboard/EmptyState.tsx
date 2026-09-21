'use client';

interface EmptyStateProps {
  searchQuery?: string;
  selectedCategory?: string;
  onClearFilters?: () => void;
  onStartScrape?: () => void;
}

export default function EmptyState({
  searchQuery,
  selectedCategory,
  onClearFilters,
  onStartScrape,
}: EmptyStateProps) {
  const hasActiveFilters = Boolean(
    (searchQuery && searchQuery.trim().length > 0) ||
      (selectedCategory && selectedCategory !== 'All')
  );

  return (
    <div className="bg-white border border-stone-200 rounded-xl p-12 text-center shadow-sm max-w-lg mx-auto my-6 space-y-4">
      <div className="w-16 h-16 rounded-full bg-stone-100 border border-stone-200 flex items-center justify-center text-3xl mx-auto">
        {hasActiveFilters ? '🔍' : '📁'}
      </div>

      <div className="space-y-1">
        <h3 className="text-base font-bold text-stone-900">
          {hasActiveFilters ? 'No Matching Portfolios Found' : 'No Portfolio Records Saved'}
        </h3>
        <p className="text-xs text-stone-500 max-w-md mx-auto">
          {hasActiveFilters
            ? `No records found matching query "${searchQuery || ''}" ${
                selectedCategory !== 'All' ? `in category "${selectedCategory}"` : ''
              }. Try clearing filters.`
            : 'Click "Start Scraping" to trigger Python Playwright engine to inspect and populate portfolio items.'}
        </p>
      </div>

      <div className="pt-2 flex items-center justify-center gap-3">
        {hasActiveFilters && onClearFilters && (
          <button
            onClick={onClearFilters}
            className="px-4 py-2 rounded-lg bg-stone-100 hover:bg-stone-200 text-stone-800 text-xs font-semibold border border-stone-200 transition"
          >
            Clear Search & Filters
          </button>
        )}

        {!hasActiveFilters && onStartScrape && (
          <button
            onClick={onStartScrape}
            className="px-5 py-2 rounded-lg bg-stone-900 hover:bg-stone-800 text-stone-50 text-xs font-semibold shadow-sm transition"
          >
            ⚡ Start Scraping
          </button>
        )}
      </div>
    </div>
  );
}

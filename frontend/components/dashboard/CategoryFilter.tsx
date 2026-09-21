'use client';

import { CATEGORIES } from '@/lib/constants';
import { CategorySummary } from '@/lib/types';

interface CategoryFilterProps {
  selectedCategory: string;
  onSelectCategory: (cat: string) => void;
  categoriesSummary?: CategorySummary[];
}

export default function CategoryFilter({
  selectedCategory,
  onSelectCategory,
  categoriesSummary = [],
}: CategoryFilterProps) {
  // Extract dynamic categories from the summary and always include "All"
  const dynamicCategories = ['All', ...categoriesSummary.map((c) => c.name)].sort();
  
  // Map category counts
  const countMap = new Map<string, number>();
  categoriesSummary.forEach((c) => countMap.set(c.name.toLowerCase(), c.count));

  return (
    <div className="space-y-2">
      <div className="flex items-center justify-between">
        <span className="text-xs font-semibold text-stone-500 uppercase tracking-wider">
          Filter By Category ({dynamicCategories.length})
        </span>
        {selectedCategory !== 'All' && (
          <button
            onClick={() => onSelectCategory('All')}
            className="text-xs text-stone-500 hover:text-stone-900 underline font-medium"
          >
            Clear Filter
          </button>
        )}
      </div>

      <div className="flex flex-wrap gap-2 max-h-36 overflow-y-auto pr-1 scrollbar-thin">
        {dynamicCategories.map((category) => {
          const isSelected = selectedCategory === category;
          const count = countMap.get(category.toLowerCase());

          return (
            <button
              key={category}
              onClick={() => onSelectCategory(category)}
              className={`px-3.5 py-1.5 rounded-lg text-xs font-medium transition-all duration-150 flex items-center gap-1.5 ${
                isSelected
                  ? 'bg-stone-900 text-stone-50 shadow-sm border border-stone-900 font-semibold'
                  : 'bg-white text-stone-700 hover:bg-stone-100/80 border border-stone-200 shadow-sm'
              }`}
            >
              <span>{category}</span>
              {count !== undefined && count > 0 && category !== 'All' && (
                <span
                  className={`text-[10px] px-1.5 py-0.2 rounded-full font-mono ${
                    isSelected
                      ? 'bg-stone-700 text-stone-100'
                      : 'bg-stone-100 text-stone-600 border border-stone-200'
                  }`}
                >
                  {count}
                </span>
              )}
            </button>
          );
        })}
      </div>
    </div>
  );
}

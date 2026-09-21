'use client';

import { useState, useEffect } from 'react';

interface SearchBarProps {
  initialValue: string;
  onSearchChange: (value: string) => void;
  debounceMs?: number;
}

export default function SearchBar({
  initialValue,
  onSearchChange,
  debounceMs = 300,
}: SearchBarProps) {
  const [searchTerm, setSearchTerm] = useState(initialValue);

  // Sync internal state if initialValue changes externally
  useEffect(() => {
    setSearchTerm(initialValue);
  }, [initialValue]);

  // Debounce search input
  useEffect(() => {
    const handler = setTimeout(() => {
      onSearchChange(searchTerm);
    }, debounceMs);

    return () => clearTimeout(handler);
  }, [searchTerm, onSearchChange, debounceMs]);

  return (
    <div className="relative w-full">
      <div className="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none text-stone-400 text-sm">
        🔍
      </div>
      <input
        type="text"
        value={searchTerm}
        onChange={(e) => setSearchTerm(e.target.value)}
        placeholder="Search business name or website..."
        className="w-full pl-10 pr-9 py-2.5 bg-white border border-stone-200 rounded-lg text-sm text-stone-900 placeholder-stone-400 focus:outline-none focus:border-stone-400 focus:ring-1 focus:ring-stone-400 shadow-sm transition"
      />
      {searchTerm && (
        <button
          onClick={() => {
            setSearchTerm('');
            onSearchChange('');
          }}
          className="absolute inset-y-0 right-0 pr-3 flex items-center text-stone-400 hover:text-stone-600 text-xs font-bold"
        >
          ✕
        </button>
      )}
    </div>
  );
}

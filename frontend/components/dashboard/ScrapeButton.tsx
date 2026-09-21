'use client';

interface ScrapeButtonProps {
  isScraping: boolean;
  isBackendHealthy: boolean;
  onStartScrape: () => void;
}

export default function ScrapeButton({
  isScraping,
  isBackendHealthy,
  onStartScrape,
}: ScrapeButtonProps) {
  const isDisabled = isScraping || !isBackendHealthy;

  return (
    <button
      onClick={onStartScrape}
      disabled={isDisabled}
      className={`px-5 py-2.5 rounded-lg text-xs font-semibold uppercase tracking-wider shadow-sm border transition-all duration-200 flex items-center gap-2 ${
        isScraping
          ? 'bg-amber-50 text-amber-700 border-amber-200 cursor-not-allowed'
          : !isBackendHealthy
          ? 'bg-stone-100 text-stone-400 border-stone-200 cursor-not-allowed'
          : 'bg-stone-900 text-stone-50 hover:bg-stone-800 border-stone-900 active:scale-[0.98] cursor-pointer'
      }`}
    >
      <span className={isScraping ? 'animate-spin' : ''}>
        {isScraping ? '⚙️' : '⚡'}
      </span>
      <span>
        {isScraping
          ? 'Scraping in Progress...'
          : !isBackendHealthy
          ? 'Backend Offline'
          : 'Start Scraping'}
      </span>
    </button>
  );
}

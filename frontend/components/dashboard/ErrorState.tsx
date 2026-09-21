'use client';

interface ErrorStateProps {
  message: string;
  onRetry: () => void;
}

export default function ErrorState({ message, onRetry }: ErrorStateProps) {
  return (
    <div className="bg-rose-50/70 border border-rose-200 rounded-xl p-5 shadow-sm max-w-xl mx-auto my-6 flex items-start gap-4 text-rose-950">
      <div className="text-2xl shrink-0">⚠️</div>
      <div className="flex-1 space-y-1">
        <h4 className="text-sm font-bold text-rose-900">Backend Communication Error</h4>
        <p className="text-xs text-rose-700">{message}</p>
        <div className="pt-2">
          <button
            onClick={onRetry}
            className="px-3.5 py-1.5 rounded-lg bg-rose-900 hover:bg-rose-800 text-rose-50 text-xs font-semibold shadow-sm transition"
          >
            ↻ Retry Connection
          </button>
        </div>
      </div>
    </div>
  );
}

import { useEffect } from 'react';
import { X, Timer } from 'lucide-react';
import { useWorkoutStore } from '@/stores/workoutStore';

interface RestTimerModalProps {
  remaining: number;
  onClose: () => void;
}

export default function RestTimerModal({ remaining, onClose }: RestTimerModalProps) {
  const { tickRestTimer } = useWorkoutStore();

  useEffect(() => {
    const interval = setInterval(() => tickRestTimer(), 1000);
    return () => clearInterval(interval);
  }, []);

  const pct = Math.max(0, (remaining / 60) * 100);

  return (
    <div className="fixed inset-0 bg-black/70 flex items-center justify-center z-50 p-4">
      <div className="bg-slate-800 border border-slate-700 rounded-2xl p-8 w-full max-w-sm text-center space-y-6">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2 text-slate-400">
            <Timer className="w-5 h-5" />
            <span className="font-medium">Rest Timer</span>
          </div>
          <button onClick={onClose} className="text-slate-400 hover:text-white">
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Circle */}
        <div className="relative w-36 h-36 mx-auto">
          <svg className="w-full h-full -rotate-90" viewBox="0 0 120 120">
            <circle cx="60" cy="60" r="54" fill="none" stroke="#1e293b" strokeWidth="8" />
            <circle
              cx="60" cy="60" r="54" fill="none"
              stroke="#7c3aed"
              strokeWidth="8"
              strokeDasharray={`${2 * Math.PI * 54}`}
              strokeDashoffset={`${2 * Math.PI * 54 * (1 - pct / 100)}`}
              strokeLinecap="round"
              className="transition-all duration-1000"
            />
          </svg>
          <div className="absolute inset-0 flex items-center justify-center">
            <span className="text-4xl font-bold text-white tabular-nums">{remaining}</span>
          </div>
        </div>

        <p className="text-slate-400 text-sm">seconds remaining</p>

        <button
          onClick={onClose}
          className="w-full py-3 bg-violet-600 hover:bg-violet-500 text-white rounded-xl font-medium transition-colors"
        >
          Skip Rest
        </button>
      </div>
    </div>
  );
}

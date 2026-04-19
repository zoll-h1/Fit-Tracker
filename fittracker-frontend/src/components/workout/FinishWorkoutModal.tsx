import { useState } from 'react';
import { useMutation } from '@tanstack/react-query';
import { Trophy, X, BarChart3, Clock, Flame } from 'lucide-react';
import { workoutsApi, type WorkoutSession } from '@/api/workouts';

interface FinishWorkoutModalProps {
  session: WorkoutSession;
  elapsed: number;
  onClose: () => void;
  onFinished: () => void;
}

function formatTime(seconds: number): string {
  const m = Math.floor(seconds / 60);
  const h = Math.floor(m / 60);
  if (h > 0) return `${h}h ${m % 60}m`;
  return `${m}m`;
}

export default function FinishWorkoutModal({ session, elapsed, onClose, onFinished }: FinishWorkoutModalProps) {
  const [notes, setNotes] = useState(session.notes || '');

  const finishMutation = useMutation({
    mutationFn: () => workoutsApi.finish(session.id, notes || undefined),
    onSuccess: onFinished,
  });

  const completedSets = session.exercises.flatMap((we) => we.sets.filter((s) => s.completed));
  const totalVolume = completedSets.reduce((acc, s) => {
    if (s.weight_kg && s.reps) return acc + s.weight_kg * s.reps;
    return acc;
  }, 0);
  const prCount = completedSets.filter((s) => s.is_pr).length;

  return (
    <div className="fixed inset-0 bg-black/70 flex items-end sm:items-center justify-center z-50 p-4">
      <div className="bg-slate-800 border border-slate-700 rounded-2xl w-full max-w-md space-y-5 p-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <h2 className="text-xl font-bold text-white">Finish Workout</h2>
          <button onClick={onClose} className="text-slate-400 hover:text-white">
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Summary stats */}
        <div className="grid grid-cols-3 gap-3">
          {[
            { icon: Clock, label: 'Time', value: formatTime(elapsed) },
            { icon: BarChart3, label: 'Volume', value: `${Math.round(totalVolume)} kg` },
            { icon: BarChart3, label: 'Sets', value: String(completedSets.length) },
          ].map(({ icon: Icon, label, value }) => (
            <div key={label} className="bg-slate-700 rounded-xl p-3 text-center">
              <Icon className="w-4 h-4 text-violet-400 mx-auto mb-1" />
              <p className="text-lg font-bold text-white">{value}</p>
              <p className="text-slate-500 text-xs">{label}</p>
            </div>
          ))}
        </div>

        {/* PRs */}
        {prCount > 0 && (
          <div className="flex items-center gap-2 bg-amber-500/10 border border-amber-500/30 rounded-xl p-3">
            <Trophy className="w-5 h-5 text-amber-400 flex-shrink-0" />
            <p className="text-amber-300 text-sm font-medium">
              {prCount} new Personal Record{prCount > 1 ? 's' : ''}! 🎉
            </p>
          </div>
        )}

        {/* Notes */}
        <div>
          <label className="text-sm font-medium text-slate-300 block mb-1.5">Notes (optional)</label>
          <textarea
            value={notes}
            onChange={(e) => setNotes(e.target.value)}
            placeholder="How did it feel? Any notes..."
            rows={3}
            className="w-full px-4 py-2.5 bg-slate-700 border border-slate-600 rounded-lg text-white placeholder-slate-500 focus:outline-none focus:border-violet-500 resize-none text-sm"
          />
        </div>

        <div className="flex gap-3">
          <button onClick={onClose} className="flex-1 py-3 border border-slate-600 rounded-xl text-slate-300 hover:text-white transition-colors">
            Continue
          </button>
          <button
            onClick={() => finishMutation.mutate()}
            disabled={finishMutation.isPending}
            className="flex-1 py-3 bg-violet-600 hover:bg-violet-500 text-white rounded-xl font-semibold transition-colors disabled:opacity-50"
          >
            {finishMutation.isPending ? 'Saving...' : 'Save Workout'}
          </button>
        </div>
      </div>
    </div>
  );
}

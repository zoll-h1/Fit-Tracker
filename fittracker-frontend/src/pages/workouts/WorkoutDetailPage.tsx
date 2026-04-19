import { useParams, useNavigate } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { ArrowLeft, Clock, BarChart3, Flame, Trophy } from 'lucide-react';
import { workoutsApi } from '@/api/workouts';
import { format } from 'date-fns';

function formatDuration(seconds: number | null): string {
  if (!seconds) return '—';
  const m = Math.floor(seconds / 60);
  const h = Math.floor(m / 60);
  if (h > 0) return `${h}h ${m % 60}m`;
  return `${m}m`;
}

export default function WorkoutDetailPage() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();

  const { data: session, isLoading } = useQuery({
    queryKey: ['workout', id],
    queryFn: () => workoutsApi.get(Number(id)),
    enabled: !!id,
  });

  if (isLoading) {
    return (
      <div className="p-6">
        <div className="space-y-4">
          <div className="h-8 w-48 bg-slate-800 rounded animate-pulse" />
          <div className="h-32 bg-slate-800 rounded-xl animate-pulse" />
        </div>
      </div>
    );
  }

  if (!session) return null;

  const prSets = session.exercises.flatMap((we) => we.sets.filter((s) => s.is_pr));

  return (
    <div className="p-6 space-y-6 max-w-2xl">
      {/* Back */}
      <button
        onClick={() => navigate('/workouts')}
        className="flex items-center gap-2 text-slate-400 hover:text-white transition-colors text-sm"
      >
        <ArrowLeft className="w-4 h-4" />
        Back to Workouts
      </button>

      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-white">{session.name}</h1>
        <p className="text-slate-400 text-sm mt-1">
          {format(new Date(session.started_at), 'EEEE, MMMM d yyyy • h:mm a')}
        </p>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
        {[
          { icon: Clock, label: 'Duration', value: formatDuration(session.duration_seconds) },
          { icon: BarChart3, label: 'Volume', value: `${Math.round(session.total_volume_kg)} kg` },
          { icon: BarChart3, label: 'Sets', value: String(session.total_sets) },
          { icon: Flame, label: 'Calories', value: session.calories_burned ? `${session.calories_burned} kcal` : '—' },
        ].map(({ icon: Icon, label, value }) => (
          <div key={label} className="bg-slate-800 border border-slate-700 rounded-xl p-3 text-center">
            <Icon className="w-5 h-5 text-violet-400 mx-auto mb-1" />
            <p className="text-xl font-bold text-white">{value}</p>
            <p className="text-slate-500 text-xs mt-0.5">{label}</p>
          </div>
        ))}
      </div>

      {/* PRs */}
      {prSets.length > 0 && (
        <div className="bg-amber-500/10 border border-amber-500/30 rounded-xl p-4">
          <div className="flex items-center gap-2 mb-3">
            <Trophy className="w-5 h-5 text-amber-400" />
            <h3 className="font-semibold text-amber-300">Personal Records 🎉</h3>
          </div>
          <div className="space-y-1">
            {prSets.map((s) => (
              <p key={s.id} className="text-amber-200 text-sm">
                {s.weight_kg} kg × {s.reps} reps
              </p>
            ))}
          </div>
        </div>
      )}

      {/* Exercises */}
      <div className="space-y-4">
        <h2 className="text-lg font-semibold text-white">Exercises</h2>
        {session.exercises.map((we) => (
          <div key={we.id} className="bg-slate-800 border border-slate-700 rounded-xl p-4">
            <h3 className="font-semibold text-white mb-3">Exercise #{we.exercise_order}</h3>
            <div className="space-y-2">
              <div className="grid grid-cols-4 text-xs text-slate-500 px-1">
                <span>Set</span>
                <span>Type</span>
                <span>Weight</span>
                <span>Reps</span>
              </div>
              {we.sets.filter((s) => s.completed).map((ws) => (
                <div key={ws.id} className="grid grid-cols-4 text-sm text-slate-300 px-1">
                  <span>{ws.set_number}</span>
                  <span className="capitalize text-slate-400">{ws.set_type}</span>
                  <span>{ws.weight_kg ?? '—'} kg</span>
                  <span className="flex items-center gap-1">
                    {ws.reps}
                    {ws.is_pr && <span className="text-[10px] font-bold text-amber-400">PR</span>}
                  </span>
                </div>
              ))}
            </div>
          </div>
        ))}
      </div>

      {/* Notes */}
      {session.notes && (
        <div className="bg-slate-800 border border-slate-700 rounded-xl p-4">
          <h3 className="font-semibold text-white mb-2">Notes</h3>
          <p className="text-slate-400 text-sm whitespace-pre-wrap">{session.notes}</p>
        </div>
      )}
    </div>
  );
}

import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useNavigate } from 'react-router-dom';
import { Plus, Clock, BarChart3, ChevronRight, Dumbbell } from 'lucide-react';
import { workoutsApi } from '@/api/workouts';
import { useWorkoutStore } from '@/stores/workoutStore';
import { formatDistanceToNow } from 'date-fns';

function formatDuration(seconds: number | null): string {
  if (!seconds) return '—';
  const m = Math.floor(seconds / 60);
  const h = Math.floor(m / 60);
  if (h > 0) return `${h}h ${m % 60}m`;
  return `${m}m`;
}

export default function WorkoutsPage() {
  const navigate = useNavigate();
  const qc = useQueryClient();
  const { setActiveSession, activeSession } = useWorkoutStore();
  const [page, setPage] = useState(1);
  const [workoutName, setWorkoutName] = useState('');
  const [showStart, setShowStart] = useState(false);

  const { data, isLoading } = useQuery({
    queryKey: ['workouts', page],
    queryFn: () => workoutsApi.list(page, 10, 'finished'),
  });

  const startMutation = useMutation({
    mutationFn: () => workoutsApi.start(workoutName || 'Workout'),
    onSuccess: (session) => {
      setActiveSession(session);
      navigate('/workouts/active');
    },
  });

  return (
    <div className="p-6 space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-white">Workouts</h1>
          <p className="text-slate-400 text-sm mt-1">Track and log your training sessions</p>
        </div>
        {activeSession ? (
          <button
            onClick={() => navigate('/workouts/active')}
            className="px-4 py-2 bg-emerald-600 hover:bg-emerald-500 text-white rounded-lg font-medium text-sm transition-colors animate-pulse"
          >
            Resume Active
          </button>
        ) : (
          <button
            onClick={() => setShowStart(true)}
            className="px-4 py-2 bg-violet-600 hover:bg-violet-500 text-white rounded-lg font-medium text-sm transition-colors flex items-center gap-2"
          >
            <Plus className="w-4 h-4" />
            New Workout
          </button>
        )}
      </div>

      {/* Start workout modal */}
      {showStart && (
        <div className="fixed inset-0 bg-black/60 flex items-center justify-center z-50 p-4">
          <div className="bg-slate-800 border border-slate-700 rounded-2xl p-6 w-full max-w-sm space-y-4">
            <h2 className="text-lg font-bold text-white">Start Workout</h2>
            <input
              type="text"
              value={workoutName}
              onChange={(e) => setWorkoutName(e.target.value)}
              placeholder="Workout name (optional)"
              autoFocus
              onKeyDown={(e) => e.key === 'Enter' && startMutation.mutate()}
              className="w-full px-4 py-2.5 bg-slate-700 border border-slate-600 rounded-lg text-white placeholder-slate-500 focus:outline-none focus:border-violet-500"
            />
            <div className="flex gap-3">
              <button
                onClick={() => setShowStart(false)}
                className="flex-1 py-2.5 border border-slate-600 rounded-lg text-slate-300 hover:text-white transition-colors"
              >
                Cancel
              </button>
              <button
                onClick={() => startMutation.mutate()}
                disabled={startMutation.isPending}
                className="flex-1 py-2.5 bg-violet-600 hover:bg-violet-500 text-white rounded-lg font-medium transition-colors disabled:opacity-50"
              >
                {startMutation.isPending ? 'Starting...' : 'Start'}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* History */}
      <div>
        <h2 className="text-lg font-semibold text-white mb-4">Workout History</h2>
        {isLoading ? (
          <div className="space-y-3">
            {Array.from({ length: 5 }).map((_, i) => (
              <div key={i} className="h-20 bg-slate-800 rounded-xl animate-pulse" />
            ))}
          </div>
        ) : data?.items.length === 0 ? (
          <div className="flex flex-col items-center justify-center py-16 text-slate-500">
            <Dumbbell className="w-12 h-12 mb-4 opacity-40" />
            <p className="text-sm">No workouts yet. Start your first one!</p>
          </div>
        ) : (
          <div className="space-y-3">
            {data?.items.map((session) => (
              <button
                key={session.id}
                onClick={() => navigate(`/workouts/${session.id}`)}
                className="w-full bg-slate-800 border border-slate-700 hover:border-violet-500 rounded-xl p-4 flex items-center gap-4 text-left transition-colors"
              >
                <div className="w-10 h-10 rounded-lg bg-violet-500/20 flex items-center justify-center flex-shrink-0">
                  <Dumbbell className="w-5 h-5 text-violet-400" />
                </div>
                <div className="flex-1 min-w-0">
                  <p className="font-semibold text-white truncate">{session.name}</p>
                  <p className="text-slate-400 text-sm mt-0.5">
                    {formatDistanceToNow(new Date(session.started_at), { addSuffix: true })}
                  </p>
                </div>
                <div className="text-right flex-shrink-0">
                  <div className="flex items-center gap-3 text-slate-400 text-sm">
                    <span className="flex items-center gap-1">
                      <Clock className="w-3.5 h-3.5" />
                      {formatDuration(session.duration_seconds)}
                    </span>
                    <span className="flex items-center gap-1">
                      <BarChart3 className="w-3.5 h-3.5" />
                      {Math.round(session.total_volume_kg)}kg
                    </span>
                  </div>
                </div>
                <ChevronRight className="w-4 h-4 text-slate-600" />
              </button>
            ))}
          </div>
        )}

        {data && data.total > data.per_page && (
          <div className="flex items-center gap-3 justify-center mt-6">
            <button disabled={page === 1} onClick={() => setPage(p => p - 1)}
              className="px-4 py-2 bg-slate-800 border border-slate-700 rounded-lg text-white disabled:opacity-40">
              Prev
            </button>
            <span className="text-slate-400 text-sm">Page {page} of {Math.ceil(data.total / data.per_page)}</span>
            <button disabled={page >= Math.ceil(data.total / data.per_page)} onClick={() => setPage(p => p + 1)}
              className="px-4 py-2 bg-slate-800 border border-slate-700 rounded-lg text-white disabled:opacity-40">
              Next
            </button>
          </div>
        )}
      </div>
    </div>
  );
}

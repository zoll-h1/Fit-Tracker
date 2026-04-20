import { useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { ArrowLeft, Clock, BarChart3, Flame, Trophy, Pencil, Trash2 } from 'lucide-react';
import { workoutsApi } from '@/api/workouts';
import { format } from 'date-fns';
import SaveAsTemplateButton from '@/components/workouts/SaveAsTemplateButton';

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
  const queryClient = useQueryClient();

  const [showEdit, setShowEdit] = useState(false);
  const [editName, setEditName] = useState('');
  const [editNotes, setEditNotes] = useState('');

  const { data: session, isLoading } = useQuery({
    queryKey: ['workout', id],
    queryFn: () => workoutsApi.get(Number(id)),
    enabled: !!id,
  });

  const deleteMutation = useMutation({
    mutationFn: () => workoutsApi.delete(Number(id)),
    onSuccess: () => navigate('/workouts'),
  });

  const updateMutation = useMutation({
    mutationFn: (data: { name?: string; notes?: string }) =>
      workoutsApi.update(Number(id), data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['workout', id] });
      setShowEdit(false);
    },
  });

  const openEdit = () => {
    setEditName(session?.name ?? '');
    setEditNotes(session?.notes ?? '');
    setShowEdit(true);
  };

  const handleDelete = () => {
    if (window.confirm('Delete this workout? This cannot be undone.')) {
      deleteMutation.mutate();
    }
  };

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
      <div className="flex items-start justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-white">{session.name}</h1>
          <p className="text-slate-400 text-sm mt-1">
            {format(new Date(session.started_at), 'EEEE, MMMM d yyyy • h:mm a')}
          </p>
        </div>
        <div className="flex items-center gap-2 flex-shrink-0">
          <button
            onClick={openEdit}
            className="p-2 rounded-lg bg-slate-800 border border-slate-700 text-slate-400 hover:text-white hover:border-slate-500 transition-colors"
            title="Edit workout"
          >
            <Pencil className="w-4 h-4" />
          </button>
          {session.status === 'finished' && (
            <button
              onClick={handleDelete}
              disabled={deleteMutation.isPending}
              className="p-2 rounded-lg bg-slate-800 border border-slate-700 text-red-400 hover:text-red-300 hover:border-red-500/50 transition-colors disabled:opacity-50"
              title="Delete workout"
            >
              <Trash2 className="w-4 h-4" />
            </button>
          )}
        </div>
      </div>

      {/* Edit Modal */}
      {showEdit && (
        <div className="fixed inset-0 bg-black/60 flex items-center justify-center z-50 p-4">
          <div className="bg-slate-800 border border-slate-700 rounded-2xl p-6 w-full max-w-sm space-y-4">
            <h2 className="text-lg font-bold text-white">Edit Workout</h2>
            <div className="space-y-3">
              <input
                type="text"
                value={editName}
                onChange={(e) => setEditName(e.target.value)}
                placeholder="Workout name"
                autoFocus
                className="w-full px-4 py-2.5 bg-slate-700 border border-slate-600 rounded-lg text-white placeholder-slate-500 focus:outline-none focus:border-violet-500"
              />
              <textarea
                value={editNotes}
                onChange={(e) => setEditNotes(e.target.value)}
                placeholder="Notes (optional)"
                rows={3}
                className="w-full px-4 py-2.5 bg-slate-700 border border-slate-600 rounded-lg text-white placeholder-slate-500 focus:outline-none focus:border-violet-500 resize-none"
              />
            </div>
            <div className="flex gap-3">
              <button
                onClick={() => setShowEdit(false)}
                className="flex-1 py-2.5 border border-slate-600 rounded-lg text-slate-300 hover:text-white transition-colors"
              >
                Cancel
              </button>
              <button
                onClick={() => updateMutation.mutate({ name: editName, notes: editNotes })}
                disabled={updateMutation.isPending}
                className="flex-1 py-2.5 bg-violet-600 hover:bg-violet-500 text-white rounded-lg font-medium transition-colors disabled:opacity-50"
              >
                {updateMutation.isPending ? 'Saving...' : 'Save'}
              </button>
            </div>
          </div>
        </div>
      )}

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
          <div
            key={we.id}
            className={`bg-slate-800 border rounded-xl p-4 ${
              we.superset_group != null ? 'border-amber-500/40' : 'border-slate-700'
            }`}
          >
            <div className="flex items-center gap-2 mb-3">
              <h3 className="font-semibold text-white">Exercise #{we.exercise_order}</h3>
              {we.superset_group != null && (
                <span className="text-[10px] font-bold text-amber-400 bg-amber-400/10 border border-amber-400/20 px-1.5 py-0.5 rounded">
                  Superset {we.superset_group}
                </span>
              )}
            </div>
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

      {/* Save as Template */}
      {(session.status === 'finished' || session.status === 'completed') && (
        <div>
          <SaveAsTemplateButton workoutId={session.id} />
        </div>
      )}
    </div>
  );
}

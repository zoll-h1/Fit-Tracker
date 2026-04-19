import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { Plus, Play, Edit2, Trash2, Clock, Dumbbell, BarChart3, X, Search } from 'lucide-react';
import { templatesApi, type Template, type TemplateCreate } from '@/api/templates';
import { exercisesApi, type Exercise } from '@/api/exercises';

// ─── CreateTemplateModal ────────────────────────────────────────────────────

interface ExerciseRow {
  exercise_library_id: number;
  exercise_name: string;
  exercise_order: number;
  target_sets: string;
  target_reps: string;
  rest_seconds: string;
}

function CreateTemplateModal({ onClose }: { onClose: () => void }) {
  const qc = useQueryClient();
  const [name, setName] = useState('');
  const [description, setDescription] = useState('');
  const [isPublic, setIsPublic] = useState(false);
  const [durationMin, setDurationMin] = useState('');
  const [exercises, setExercises] = useState<ExerciseRow[]>([]);
  const [search, setSearch] = useState('');
  const [showSearch, setShowSearch] = useState(false);

  const { data: searchResults } = useQuery({
    queryKey: ['exercises', 'search', search],
    queryFn: () => exercisesApi.list({ search, per_page: 10 }),
    enabled: search.length >= 2,
  });

  const createMutation = useMutation({
    mutationFn: (data: TemplateCreate) => templatesApi.create(data),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['templates'] });
      onClose();
    },
  });

  const addExercise = (ex: Exercise) => {
    setExercises(prev => [
      ...prev,
      {
        exercise_library_id: ex.id,
        exercise_name: ex.name,
        exercise_order: prev.length + 1,
        target_sets: '3',
        target_reps: '10',
        rest_seconds: '60',
      },
    ]);
    setSearch('');
    setShowSearch(false);
  };

  const removeExercise = (idx: number) => {
    setExercises(prev => prev.filter((_, i) => i !== idx).map((e, i) => ({ ...e, exercise_order: i + 1 })));
  };

  const updateExercise = (idx: number, field: keyof ExerciseRow, value: string) => {
    setExercises(prev => prev.map((e, i) => (i === idx ? { ...e, [field]: value } : e)));
  };

  const handleSubmit = () => {
    if (!name.trim()) return;
    createMutation.mutate({
      name: name.trim(),
      description: description || undefined,
      is_public: isPublic,
      estimated_duration_min: durationMin ? Number(durationMin) : undefined,
      exercises: exercises.map(e => ({
        exercise_library_id: e.exercise_library_id,
        exercise_order: e.exercise_order,
        target_sets: e.target_sets ? Number(e.target_sets) : undefined,
        target_reps: e.target_reps ? Number(e.target_reps) : undefined,
        rest_seconds: e.rest_seconds ? Number(e.rest_seconds) : 60,
      })),
    });
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 p-4">
      <div className="bg-slate-800 border border-slate-700 rounded-2xl w-full max-w-lg max-h-[90vh] overflow-y-auto">
        <div className="flex items-center justify-between p-5 border-b border-slate-700">
          <h2 className="text-lg font-bold text-white">New Template</h2>
          <button onClick={onClose} className="text-slate-400 hover:text-white">
            <X className="w-5 h-5" />
          </button>
        </div>

        <div className="p-5 space-y-4">
          <div>
            <label className="block text-sm text-slate-400 mb-1">Name *</label>
            <input
              className="w-full bg-slate-700 border border-slate-600 rounded-lg px-3 py-2 text-white text-sm focus:outline-none focus:border-violet-500"
              value={name}
              onChange={e => setName(e.target.value)}
              placeholder="e.g. Push Day"
            />
          </div>

          <div>
            <label className="block text-sm text-slate-400 mb-1">Description</label>
            <textarea
              className="w-full bg-slate-700 border border-slate-600 rounded-lg px-3 py-2 text-white text-sm focus:outline-none focus:border-violet-500 resize-none"
              rows={2}
              value={description}
              onChange={e => setDescription(e.target.value)}
              placeholder="Optional description"
            />
          </div>

          <div className="flex gap-4">
            <div className="flex-1">
              <label className="block text-sm text-slate-400 mb-1">Est. Duration (min)</label>
              <input
                type="number"
                className="w-full bg-slate-700 border border-slate-600 rounded-lg px-3 py-2 text-white text-sm focus:outline-none focus:border-violet-500"
                value={durationMin}
                onChange={e => setDurationMin(e.target.value)}
                placeholder="60"
              />
            </div>
            <div className="flex items-end pb-1">
              <label className="flex items-center gap-2 cursor-pointer">
                <div
                  onClick={() => setIsPublic(p => !p)}
                  className={`w-10 h-6 rounded-full transition-colors relative cursor-pointer ${isPublic ? 'bg-violet-600' : 'bg-slate-600'}`}
                >
                  <span className={`absolute top-1 w-4 h-4 bg-white rounded-full transition-all ${isPublic ? 'left-5' : 'left-1'}`} />
                </div>
                <span className="text-sm text-slate-300">Public</span>
              </label>
            </div>
          </div>

          {/* Exercises */}
          <div>
            <div className="flex items-center justify-between mb-2">
              <label className="text-sm text-slate-400">Exercises</label>
              <button
                onClick={() => setShowSearch(s => !s)}
                className="flex items-center gap-1 text-xs text-violet-400 hover:text-violet-300"
              >
                <Plus className="w-3 h-3" />
                Add
              </button>
            </div>

            {showSearch && (
              <div className="mb-3">
                <div className="relative">
                  <Search className="absolute left-3 top-2.5 w-4 h-4 text-slate-400" />
                  <input
                    className="w-full bg-slate-700 border border-slate-600 rounded-lg pl-9 pr-3 py-2 text-white text-sm focus:outline-none focus:border-violet-500"
                    value={search}
                    onChange={e => setSearch(e.target.value)}
                    placeholder="Search exercises..."
                    autoFocus
                  />
                </div>
                {searchResults && searchResults.items.length > 0 && (
                  <div className="mt-1 bg-slate-700 border border-slate-600 rounded-lg overflow-hidden max-h-40 overflow-y-auto">
                    {searchResults.items.map(ex => (
                      <button
                        key={ex.id}
                        onClick={() => addExercise(ex)}
                        className="w-full text-left px-3 py-2 text-sm text-white hover:bg-slate-600 border-b border-slate-600 last:border-0"
                      >
                        <span className="font-medium">{ex.name}</span>
                        <span className="text-slate-400 ml-2 text-xs">{ex.category}</span>
                      </button>
                    ))}
                  </div>
                )}
              </div>
            )}

            {exercises.length === 0 ? (
              <p className="text-slate-500 text-sm text-center py-2">No exercises added yet</p>
            ) : (
              <div className="space-y-2">
                {exercises.map((ex, idx) => (
                  <div key={idx} className="bg-slate-700/50 border border-slate-600 rounded-lg p-3">
                    <div className="flex items-center justify-between mb-2">
                      <span className="text-sm font-medium text-white">{ex.exercise_name}</span>
                      <button onClick={() => removeExercise(idx)} className="text-slate-500 hover:text-red-400">
                        <X className="w-4 h-4" />
                      </button>
                    </div>
                    <div className="grid grid-cols-3 gap-2">
                      {[
                        { label: 'Sets', field: 'target_sets' as const },
                        { label: 'Reps', field: 'target_reps' as const },
                        { label: 'Rest (s)', field: 'rest_seconds' as const },
                      ].map(({ label, field }) => (
                        <div key={field}>
                          <label className="block text-xs text-slate-500 mb-0.5">{label}</label>
                          <input
                            type="number"
                            className="w-full bg-slate-600 border border-slate-500 rounded px-2 py-1 text-white text-xs focus:outline-none focus:border-violet-500"
                            value={ex[field]}
                            onChange={e => updateExercise(idx, field, e.target.value)}
                          />
                        </div>
                      ))}
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>

        <div className="flex gap-3 p-5 border-t border-slate-700">
          <button
            onClick={onClose}
            className="flex-1 bg-slate-700 hover:bg-slate-600 text-white rounded-lg py-2 text-sm font-medium transition-colors"
          >
            Cancel
          </button>
          <button
            onClick={handleSubmit}
            disabled={!name.trim() || createMutation.isPending}
            className="flex-1 bg-violet-600 hover:bg-violet-500 disabled:opacity-50 text-white rounded-lg py-2 text-sm font-medium transition-colors"
          >
            {createMutation.isPending ? 'Creating…' : 'Create Template'}
          </button>
        </div>
      </div>
    </div>
  );
}

// ─── EditTemplateModal ───────────────────────────────────────────────────────

function EditTemplateModal({ template, onClose }: { template: Template; onClose: () => void }) {
  const qc = useQueryClient();
  const [name, setName] = useState(template.name);
  const [description, setDescription] = useState(template.description ?? '');
  const [isPublic, setIsPublic] = useState(template.is_public);
  const [durationMin, setDurationMin] = useState(String(template.estimated_duration_min ?? ''));

  const updateMutation = useMutation({
    mutationFn: () =>
      templatesApi.update(template.id, {
        name: name.trim() || undefined,
        description: description || undefined,
        is_public: isPublic,
        estimated_duration_min: durationMin ? Number(durationMin) : undefined,
      }),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['templates'] });
      onClose();
    },
  });

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 p-4">
      <div className="bg-slate-800 border border-slate-700 rounded-2xl w-full max-w-md">
        <div className="flex items-center justify-between p-5 border-b border-slate-700">
          <h2 className="text-lg font-bold text-white">Edit Template</h2>
          <button onClick={onClose} className="text-slate-400 hover:text-white">
            <X className="w-5 h-5" />
          </button>
        </div>

        <div className="p-5 space-y-4">
          <div>
            <label className="block text-sm text-slate-400 mb-1">Name</label>
            <input
              className="w-full bg-slate-700 border border-slate-600 rounded-lg px-3 py-2 text-white text-sm focus:outline-none focus:border-violet-500"
              value={name}
              onChange={e => setName(e.target.value)}
            />
          </div>
          <div>
            <label className="block text-sm text-slate-400 mb-1">Description</label>
            <textarea
              className="w-full bg-slate-700 border border-slate-600 rounded-lg px-3 py-2 text-white text-sm focus:outline-none focus:border-violet-500 resize-none"
              rows={2}
              value={description}
              onChange={e => setDescription(e.target.value)}
            />
          </div>
          <div className="flex gap-4">
            <div className="flex-1">
              <label className="block text-sm text-slate-400 mb-1">Est. Duration (min)</label>
              <input
                type="number"
                className="w-full bg-slate-700 border border-slate-600 rounded-lg px-3 py-2 text-white text-sm focus:outline-none focus:border-violet-500"
                value={durationMin}
                onChange={e => setDurationMin(e.target.value)}
              />
            </div>
            <div className="flex items-end pb-1">
              <label className="flex items-center gap-2 cursor-pointer">
                <div
                  onClick={() => setIsPublic(p => !p)}
                  className={`w-10 h-6 rounded-full transition-colors relative cursor-pointer ${isPublic ? 'bg-violet-600' : 'bg-slate-600'}`}
                >
                  <span className={`absolute top-1 w-4 h-4 bg-white rounded-full transition-all ${isPublic ? 'left-5' : 'left-1'}`} />
                </div>
                <span className="text-sm text-slate-300">Public</span>
              </label>
            </div>
          </div>
        </div>

        <div className="flex gap-3 p-5 border-t border-slate-700">
          <button
            onClick={onClose}
            className="flex-1 bg-slate-700 hover:bg-slate-600 text-white rounded-lg py-2 text-sm font-medium transition-colors"
          >
            Cancel
          </button>
          <button
            onClick={() => updateMutation.mutate()}
            disabled={updateMutation.isPending}
            className="flex-1 bg-violet-600 hover:bg-violet-500 disabled:opacity-50 text-white rounded-lg py-2 text-sm font-medium transition-colors"
          >
            {updateMutation.isPending ? 'Saving…' : 'Save Changes'}
          </button>
        </div>
      </div>
    </div>
  );
}

// ─── TemplateCard ────────────────────────────────────────────────────────────

function TemplateCard({
  template,
  isOwner,
  onEdit,
  onDelete,
}: {
  template: Template;
  isOwner: boolean;
  onEdit: () => void;
  onDelete: () => void;
}) {
  const navigate = useNavigate();
  const qc = useQueryClient();
  const [starting, setStarting] = useState(false);
  const [toast, setToast] = useState('');

  const handleStart = async () => {
    setStarting(true);
    try {
      await templatesApi.start(template.id);
      qc.invalidateQueries({ queryKey: ['workouts'] });
      navigate('/workouts');
    } catch {
      setToast('Failed to start workout');
      setTimeout(() => setToast(''), 3000);
    } finally {
      setStarting(false);
    }
  };

  return (
    <div className="bg-slate-800 border border-slate-700 rounded-xl p-4 flex flex-col gap-3">
      {toast && (
        <div className="text-red-400 text-xs bg-red-500/10 border border-red-500/20 rounded px-2 py-1">
          {toast}
        </div>
      )}
      <div>
        <div className="flex items-start justify-between gap-2">
          <h3 className="font-semibold text-white text-sm leading-tight">{template.name}</h3>
          {template.is_public && (
            <span className="text-[10px] bg-violet-500/20 text-violet-300 border border-violet-500/30 rounded px-1.5 py-0.5 shrink-0">
              Public
            </span>
          )}
        </div>
        {template.description && (
          <p className="text-slate-400 text-xs mt-1 line-clamp-2">{template.description}</p>
        )}
      </div>

      <div className="flex items-center gap-3 text-slate-400 text-xs">
        <span className="flex items-center gap-1">
          <Dumbbell className="w-3.5 h-3.5" />
          {template.exercise_count} exercises
        </span>
        {template.estimated_duration_min && (
          <span className="flex items-center gap-1">
            <Clock className="w-3.5 h-3.5" />
            {template.estimated_duration_min}m
          </span>
        )}
        <span className="flex items-center gap-1">
          <BarChart3 className="w-3.5 h-3.5" />
          {template.times_used}× used
        </span>
      </div>

      <div className="flex gap-2 mt-auto">
        <button
          onClick={handleStart}
          disabled={starting}
          className="flex-1 flex items-center justify-center gap-1.5 bg-violet-600 hover:bg-violet-500 disabled:opacity-50 text-white rounded-lg py-1.5 text-xs font-medium transition-colors"
        >
          <Play className="w-3.5 h-3.5" />
          {starting ? 'Starting…' : 'Start Workout'}
        </button>
        {isOwner && (
          <>
            <button
              onClick={onEdit}
              className="p-1.5 bg-slate-700 hover:bg-slate-600 text-slate-300 rounded-lg transition-colors"
            >
              <Edit2 className="w-4 h-4" />
            </button>
            <button
              onClick={onDelete}
              className="p-1.5 bg-slate-700 hover:bg-red-500/20 text-slate-300 hover:text-red-400 rounded-lg transition-colors"
            >
              <Trash2 className="w-4 h-4" />
            </button>
          </>
        )}
      </div>
    </div>
  );
}

// ─── TemplatesPage ───────────────────────────────────────────────────────────

export default function TemplatesPage() {
  const qc = useQueryClient();
  const [tab, setTab] = useState<'mine' | 'public'>('mine');
  const [showCreate, setShowCreate] = useState(false);
  const [editing, setEditing] = useState<Template | null>(null);

  const { data: myTemplates = [], isLoading: loadingMine } = useQuery({
    queryKey: ['templates', 'mine'],
    queryFn: () => templatesApi.list({ mine: true, public: false }),
    enabled: tab === 'mine',
  });

  const { data: publicTemplates = [], isLoading: loadingPublic } = useQuery({
    queryKey: ['templates', 'public'],
    queryFn: () => templatesApi.list({ mine: false, public: true }),
    enabled: tab === 'public',
  });

  const deleteMutation = useMutation({
    mutationFn: (id: number) => templatesApi.delete(id),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['templates'] }),
  });

  const templates = tab === 'mine' ? myTemplates : publicTemplates;
  const loading = tab === 'mine' ? loadingMine : loadingPublic;

  return (
    <div className="p-6 space-y-6 max-w-4xl">
      {showCreate && <CreateTemplateModal onClose={() => setShowCreate(false)} />}
      {editing && <EditTemplateModal template={editing} onClose={() => setEditing(null)} />}

      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-white">Workout Templates</h1>
          <p className="text-slate-400 text-sm mt-1">Reusable workout plans to save time</p>
        </div>
        <button
          onClick={() => setShowCreate(true)}
          className="flex items-center gap-2 bg-violet-600 hover:bg-violet-500 text-white px-4 py-2 rounded-lg text-sm font-medium transition-colors"
        >
          <Plus className="w-4 h-4" />
          New Template
        </button>
      </div>

      {/* Tabs */}
      <div className="flex gap-1 bg-slate-800 border border-slate-700 rounded-xl p-1 w-fit">
        {(['mine', 'public'] as const).map(t => (
          <button
            key={t}
            onClick={() => setTab(t)}
            className={`px-4 py-1.5 rounded-lg text-sm font-medium transition-colors ${
              tab === t ? 'bg-violet-600 text-white' : 'text-slate-400 hover:text-white'
            }`}
          >
            {t === 'mine' ? 'My Templates' : 'Public Templates'}
          </button>
        ))}
      </div>

      {/* Grid */}
      {loading ? (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {[1, 2, 3].map(i => (
            <div key={i} className="bg-slate-800 border border-slate-700 rounded-xl h-40 animate-pulse" />
          ))}
        </div>
      ) : templates.length === 0 ? (
        <div className="text-center py-16 text-slate-500">
          <Dumbbell className="w-12 h-12 mx-auto mb-3 opacity-30" />
          <p className="text-lg font-medium">
            {tab === 'mine' ? 'No templates yet' : 'No public templates'}
          </p>
          {tab === 'mine' && (
            <p className="text-sm mt-1">
              Create your first template to speed up your workouts
            </p>
          )}
        </div>
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {templates.map(t => (
            <TemplateCard
              key={t.id}
              template={t}
              isOwner={tab === 'mine'}
              onEdit={() => setEditing(t)}
              onDelete={() => {
                if (confirm(`Delete "${t.name}"?`)) {
                  deleteMutation.mutate(t.id);
                }
              }}
            />
          ))}
        </div>
      )}
    </div>
  );
}

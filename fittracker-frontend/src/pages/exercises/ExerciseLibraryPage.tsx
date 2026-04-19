import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { Search, Dumbbell, Plus, X } from 'lucide-react';
import { exercisesApi, type Exercise } from '@/api/exercises';

const CATEGORIES = ['strength', 'cardio', 'olympic', 'flexibility'];
const DIFFICULTIES = ['beginner', 'intermediate', 'advanced'];
const MUSCLE_GROUPS = ['chest', 'back', 'shoulders', 'biceps', 'triceps', 'legs', 'glutes', 'core', 'cardio'];

export default function ExerciseLibraryPage() {
  const [search, setSearch] = useState('');
  const [category, setCategory] = useState('');
  const [difficulty, setDifficulty] = useState('');
  const [page, setPage] = useState(1);
  const [showCustomModal, setShowCustomModal] = useState(false);
  const queryClient = useQueryClient();

  const { data, isLoading } = useQuery({
    queryKey: ['exercises', search, category, difficulty, page],
    queryFn: () =>
      exercisesApi.list({ search: search || undefined, category: category || undefined, difficulty: difficulty || undefined, page }),
    placeholderData: (prev) => prev,
  });

  const { data: customExercises = [] } = useQuery({
    queryKey: ['exercises', 'custom'],
    queryFn: () => exercisesApi.listCustom(),
  });

  return (
    <div className="p-6 space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-white">Exercise Library</h1>
          <p className="text-slate-400 text-sm mt-1">{data?.total ?? 0} exercises available</p>
        </div>
        <button
          onClick={() => setShowCustomModal(true)}
          className="flex items-center gap-2 px-4 py-2 bg-violet-600 hover:bg-violet-500 text-white rounded-lg text-sm font-medium transition-colors"
        >
          <Plus className="w-4 h-4" />
          Create Custom
        </button>
      </div>

      {/* Custom Exercises */}
      {customExercises.length > 0 && (
        <div className="space-y-3">
          <h2 className="text-lg font-semibold text-white">My Custom Exercises</h2>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
            {customExercises.map((ex) => (
              <ExerciseCard key={ex.id} exercise={ex} isCustom />
            ))}
          </div>
        </div>
      )}

      {/* Filters */}
      <div className="flex flex-wrap gap-3">
        <div className="relative flex-1 min-w-[200px]">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400 w-4 h-4" />
          <input
            type="text"
            placeholder="Search exercises..."
            value={search}
            onChange={(e) => { setSearch(e.target.value); setPage(1); }}
            className="w-full pl-9 pr-4 py-2 bg-slate-800 border border-slate-700 rounded-lg text-white placeholder-slate-500 focus:outline-none focus:border-violet-500"
          />
        </div>

        <select
          value={category}
          onChange={(e) => { setCategory(e.target.value); setPage(1); }}
          className="px-3 py-2 bg-slate-800 border border-slate-700 rounded-lg text-white focus:outline-none focus:border-violet-500"
        >
          <option value="">All Categories</option>
          {CATEGORIES.map((c) => (
            <option key={c} value={c}>{c.charAt(0).toUpperCase() + c.slice(1)}</option>
          ))}
        </select>

        <select
          value={difficulty}
          onChange={(e) => { setDifficulty(e.target.value); setPage(1); }}
          className="px-3 py-2 bg-slate-800 border border-slate-700 rounded-lg text-white focus:outline-none focus:border-violet-500"
        >
          <option value="">All Levels</option>
          {DIFFICULTIES.map((d) => (
            <option key={d} value={d}>{d.charAt(0).toUpperCase() + d.slice(1)}</option>
          ))}
        </select>
      </div>

      {/* Grid */}
      {isLoading ? (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
          {Array.from({ length: 8 }).map((_, i) => (
            <div key={i} className="h-36 bg-slate-800 rounded-xl animate-pulse" />
          ))}
        </div>
      ) : (
        <>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
            {data?.items.map((ex) => (
              <ExerciseCard key={ex.id} exercise={ex} />
            ))}
          </div>

          {/* Pagination */}
          {data && data.total > data.per_page && (
            <div className="flex items-center gap-3 justify-center">
              <button
                disabled={page === 1}
                onClick={() => setPage((p) => p - 1)}
                className="px-4 py-2 bg-slate-800 border border-slate-700 rounded-lg text-white disabled:opacity-40"
              >
                Prev
              </button>
              <span className="text-slate-400 text-sm">
                Page {page} of {Math.ceil(data.total / data.per_page)}
              </span>
              <button
                disabled={page >= Math.ceil(data.total / data.per_page)}
                onClick={() => setPage((p) => p + 1)}
                className="px-4 py-2 bg-slate-800 border border-slate-700 rounded-lg text-white disabled:opacity-40"
              >
                Next
              </button>
            </div>
          )}
        </>
      )}

      {/* Custom Exercise Modal */}
      {showCustomModal && (
        <CustomExerciseModal
          onClose={() => setShowCustomModal(false)}
          onCreated={() => {
            queryClient.invalidateQueries({ queryKey: ['exercises', 'custom'] });
            setShowCustomModal(false);
          }}
        />
      )}
    </div>
  );
}

function ExerciseCard({ exercise, isCustom = false }: { exercise: Exercise; isCustom?: boolean }) {
  const difficultyColor: Record<string, string> = {
    beginner: 'text-emerald-400',
    intermediate: 'text-amber-400',
    advanced: 'text-rose-400',
  };

  return (
    <div className={`bg-slate-800 border rounded-xl p-4 hover:border-violet-500 transition-colors ${isCustom ? 'border-violet-500/40' : 'border-slate-700'}`}>
      <div className="flex items-start justify-between mb-2">
        <div className="w-10 h-10 rounded-lg bg-violet-500/20 flex items-center justify-center">
          <Dumbbell className="w-5 h-5 text-violet-400" />
        </div>
        <div className="flex flex-col items-end gap-1">
          <span className={`text-xs font-medium ${difficultyColor[exercise.difficulty] ?? 'text-slate-400'}`}>
            {exercise.difficulty}
          </span>
          {isCustom && (
            <span className="text-[10px] bg-violet-500/20 text-violet-300 px-1.5 py-0.5 rounded font-medium">Custom</span>
          )}
        </div>
      </div>
      <h3 className="font-semibold text-white text-sm mt-2 line-clamp-2">{exercise.name}</h3>
      <p className="text-slate-500 text-xs mt-1 capitalize">{exercise.category}</p>
      {exercise.muscle_primary && (
        <p className="text-slate-400 text-xs mt-1 truncate">
          {exercise.muscle_primary.replace(/,/g, ' · ')}
        </p>
      )}
    </div>
  );
}

interface CustomExerciseModalProps {
  onClose: () => void;
  onCreated: () => void;
}

function CustomExerciseModal({ onClose, onCreated }: CustomExerciseModalProps) {
  const [name, setName] = useState('');
  const [muscle, setMuscle] = useState('');
  const [category, setCategory] = useState('strength');
  const [difficulty, setDifficulty] = useState('intermediate');
  const [description, setDescription] = useState('');
  const [videoUrl, setVideoUrl] = useState('');

  const createMutation = useMutation({
    mutationFn: () =>
      exercisesApi.createCustom({
        name,
        muscle_primary: muscle || undefined,
        category,
        difficulty,
        description: description || undefined,
        video_url: videoUrl || undefined,
      }),
    onSuccess: onCreated,
  });

  return (
    <div className="fixed inset-0 bg-black/60 flex items-center justify-center z-50 p-4">
      <div className="bg-slate-800 border border-slate-700 rounded-2xl p-6 w-full max-w-md space-y-4">
        <div className="flex items-center justify-between">
          <h2 className="text-lg font-bold text-white">Create Custom Exercise</h2>
          <button onClick={onClose} className="text-slate-400 hover:text-white">
            <X className="w-5 h-5" />
          </button>
        </div>

        <div className="space-y-3">
          <div>
            <label className="text-xs text-slate-400 block mb-1">Name *</label>
            <input
              type="text"
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder="Exercise name"
              className="w-full px-3 py-2 bg-slate-700 border border-slate-600 rounded-lg text-white placeholder-slate-500 focus:outline-none focus:border-violet-500 text-sm"
            />
          </div>

          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="text-xs text-slate-400 block mb-1">Muscle Group</label>
              <select
                value={muscle}
                onChange={(e) => setMuscle(e.target.value)}
                className="w-full px-3 py-2 bg-slate-700 border border-slate-600 rounded-lg text-white focus:outline-none focus:border-violet-500 text-sm"
              >
                <option value="">Select...</option>
                {MUSCLE_GROUPS.map((m) => (
                  <option key={m} value={m}>{m.charAt(0).toUpperCase() + m.slice(1)}</option>
                ))}
              </select>
            </div>
            <div>
              <label className="text-xs text-slate-400 block mb-1">Category</label>
              <select
                value={category}
                onChange={(e) => setCategory(e.target.value)}
                className="w-full px-3 py-2 bg-slate-700 border border-slate-600 rounded-lg text-white focus:outline-none focus:border-violet-500 text-sm"
              >
                {CATEGORIES.map((c) => (
                  <option key={c} value={c}>{c.charAt(0).toUpperCase() + c.slice(1)}</option>
                ))}
              </select>
            </div>
          </div>

          <div>
            <label className="text-xs text-slate-400 block mb-1">Difficulty</label>
            <select
              value={difficulty}
              onChange={(e) => setDifficulty(e.target.value)}
              className="w-full px-3 py-2 bg-slate-700 border border-slate-600 rounded-lg text-white focus:outline-none focus:border-violet-500 text-sm"
            >
              {DIFFICULTIES.map((d) => (
                <option key={d} value={d}>{d.charAt(0).toUpperCase() + d.slice(1)}</option>
              ))}
            </select>
          </div>

          <div>
            <label className="text-xs text-slate-400 block mb-1">Description (optional)</label>
            <textarea
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              placeholder="Describe the exercise..."
              rows={2}
              className="w-full px-3 py-2 bg-slate-700 border border-slate-600 rounded-lg text-white placeholder-slate-500 focus:outline-none focus:border-violet-500 text-sm resize-none"
            />
          </div>

          <div>
            <label className="text-xs text-slate-400 block mb-1">Video URL (optional)</label>
            <input
              type="url"
              value={videoUrl}
              onChange={(e) => setVideoUrl(e.target.value)}
              placeholder="https://..."
              className="w-full px-3 py-2 bg-slate-700 border border-slate-600 rounded-lg text-white placeholder-slate-500 focus:outline-none focus:border-violet-500 text-sm"
            />
          </div>
        </div>

        <div className="flex gap-3 pt-1">
          <button
            onClick={onClose}
            className="flex-1 py-2.5 border border-slate-600 rounded-lg text-slate-300 hover:text-white transition-colors text-sm"
          >
            Cancel
          </button>
          <button
            onClick={() => createMutation.mutate()}
            disabled={!name.trim() || createMutation.isPending}
            className="flex-1 py-2.5 bg-violet-600 hover:bg-violet-500 text-white rounded-lg font-medium transition-colors disabled:opacity-50 text-sm"
          >
            {createMutation.isPending ? 'Creating...' : 'Create Exercise'}
          </button>
        </div>
      </div>
    </div>
  );
}

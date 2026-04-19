import { useState, useEffect } from 'react';
import { Search, X } from 'lucide-react';
import { useQuery, useMutation } from '@tanstack/react-query';
import { exercisesApi, type Exercise } from '@/api/exercises';
import { workoutsApi, type WorkoutExercise } from '@/api/workouts';

interface AddExerciseModalProps {
  sessionId: number;
  currentCount: number;
  onAdd: (exercise: WorkoutExercise) => void;
  onClose: () => void;
}

export default function AddExerciseModal({ sessionId, currentCount, onAdd, onClose }: AddExerciseModalProps) {
  const [search, setSearch] = useState('');
  const [debouncedSearch, setDebouncedSearch] = useState('');

  useEffect(() => {
    const t = setTimeout(() => setDebouncedSearch(search), 300);
    return () => clearTimeout(t);
  }, [search]);

  const { data } = useQuery({
    queryKey: ['exercises-modal', debouncedSearch],
    queryFn: () => exercisesApi.list({ search: debouncedSearch || undefined, per_page: 30 }),
  });

  const addMutation = useMutation({
    mutationFn: (exercise: Exercise) =>
      workoutsApi.addExercise(sessionId, exercise.id, currentCount + 1),
    onSuccess: onAdd,
  });

  return (
    <div className="fixed inset-0 bg-black/70 flex items-end sm:items-center justify-center z-50 p-4">
      <div className="bg-slate-800 border border-slate-700 rounded-2xl w-full max-w-md max-h-[80vh] flex flex-col">
        {/* Header */}
        <div className="flex items-center justify-between p-4 border-b border-slate-700">
          <h2 className="text-lg font-bold text-white">Add Exercise</h2>
          <button onClick={onClose} className="text-slate-400 hover:text-white">
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Search */}
        <div className="p-4 border-b border-slate-700">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400 w-4 h-4" />
            <input
              autoFocus
              type="text"
              placeholder="Search exercises..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="w-full pl-9 pr-4 py-2 bg-slate-700 border border-slate-600 rounded-lg text-white placeholder-slate-500 focus:outline-none focus:border-violet-500"
            />
          </div>
        </div>

        {/* List */}
        <div className="overflow-y-auto flex-1 p-2">
          {data?.items.map((ex) => (
            <button
              key={ex.id}
              onClick={() => addMutation.mutate(ex)}
              disabled={addMutation.isPending}
              className="w-full text-left px-4 py-3 hover:bg-slate-700 rounded-xl transition-colors"
            >
              <p className="font-medium text-white text-sm">{ex.name}</p>
              <p className="text-slate-500 text-xs mt-0.5 capitalize">
                {ex.category} · {ex.muscle_primary?.replace(/,/g, ', ')}
              </p>
            </button>
          ))}
        </div>
      </div>
    </div>
  );
}

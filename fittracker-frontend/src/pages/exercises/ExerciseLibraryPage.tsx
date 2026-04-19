import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { Search, Filter, Dumbbell } from 'lucide-react';
import { exercisesApi, type Exercise } from '@/api/exercises';

const CATEGORIES = ['strength', 'cardio', 'olympic', 'flexibility'];
const DIFFICULTIES = ['beginner', 'intermediate', 'advanced'];

export default function ExerciseLibraryPage() {
  const [search, setSearch] = useState('');
  const [category, setCategory] = useState('');
  const [difficulty, setDifficulty] = useState('');
  const [page, setPage] = useState(1);

  const { data, isLoading } = useQuery({
    queryKey: ['exercises', search, category, difficulty, page],
    queryFn: () =>
      exercisesApi.list({ search: search || undefined, category: category || undefined, difficulty: difficulty || undefined, page }),
    placeholderData: (prev) => prev,
  });

  return (
    <div className="p-6 space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-white">Exercise Library</h1>
        <p className="text-slate-400 text-sm mt-1">{data?.total ?? 0} exercises available</p>
      </div>

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
    </div>
  );
}

function ExerciseCard({ exercise }: { exercise: Exercise }) {
  const difficultyColor: Record<string, string> = {
    beginner: 'text-emerald-400',
    intermediate: 'text-amber-400',
    advanced: 'text-rose-400',
  };

  return (
    <div className="bg-slate-800 border border-slate-700 rounded-xl p-4 hover:border-violet-500 transition-colors">
      <div className="flex items-start justify-between mb-2">
        <div className="w-10 h-10 rounded-lg bg-violet-500/20 flex items-center justify-center">
          <Dumbbell className="w-5 h-5 text-violet-400" />
        </div>
        <span className={`text-xs font-medium ${difficultyColor[exercise.difficulty] ?? 'text-slate-400'}`}>
          {exercise.difficulty}
        </span>
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

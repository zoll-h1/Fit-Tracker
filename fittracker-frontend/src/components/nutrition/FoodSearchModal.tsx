import { useState, useEffect, useCallback } from 'react';
import { useMutation } from '@tanstack/react-query';
import { Search, X, Plus } from 'lucide-react';
import { foodsApi, nutritionApi, type Food } from '@/api/nutrition';

type MealType = 'breakfast' | 'lunch' | 'dinner' | 'snack';

interface FoodSearchModalProps {
  mealType: MealType;
  logDate: string; // ISO date string
  onClose: () => void;
  onLogged: () => void;
}

export default function FoodSearchModal({ mealType, logDate, onClose, onLogged }: FoodSearchModalProps) {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState<Food[]>([]);
  const [selected, setSelected] = useState<Food | null>(null);
  const [grams, setGrams] = useState('100');
  const [searching, setSearching] = useState(false);

  // Debounced search
  const doSearch = useCallback(async (q: string) => {
    if (!q.trim()) { setResults([]); return; }
    setSearching(true);
    try {
      const res = await foodsApi.search(q);
      setResults(res.items);
    } finally {
      setSearching(false);
    }
  }, []);

  useEffect(() => {
    const id = setTimeout(() => doSearch(query), 350);
    return () => clearTimeout(id);
  }, [query, doSearch]);

  const servingG = parseFloat(grams) || 100;
  const factor = servingG / 100;
  const preview = selected
    ? {
        calories: Math.round((selected.calories_per_100g ?? 0) * factor),
        protein: +((selected.protein_g ?? 0) * factor).toFixed(1),
        carbs: +((selected.carbs_g ?? 0) * factor).toFixed(1),
        fat: +((selected.fat_g ?? 0) * factor).toFixed(1),
      }
    : null;

  const logMutation = useMutation({
    mutationFn: () => {
      // Send full ISO datetime (today at current time, or noon of the target date)
      // to avoid UTC-midnight timezone boundary issues
      const now = new Date();
      const todayStr = `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, '0')}-${String(now.getDate()).padStart(2, '0')}`;
      const loggedAt = logDate === todayStr
        ? now.toISOString()
        : `${logDate}T12:00:00.000Z`;
      return nutritionApi.logMeal(selected!.id, mealType, servingG, loggedAt);
    },
    onSuccess: onLogged,
  });

  return (
    <div className="fixed inset-0 bg-black/60 flex items-end sm:items-center justify-center z-50 p-4">
      <div className="bg-slate-800 border border-slate-700 rounded-2xl w-full max-w-lg max-h-[80vh] flex flex-col">
        {/* Header */}
        <div className="flex items-center justify-between px-5 py-4 border-b border-slate-700">
          <h2 className="font-bold text-white">
            Add to <span className="capitalize text-violet-400">{mealType}</span>
          </h2>
          <button onClick={onClose} className="text-slate-400 hover:text-white"><X className="w-5 h-5" /></button>
        </div>

        {/* Search */}
        <div className="px-5 py-3 border-b border-slate-700">
          <div className="relative">
            <Search className="absolute left-3 top-2.5 w-4 h-4 text-slate-400" />
            <input
              autoFocus
              placeholder="Search foods…"
              value={query}
              onChange={e => { setQuery(e.target.value); setSelected(null); }}
              className="w-full pl-9 pr-3 py-2 bg-slate-700 border border-slate-600 rounded-lg text-white text-sm focus:outline-none focus:border-violet-500"
            />
          </div>
        </div>

        {/* Results / selected */}
        <div className="flex-1 overflow-y-auto">
          {!selected ? (
            <div>
              {searching && (
                <div className="flex justify-center py-6">
                  <div className="w-5 h-5 border-2 border-violet-500 border-t-transparent rounded-full animate-spin" />
                </div>
              )}
              {results.map(food => (
                <button
                  key={food.id}
                  onClick={() => setSelected(food)}
                  className="w-full flex items-center justify-between px-5 py-3 hover:bg-slate-700 text-left transition-colors"
                >
                  <div>
                    <p className="text-white text-sm font-medium">{food.name}</p>
                    <p className="text-slate-500 text-xs">{food.brand ?? 'Generic'}</p>
                  </div>
                  <div className="text-right text-xs text-slate-400">
                    <p>{food.calories_per_100g} kcal</p>
                    <p className="text-slate-500">per 100g</p>
                  </div>
                </button>
              ))}
              {!searching && query && results.length === 0 && (
                <p className="text-center text-slate-500 py-6 text-sm">No foods found</p>
              )}
              {!query && (
                <p className="text-center text-slate-500 py-6 text-sm">Type to search for foods</p>
              )}
            </div>
          ) : (
            <div className="p-5 space-y-4">
              <div className="flex items-start justify-between">
                <div>
                  <p className="font-semibold text-white">{selected.name}</p>
                  <p className="text-slate-400 text-xs">{selected.brand ?? 'Generic'}</p>
                </div>
                <button onClick={() => setSelected(null)} className="text-slate-400 hover:text-white text-sm">Change</button>
              </div>

              <div>
                <label className="text-xs text-slate-400 block mb-1">Serving size (grams)</label>
                <input
                  type="number"
                  min="1"
                  value={grams}
                  onChange={e => setGrams(e.target.value)}
                  className="w-32 px-3 py-2 bg-slate-700 border border-slate-600 rounded-lg text-white text-sm focus:outline-none focus:border-violet-500"
                />
              </div>

              {preview && (
                <div className="grid grid-cols-4 gap-2">
                  {[
                    { label: 'Calories', value: `${preview.calories}` },
                    { label: 'Protein', value: `${preview.protein}g` },
                    { label: 'Carbs', value: `${preview.carbs}g` },
                    { label: 'Fat', value: `${preview.fat}g` },
                  ].map(({ label, value }) => (
                    <div key={label} className="bg-slate-700 rounded-lg p-2.5 text-center">
                      <p className="text-white font-semibold text-sm">{value}</p>
                      <p className="text-slate-500 text-[10px] mt-0.5">{label}</p>
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}
        </div>

        {/* Footer */}
        {selected && (
          <div className="px-5 py-4 border-t border-slate-700">
            <button
              onClick={() => logMutation.mutate()}
              disabled={logMutation.isPending}
              className="w-full py-3 bg-violet-600 hover:bg-violet-500 text-white rounded-xl font-semibold flex items-center justify-center gap-2 disabled:opacity-50"
            >
              <Plus className="w-4 h-4" />
              Add to {mealType}
            </button>
          </div>
        )}
      </div>
    </div>
  );
}

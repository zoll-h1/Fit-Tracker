import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { ChevronLeft, ChevronRight, Plus } from 'lucide-react';
import { format, addDays, subDays, parseISO } from 'date-fns';
import { nutritionApi, type MealTypeGroup } from '@/api/nutrition';
import MacroRing from '@/components/nutrition/MacroRing';
import FoodSearchModal from '@/components/nutrition/FoodSearchModal';
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell,
} from 'recharts';

type MealType = 'breakfast' | 'lunch' | 'dinner' | 'snack';

export default function NutritionPage() {
  const qc = useQueryClient();
  const [date, setDate] = useState(() => new Date());
  const [addingMeal, setAddingMeal] = useState<MealType | null>(null);

  const dateStr = format(date, 'yyyy-MM-dd');
  const isToday = dateStr === format(new Date(), 'yyyy-MM-dd');

  const { data: summary } = useQuery({
    queryKey: ['nutrition-daily', dateStr],
    queryFn: () => nutritionApi.daily(dateStr),
  });

  const { data: goals } = useQuery({
    queryKey: ['nutrition-goals'],
    queryFn: () => nutritionApi.getGoals(),
  });

  const { data: weekly } = useQuery({
    queryKey: ['nutrition-weekly'],
    queryFn: () => nutritionApi.weekly(),
  });

  const deleteLog = useMutation({
    mutationFn: (id: number) => nutritionApi.deleteLog(id),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['nutrition-daily', dateStr] }),
  });

  const totalCal = summary?.total_calories ?? 0;
  const totalProt = summary?.total_protein_g ?? 0;
  const totalCarbs = summary?.total_carbs_g ?? 0;
  const totalFat = summary?.total_fat_g ?? 0;

  const goalCal = goals?.calories_target ?? 2000;
  const goalProt = goals?.protein_g ?? 150;
  const goalCarbs = goals?.carbs_g ?? 200;
  const goalFat = goals?.fat_g ?? 65;

  const weeklyChartData = (weekly?.days ?? []).map((d) => ({
    day: format(parseISO(d.date), 'EEE'),
    calories: d.calories,
    target: d.target,
    pct: d.adherence_pct,
  }));

  const MEAL_ORDER: MealType[] = ['breakfast', 'lunch', 'dinner', 'snack'];

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-white">Nutrition</h1>
          <p className="text-slate-400 text-sm mt-1">Track your daily food intake</p>
        </div>
      </div>

      {/* Date picker */}
      <div className="flex items-center gap-3">
        <button
          onClick={() => setDate(d => subDays(d, 1))}
          className="p-1.5 rounded-lg hover:bg-slate-700 text-slate-400 hover:text-white transition-colors"
        >
          <ChevronLeft className="w-5 h-5" />
        </button>
        <span className="text-white font-medium min-w-32 text-center">
          {isToday ? 'Today' : format(date, 'MMM d, yyyy')}
        </span>
        <button
          onClick={() => setDate(d => addDays(d, 1))}
          disabled={isToday}
          className="p-1.5 rounded-lg hover:bg-slate-700 text-slate-400 hover:text-white transition-colors disabled:opacity-30"
        >
          <ChevronRight className="w-5 h-5" />
        </button>
      </div>

      {/* Macro summary card */}
      <div className="bg-slate-800 border border-slate-700 rounded-2xl p-6">
        {goals ? (
          <MacroRing
            calories={totalCal}
            caloriesTarget={goalCal}
            protein={totalProt}
            proteinTarget={goalProt}
            carbs={totalCarbs}
            carbsTarget={goalCarbs}
            fat={totalFat}
            fatTarget={goalFat}
          />
        ) : (
          <div className="text-center text-slate-500 py-4">Loading goals…</div>
        )}
      </div>

      {/* Meals */}
      {MEAL_ORDER.map((mealType) => {
        const group = summary?.meals.find((m) => m.meal_type === mealType);
        return (
          <MealSection
            key={mealType}
            mealType={mealType}
            group={group}
            onAdd={() => setAddingMeal(mealType)}
            onDelete={(id) => deleteLog.mutate(id)}
          />
        );
      })}

      {/* Weekly adherence chart */}
      {weeklyChartData.length > 0 && (
        <div className="bg-slate-800 border border-slate-700 rounded-2xl p-5">
          <h2 className="text-lg font-semibold text-white mb-4">Weekly Adherence</h2>
          <div className="text-center text-2xl font-bold text-white mb-4">
            {weekly?.avg_adherence_pct ?? 0}%
            <span className="text-sm font-normal text-slate-400 ml-2">avg this week</span>
          </div>
          <ResponsiveContainer width="100%" height={160}>
            <BarChart data={weeklyChartData} barCategoryGap="30%">
              <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
              <XAxis dataKey="day" tick={{ fill: '#64748b', fontSize: 11 }} />
              <YAxis tick={{ fill: '#64748b', fontSize: 11 }} unit="%" domain={[0, 100]} />
              <Tooltip
                contentStyle={{ background: '#1e293b', border: '1px solid #334155', borderRadius: 8 }}
                labelStyle={{ color: '#94a3b8' }}
                formatter={(v) => [`${v ?? 0}%`, 'Adherence']}
              />
              <Bar dataKey="pct" radius={[4, 4, 0, 0]}>
                {weeklyChartData.map((d) => (
                  <Cell key={d.day} fill={d.pct >= 90 ? '#22c55e' : d.pct >= 70 ? '#f59e0b' : '#ef4444'} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>
      )}

      {/* Food search modal */}
      {addingMeal && (
        <FoodSearchModal
          mealType={addingMeal}
          logDate={dateStr}
          onClose={() => setAddingMeal(null)}
          onLogged={() => {
            setAddingMeal(null);
            qc.invalidateQueries({ queryKey: ['nutrition-daily', dateStr] });
          }}
        />
      )}
    </div>
  );
}

// ── MealSection ───────────────────────────────────────────────────────────────
const MEAL_LABELS: Record<string, string> = {
  breakfast: '☀️ Breakfast',
  lunch: '🌤️ Lunch',
  dinner: '🌙 Dinner',
  snack: '🍎 Snack',
};

function MealSection({
  mealType,
  group,
  onAdd,
  onDelete,
}: {
  mealType: MealType;
  group?: MealTypeGroup;
  onAdd: () => void;
  onDelete: (id: number) => void;
}) {
  return (
    <div className="bg-slate-800 border border-slate-700 rounded-2xl overflow-hidden">
      <div className="flex items-center justify-between px-5 py-4 border-b border-slate-700">
        <div>
          <h3 className="font-semibold text-white capitalize">{MEAL_LABELS[mealType] ?? mealType}</h3>
          {group && (
            <p className="text-xs text-slate-400 mt-0.5">
              {Math.round(group.subtotal_calories)} kcal ·{' '}
              {group.subtotal_protein_g.toFixed(1)}p / {group.subtotal_carbs_g.toFixed(1)}c / {group.subtotal_fat_g.toFixed(1)}f
            </p>
          )}
        </div>
        <button
          onClick={onAdd}
          className="p-1.5 rounded-lg hover:bg-slate-700 text-violet-400 hover:text-violet-300 transition-colors"
        >
          <Plus className="w-5 h-5" />
        </button>
      </div>
      {group && group.items.length > 0 ? (
        <div className="divide-y divide-slate-700/50">
          {group.items.map((item) => (
            <div key={item.id} className="flex items-center px-5 py-3 gap-3">
              <div className="flex-1">
                <p className="text-white text-sm">{item.food_name ?? `Food #${item.food_id}`}</p>
                <p className="text-slate-500 text-xs">{item.quantity_g}g</p>
              </div>
              <div className="text-right">
                <p className="text-white text-sm">{Math.round(item.calories)} kcal</p>
                <p className="text-slate-500 text-xs">
                  {item.protein_g.toFixed(1)}p / {item.carbs_g.toFixed(1)}c / {item.fat_g.toFixed(1)}f
                </p>
              </div>
              <button onClick={() => onDelete(item.id)} className="text-slate-600 hover:text-rose-400 text-xs ml-2">✕</button>
            </div>
          ))}
        </div>
      ) : (
        <div className="px-5 py-4 text-slate-500 text-sm">No food logged yet — tap + to add</div>
      )}
    </div>
  );
}

import type { BodyGoal } from '@/api/body';

interface GoalsSectionProps {
  goals: BodyGoal[];
}

const GOAL_TYPE_LABELS: Record<string, string> = {
  weight_loss: 'Weight Loss',
  weight_gain: 'Weight Gain',
  body_fat: 'Body Fat %',
  muscle_mass: 'Muscle Mass',
  waist: 'Waist',
  custom: 'Custom',
};

export default function GoalsSection({ goals }: GoalsSectionProps) {
  const active = goals.filter((g) => g.status === 'active');
  const completed = goals.filter((g) => g.status === 'completed');

  if (active.length === 0 && completed.length === 0) return null;

  return (
    <div className="space-y-3">
      <h2 className="text-lg font-semibold text-white">Goals</h2>
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
        {active.map((goal) => (
          <GoalCard key={goal.id} goal={goal} />
        ))}
      </div>
      {completed.length > 0 && (
        <div className="space-y-2">
          <p className="text-xs text-slate-500 uppercase tracking-wider">Completed</p>
          {completed.map((goal) => (
            <div key={goal.id} className="flex items-center gap-3 px-4 py-3 bg-slate-800/50 rounded-lg border border-emerald-500/20">
              <span className="text-emerald-400 text-lg">✓</span>
              <div>
                <p className="text-sm font-medium text-white">
                  {GOAL_TYPE_LABELS[goal.goal_type] ?? goal.goal_type}
                </p>
                <p className="text-xs text-slate-400">
                  {goal.target_value} {goal.unit}
                </p>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

function GoalCard({ goal }: { goal: BodyGoal }) {
  const pct = goal.progress_pct ?? 0;
  const label = GOAL_TYPE_LABELS[goal.goal_type] ?? goal.goal_type;

  return (
    <div className="bg-slate-800 border border-slate-700 rounded-xl p-4 space-y-3">
      <div className="flex items-center justify-between">
        <p className="font-medium text-white text-sm">{label}</p>
        <span className="text-xs text-slate-400">
          {goal.current_value ?? goal.start_value ?? '?'} → {goal.target_value} {goal.unit}
        </span>
      </div>
      <div className="w-full bg-slate-700 rounded-full h-2">
        <div
          className="bg-violet-500 h-2 rounded-full transition-all duration-500"
          style={{ width: `${pct}%` }}
        />
      </div>
      <div className="flex items-center justify-between text-xs text-slate-400">
        <span>{pct}% complete</span>
        {goal.deadline && (
          <span>Due {new Date(goal.deadline).toLocaleDateString()}</span>
        )}
      </div>
    </div>
  );
}

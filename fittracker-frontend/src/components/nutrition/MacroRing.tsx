interface MacroRingProps {
  calories: number;
  caloriesTarget: number;
  protein: number;
  proteinTarget: number;
  carbs: number;
  carbsTarget: number;
  fat: number;
  fatTarget: number;
}

interface RingProps {
  pct: number;
  color: string;
  radius: number;
}

function Ring({ pct, color, radius }: RingProps) {
  const circumference = 2 * Math.PI * radius;
  const offset = circumference - (Math.min(pct, 100) / 100) * circumference;
  return (
    <circle
      cx="60"
      cy="60"
      r={radius}
      fill="none"
      stroke={color}
      strokeWidth="8"
      strokeDasharray={circumference}
      strokeDashoffset={offset}
      strokeLinecap="round"
      style={{ transition: 'stroke-dashoffset 0.6s ease', transform: 'rotate(-90deg)', transformOrigin: '60px 60px' }}
    />
  );
}

export default function MacroRing({
  calories, caloriesTarget,
  protein, proteinTarget,
  carbs, carbsTarget,
  fat, fatTarget,
}: MacroRingProps) {
  const calPct = caloriesTarget > 0 ? (calories / caloriesTarget) * 100 : 0;
  const protPct = proteinTarget > 0 ? (protein / proteinTarget) * 100 : 0;
  const carbPct = carbsTarget > 0 ? (carbs / carbsTarget) * 100 : 0;
  const fatPct = fatTarget > 0 ? (fat / fatTarget) * 100 : 0;

  return (
    <div className="flex flex-col items-center gap-4">
      {/* Concentric rings: calories (outer) > protein > carbs > fat (inner) */}
      <div className="relative w-32 h-32">
        <svg viewBox="0 0 120 120" className="w-full h-full">
          {/* Background tracks */}
          {[46, 36, 26, 16].map((r) => (
            <circle key={r} cx="60" cy="60" r={r} fill="none" stroke="#1e293b" strokeWidth="8" />
          ))}
          {/* Filled rings */}
          <Ring pct={calPct} color="#7c3aed" radius={46} />
          <Ring pct={protPct} color="#3b82f6" radius={36} />
          <Ring pct={carbPct} color="#f59e0b" radius={26} />
          <Ring pct={fatPct} color="#10b981" radius={16} />
        </svg>
        {/* Center label */}
        <div className="absolute inset-0 flex flex-col items-center justify-center">
          <span className="text-lg font-bold text-white">{Math.round(calories)}</span>
          <span className="text-[10px] text-slate-400">kcal</span>
        </div>
      </div>

      {/* Legend */}
      <div className="grid grid-cols-2 gap-x-6 gap-y-1.5 text-sm">
        {[
          { label: 'Calories', color: 'bg-violet-500', val: Math.round(calories), target: caloriesTarget, unit: 'kcal' },
          { label: 'Protein', color: 'bg-blue-500', val: Math.round(protein), target: proteinTarget, unit: 'g' },
          { label: 'Carbs', color: 'bg-amber-400', val: Math.round(carbs), target: carbsTarget, unit: 'g' },
          { label: 'Fat', color: 'bg-emerald-400', val: Math.round(fat), target: fatTarget, unit: 'g' },
        ].map(({ label, color, val, target, unit }) => (
          <div key={label} className="flex items-center gap-2">
            <div className={`w-2.5 h-2.5 rounded-full flex-shrink-0 ${color}`} />
            <span className="text-slate-400 text-xs">{label}</span>
            <span className="text-white text-xs font-medium ml-auto">
              {val}<span className="text-slate-500">/{target}{unit}</span>
            </span>
          </div>
        ))}
      </div>
    </div>
  );
}

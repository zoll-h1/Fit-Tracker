import { useMemo } from 'react';
import type { CalendarDay } from '@/api/gamification';

interface CalendarHeatmapProps {
  days: CalendarDay[];
  currentStreak: number;
  longestStreak: number;
}

export default function CalendarHeatmap({ days, currentStreak, longestStreak }: CalendarHeatmapProps) {
  const weeks = useMemo(() => {
    const result: CalendarDay[][] = [];
    let week: CalendarDay[] = [];
    if (days.length > 0) {
      const firstDay = new Date(days[0].date).getDay();
      for (let i = 0; i < firstDay; i++) {
        week.push({ date: '', has_workout: false });
      }
    }
    for (const day of days) {
      week.push(day);
      if (week.length === 7) {
        result.push(week);
        week = [];
      }
    }
    if (week.length) result.push(week);
    return result;
  }, [days]);

  const dayLabels = ['S', 'M', 'T', 'W', 'T', 'F', 'S'];

  return (
    <div className="space-y-3">
      <div className="flex items-center gap-6 mb-4">
        <div className="text-center">
          <p className="text-2xl font-bold text-amber-400">🔥 {currentStreak}</p>
          <p className="text-xs text-slate-500 mt-0.5">Current Streak</p>
        </div>
        <div className="text-center">
          <p className="text-2xl font-bold text-white">{longestStreak}</p>
          <p className="text-xs text-slate-500 mt-0.5">Best Streak</p>
        </div>
      </div>

      <div className="overflow-x-auto pb-1">
        <div className="flex gap-1">
          <div className="flex flex-col gap-1 mr-1">
            {dayLabels.map((l, i) => (
              <div key={i} className="w-3 h-3 flex items-center justify-center text-[9px] text-slate-600">
                {i % 2 === 0 ? l : ''}
              </div>
            ))}
          </div>
          {weeks.map((week, wi) => (
            <div key={wi} className="flex flex-col gap-1">
              {week.map((day, di) => (
                <div
                  key={di}
                  title={day.date || undefined}
                  className={`w-3 h-3 rounded-sm transition-colors ${
                    !day.date
                      ? 'bg-transparent'
                      : day.has_workout
                      ? 'bg-violet-500 hover:bg-violet-400'
                      : 'bg-slate-700 hover:bg-slate-600'
                  }`}
                />
              ))}
            </div>
          ))}
        </div>
      </div>

      <div className="flex items-center gap-2 text-[10px] text-slate-500">
        <div className="w-3 h-3 rounded-sm bg-slate-700" />
        <span>Rest</span>
        <div className="w-3 h-3 rounded-sm bg-violet-500 ml-2" />
        <span>Workout</span>
      </div>
    </div>
  );
}

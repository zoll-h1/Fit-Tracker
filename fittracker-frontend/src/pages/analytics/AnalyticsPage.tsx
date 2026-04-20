import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import {
  LineChart, Line, BarChart, Bar,
  XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell,
  AreaChart, Area, RadarChart, Radar, PolarGrid, PolarAngleAxis, PolarRadiusAxis,
  ComposedChart,
} from 'recharts';
import {
  analyticsApi,
  type StrengthPoint, type VolumePoint, type MuscleGroup, type PRRecord,
  type VolumeProgressionPoint, type MuscleBalanceCategory, type BodyCompositionPoint,
} from '@/api/gamification';
import { exercisesApi } from '@/api/exercises';
import CalendarHeatmap from '@/components/analytics/CalendarHeatmap';

const TABS = ['Overview', 'Strength', 'Volume', 'Muscles', 'Records', 'Volume Trend', 'Balance', 'Body Comp'];
const PIE_COLORS = ['#8b5cf6', '#06b6d4', '#10b981', '#f59e0b', '#ef4444', '#ec4899', '#6366f1'];

const BALANCE_COLORS: Record<string, string> = {
  push: '#3b82f6',
  pull: '#22c55e',
  legs: '#f97316',
  core: '#a855f7',
  other: '#64748b',
};

export default function AnalyticsPage() {
  const [tab, setTab] = useState('Overview');

  const handleExportCSV = () => {
    analyticsApi.downloadCSV().catch(console.error);
  };

  return (
    <div className="p-6 space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-white">Analytics</h1>
        <button
          onClick={handleExportCSV}
          className="flex items-center gap-2 px-4 py-2 bg-slate-700 hover:bg-slate-600 text-white text-sm font-medium rounded-lg transition-colors"
        >
          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
          </svg>
          Export CSV
        </button>
      </div>

      {/* Tab bar */}
      <div className="flex gap-1 bg-slate-800 p-1 rounded-xl w-fit">
        {TABS.map(t => (
          <button
            key={t}
            onClick={() => setTab(t)}
            className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
              tab === t ? 'bg-violet-600 text-white' : 'text-slate-400 hover:text-white'
            }`}
          >
            {t}
          </button>
        ))}
      </div>

      {tab === 'Overview' && <OverviewTab />}
      {tab === 'Strength' && <StrengthTab />}
      {tab === 'Volume' && <VolumeTab />}
      {tab === 'Muscles' && <MusclesTab />}
      {tab === 'Records' && <RecordsTab />}
      {tab === 'Volume Trend' && <VolumeTrendTab />}
      {tab === 'Balance' && <BalanceTab />}
      {tab === 'Body Comp' && <BodyCompTab />}
    </div>
  );
}

/* ─── Overview ─────────────────────────────────────────────────── */
function OverviewTab() {
  const { data: stats, isLoading } = useQuery({
    queryKey: ['analytics-dashboard'],
    queryFn: analyticsApi.dashboard,
  });
  const { data: streakData } = useQuery({
    queryKey: ['analytics-streak'],
    queryFn: analyticsApi.streak,
  });

  if (isLoading) return <Spinner />;

  return (
    <div className="space-y-6">
      {/* Stats grid */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard label="Workouts This Week" value={stats?.this_week_workouts ?? 0} unit="sessions" />
        <StatCard label="Workouts This Month" value={stats?.this_month_workouts ?? 0} unit="sessions" />
        <StatCard label="Total Volume" value={Math.round((stats?.total_volume_kg ?? 0) / 1000)} unit="tonnes" />
        <StatCard label="Avg Duration" value={Math.round(stats?.avg_workout_duration_min ?? 0)} unit="min" />
      </div>

      {/* Calendar heatmap */}
      {streakData && (
        <div className="bg-slate-800 border border-slate-700 rounded-2xl p-5">
          <h3 className="text-sm font-semibold text-slate-300 mb-4">Activity</h3>
          <CalendarHeatmap
            days={streakData.calendar}
            currentStreak={streakData.current_streak}
            longestStreak={streakData.longest_streak}
          />
        </div>
      )}

      {/* Recent PRs */}
      {stats?.recent_prs && stats.recent_prs.length > 0 && (
        <div className="bg-slate-800 border border-slate-700 rounded-2xl p-5">
          <h3 className="text-sm font-semibold text-slate-300 mb-3">Recent Personal Records</h3>
          <ul className="space-y-2">
            {stats.recent_prs.map((pr, i) => (
              <li key={i} className="flex items-center justify-between text-sm">
                <span className="text-slate-300">{pr.exercise}</span>
                <span className="text-amber-400 font-medium">{pr.weight_kg} kg</span>
                <span className="text-slate-500 text-xs">{new Date(pr.date).toLocaleDateString()}</span>
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}

/* ─── Strength ──────────────────────────────────────────────────── */
function StrengthTab() {
  const [exerciseId, setExerciseId] = useState<number | null>(null);
  const [period, setPeriod] = useState('90d');
  const [search, setSearch] = useState('');

  const { data: exercises } = useQuery({
    queryKey: ['exercises-list', search],
    queryFn: () => exercisesApi.list({ search, per_page: 30 }),
  });

  const { data: chart, isLoading } = useQuery({
    queryKey: ['analytics-strength', exerciseId, period],
    queryFn: () => analyticsApi.strength(exerciseId!, period),
    enabled: exerciseId != null,
  });

  return (
    <div className="space-y-4">
      <div className="flex flex-wrap gap-3">
        <div className="flex-1 min-w-48">
          <label className="block text-xs text-slate-400 mb-1">Exercise</label>
          <input
            value={search}
            onChange={e => setSearch(e.target.value)}
            placeholder="Search exercise…"
            className="w-full bg-slate-800 border border-slate-700 rounded-lg px-3 py-2 text-sm text-white placeholder-slate-500 focus:outline-none focus:border-violet-500"
          />
          {exercises?.items && search && (
            <ul className="absolute z-10 mt-1 bg-slate-800 border border-slate-700 rounded-lg shadow-lg max-h-48 overflow-y-auto text-sm">
              {exercises.items.map(e => (
                <li
                  key={e.id}
                  onClick={() => { setExerciseId(e.id); setSearch(e.name); }}
                  className="px-3 py-2 hover:bg-slate-700 cursor-pointer text-slate-300"
                >
                  {e.name}
                </li>
              ))}
            </ul>
          )}
        </div>
        <div>
          <label className="block text-xs text-slate-400 mb-1">Period</label>
          <select
            value={period}
            onChange={e => setPeriod(e.target.value)}
            className="bg-slate-800 border border-slate-700 rounded-lg px-3 py-2 text-sm text-white focus:outline-none focus:border-violet-500"
          >
            <option value="30d">30 days</option>
            <option value="90d">90 days</option>
            <option value="180d">6 months</option>
            <option value="365d">1 year</option>
          </select>
        </div>
      </div>

      {!exerciseId && (
        <div className="text-center py-12 text-slate-500">Select an exercise to view progress</div>
      )}
      {exerciseId && isLoading && <Spinner />}
      {chart && (
        <div className="bg-slate-800 border border-slate-700 rounded-2xl p-5">
          {chart.pr_weight && (
            <p className="text-sm text-amber-400 mb-3">
              🏆 PR: {chart.pr_weight} kg on {chart.pr_date ? new Date(chart.pr_date).toLocaleDateString() : '—'}
            </p>
          )}
          <ResponsiveContainer width="100%" height={280}>
            <LineChart data={chart.chart} margin={{ top: 4, right: 8, bottom: 0, left: 0 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
              <XAxis dataKey="date" tick={{ fill: '#94a3b8', fontSize: 11 }} tickFormatter={d => d.slice(5)} />
              <YAxis tick={{ fill: '#94a3b8', fontSize: 11 }} />
              <Tooltip
                contentStyle={{ backgroundColor: '#1e293b', border: '1px solid #334155', borderRadius: 8 }}
                labelStyle={{ color: '#cbd5e1' }}
                formatter={(v) => [`${v} kg`, 'Max Weight']}
              />
              <Line type="monotone" dataKey="max_weight_kg" stroke="#8b5cf6" strokeWidth={2} dot={false} />
            </LineChart>
          </ResponsiveContainer>
        </div>
      )}
    </div>
  );
}

/* ─── Volume ────────────────────────────────────────────────────── */
function VolumeTab() {
  const [period, setPeriod] = useState('30d');
  const { data, isLoading } = useQuery<VolumePoint[]>({
    queryKey: ['analytics-volume', period],
    queryFn: () => analyticsApi.volume(period),
  });

  return (
    <div className="space-y-4">
      <div className="flex justify-end">
        <select
          value={period}
          onChange={e => setPeriod(e.target.value)}
          className="bg-slate-800 border border-slate-700 rounded-lg px-3 py-2 text-sm text-white focus:outline-none focus:border-violet-500"
        >
          <option value="30d">30 days</option>
          <option value="90d">90 days</option>
          <option value="180d">6 months</option>
        </select>
      </div>
      {isLoading ? <Spinner /> : (
        <div className="bg-slate-800 border border-slate-700 rounded-2xl p-5">
          <h3 className="text-sm font-semibold text-slate-300 mb-4">Volume per Session (kg)</h3>
          <ResponsiveContainer width="100%" height={280}>
            <BarChart data={data ?? []} margin={{ top: 4, right: 8, bottom: 0, left: 0 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
              <XAxis dataKey="date" tick={{ fill: '#94a3b8', fontSize: 11 }} tickFormatter={d => d.slice(5)} />
              <YAxis tick={{ fill: '#94a3b8', fontSize: 11 }} />
              <Tooltip
                contentStyle={{ backgroundColor: '#1e293b', border: '1px solid #334155', borderRadius: 8 }}
                labelStyle={{ color: '#cbd5e1' }}
                formatter={(v) => [`${v} kg`, 'Volume']}
              />
              <Bar dataKey="volume_kg" fill="#8b5cf6" radius={[3, 3, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      )}
    </div>
  );
}

/* ─── Muscles ───────────────────────────────────────────────────── */
function MusclesTab() {
  const [period, setPeriod] = useState('30d');
  const { data, isLoading } = useQuery<MuscleGroup[]>({
    queryKey: ['analytics-muscles', period],
    queryFn: () => analyticsApi.muscles(period),
  });

  return (
    <div className="space-y-4">
      <div className="flex justify-end">
        <select
          value={period}
          onChange={e => setPeriod(e.target.value)}
          className="bg-slate-800 border border-slate-700 rounded-lg px-3 py-2 text-sm text-white focus:outline-none focus:border-violet-500"
        >
          <option value="7d">7 days</option>
          <option value="30d">30 days</option>
          <option value="90d">90 days</option>
        </select>
      </div>
      {isLoading ? <Spinner /> : (
        <div className="bg-slate-800 border border-slate-700 rounded-2xl p-5 grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Pie chart */}
          <div>
            <h3 className="text-sm font-semibold text-slate-300 mb-4">Distribution</h3>
            <ResponsiveContainer width="100%" height={240}>
              <PieChart>
                <Pie data={data ?? []} dataKey="sets_count" nameKey="muscle_group" cx="50%" cy="50%" outerRadius={90} label={(e) => (e as unknown as MuscleGroup).muscle_group}>
                  {(data ?? []).map((_, i) => (
                    <Cell key={i} fill={PIE_COLORS[i % PIE_COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip
                  contentStyle={{ backgroundColor: '#1e293b', border: '1px solid #334155', borderRadius: 8 }}
                  formatter={(v) => [`${v} sets`, 'Sets']}
                />
              </PieChart>
            </ResponsiveContainer>
          </div>
          {/* Bar list */}
          <div>
            <h3 className="text-sm font-semibold text-slate-300 mb-4">Sets per Muscle Group</h3>
            <div className="space-y-2">
              {(data ?? []).map((m, i) => (
                <div key={m.muscle_group} className="flex items-center gap-3">
                  <span className="text-slate-300 text-sm w-28 truncate capitalize">{m.muscle_group}</span>
                  <div className="flex-1 bg-slate-700 rounded-full h-2">
                    <div
                      className="h-2 rounded-full"
                      style={{ width: `${m.percentage}%`, backgroundColor: PIE_COLORS[i % PIE_COLORS.length] }}
                    />
                  </div>
                  <span className="text-slate-400 text-xs w-12 text-right">{m.sets_count} sets</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}
      {!data?.length && !isLoading && (
        <div className="text-center py-12 text-slate-500">No muscle data for this period</div>
      )}
    </div>
  );
}

/* ─── Records ───────────────────────────────────────────────────── */
function RecordsTab() {
  const { data, isLoading } = useQuery<PRRecord[]>({
    queryKey: ['analytics-prs'],
    queryFn: analyticsApi.personalRecords,
  });

  return (
    <div className="space-y-4">
      <h3 className="text-sm font-semibold text-slate-300">All Personal Records</h3>
      {isLoading ? <Spinner /> : (
        <div className="bg-slate-800 border border-slate-700 rounded-2xl overflow-hidden">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-slate-700 text-slate-400 text-xs">
                <th className="text-left px-4 py-3">Exercise</th>
                <th className="text-right px-4 py-3">Weight</th>
                <th className="text-right px-4 py-3">Reps</th>
                <th className="text-right px-4 py-3">Date</th>
              </tr>
            </thead>
            <tbody>
              {(data ?? []).map((pr) => (
                <tr key={`${pr.exercise_id}-${pr.achieved_at}`} className="border-b border-slate-700/50 hover:bg-slate-700/30">
                  <td className="px-4 py-3 text-white">{pr.exercise_name}</td>
                  <td className="px-4 py-3 text-amber-400 text-right font-medium">{pr.weight_kg} kg</td>
                  <td className="px-4 py-3 text-slate-300 text-right">{pr.reps ?? '—'}</td>
                  <td className="px-4 py-3 text-slate-400 text-right">{new Date(pr.achieved_at).toLocaleDateString()}</td>
                </tr>
              ))}
            </tbody>
          </table>
          {!data?.length && (
            <div className="text-center py-12 text-slate-500">No personal records yet</div>
          )}
        </div>
      )}
    </div>
  );
}

/* ─── Volume Trend ──────────────────────────────────────────────────── */
function VolumeTrendTab() {
  const { data, isLoading } = useQuery<VolumeProgressionPoint[]>({
    queryKey: ['analytics-volume-progression'],
    queryFn: analyticsApi.volumeProgression,
  });

  if (isLoading) return <Spinner />;
  if (!data?.length) return <div className="text-center py-12 text-slate-500">No volume data yet</div>;

  return (
    <div className="space-y-6">
      <div className="bg-slate-800 border border-slate-700 rounded-2xl p-5">
        <h3 className="text-sm font-semibold text-slate-300 mb-4">Weekly Volume (kg) + 4-Week Rolling Avg</h3>
        <ResponsiveContainer width="100%" height={280}>
          <AreaChart data={data} margin={{ top: 4, right: 8, bottom: 0, left: 0 }}>
            <defs>
              <linearGradient id="volGrad" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.3} />
                <stop offset="95%" stopColor="#3b82f6" stopOpacity={0} />
              </linearGradient>
            </defs>
            <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
            <XAxis dataKey="week" tick={{ fill: '#94a3b8', fontSize: 10 }} />
            <YAxis tick={{ fill: '#94a3b8', fontSize: 11 }} />
            <Tooltip
              contentStyle={{ backgroundColor: '#1e293b', border: '1px solid #334155', borderRadius: 8 }}
              labelStyle={{ color: '#cbd5e1' }}
            />
            <Area type="monotone" dataKey="total_volume" stroke="#3b82f6" fill="url(#volGrad)" strokeWidth={2} name="Volume (kg)" />
            <Line type="monotone" dataKey="rolling_avg" stroke="#f97316" strokeWidth={2} strokeDasharray="5 3" dot={false} name="4-wk Avg" />
          </AreaChart>
        </ResponsiveContainer>
      </div>

      <div className="bg-slate-800 border border-slate-700 rounded-2xl p-5">
        <h3 className="text-sm font-semibold text-slate-300 mb-4">Workouts per Week</h3>
        <ResponsiveContainer width="100%" height={180}>
          <BarChart data={data} margin={{ top: 4, right: 8, bottom: 0, left: 0 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
            <XAxis dataKey="week" tick={{ fill: '#94a3b8', fontSize: 10 }} />
            <YAxis tick={{ fill: '#94a3b8', fontSize: 11 }} allowDecimals={false} />
            <Tooltip
              contentStyle={{ backgroundColor: '#1e293b', border: '1px solid #334155', borderRadius: 8 }}
              labelStyle={{ color: '#cbd5e1' }}
            />
            <Bar dataKey="workout_count" fill="#8b5cf6" radius={[3, 3, 0, 0]} name="Workouts" />
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}

/* ─── Balance ───────────────────────────────────────────────────────── */
function BalanceTab() {
  const { data, isLoading } = useQuery<MuscleBalanceCategory[]>({
    queryKey: ['analytics-muscle-balance'],
    queryFn: analyticsApi.muscleBalance,
  });

  if (isLoading) return <Spinner />;

  const radarData = (data ?? []).map(d => ({
    category: d.category.charAt(0).toUpperCase() + d.category.slice(1),
    sets: d.sets_count,
  }));

  return (
    <div className="space-y-6">
      <div className="bg-slate-800 border border-slate-700 rounded-2xl p-5">
        <h3 className="text-sm font-semibold text-slate-300 mb-4">Push / Pull / Legs / Core Balance</h3>
        <ResponsiveContainer width="100%" height={280}>
          <RadarChart data={radarData}>
            <PolarGrid stroke="#334155" />
            <PolarAngleAxis dataKey="category" tick={{ fill: '#94a3b8', fontSize: 12 }} />
            <PolarRadiusAxis tick={{ fill: '#64748b', fontSize: 10 }} />
            <Radar name="Sets" dataKey="sets" stroke="#8b5cf6" fill="#8b5cf6" fillOpacity={0.4} />
            <Tooltip
              contentStyle={{ backgroundColor: '#1e293b', border: '1px solid #334155', borderRadius: 8 }}
            />
          </RadarChart>
        </ResponsiveContainer>
      </div>

      <div className="grid grid-cols-2 lg:grid-cols-3 gap-3">
        {(data ?? []).map(cat => (
          <div
            key={cat.category}
            className="bg-slate-800 border border-slate-700 rounded-xl p-4"
            style={{ borderLeftColor: BALANCE_COLORS[cat.category], borderLeftWidth: 3 }}
          >
            <p className="text-xs text-slate-400 uppercase tracking-wide mb-1">{cat.category}</p>
            <p className="text-xl font-bold text-white">
              {cat.sets_count} <span className="text-sm font-normal text-slate-400">sets</span>
            </p>
            <p className="text-xs text-slate-500 mt-0.5">{cat.percentage}%</p>
            {cat.exercises.length > 0 && (
              <p className="text-xs text-slate-500 mt-1 truncate">{cat.exercises.join(', ')}</p>
            )}
          </div>
        ))}
      </div>

      <div className="bg-slate-800 border border-slate-700 rounded-2xl p-5">
        <h3 className="text-sm font-semibold text-slate-300 mb-4">Sets by Category</h3>
        <div className="space-y-3">
          {(data ?? []).map(cat => (
            <div key={cat.category} className="flex items-center gap-3">
              <span className="text-slate-300 text-sm w-16 capitalize">{cat.category}</span>
              <div className="flex-1 bg-slate-700 rounded-full h-2">
                <div
                  className="h-2 rounded-full transition-all"
                  style={{ width: `${cat.percentage}%`, backgroundColor: BALANCE_COLORS[cat.category] }}
                />
              </div>
              <span className="text-slate-400 text-xs w-24 text-right">
                {cat.sets_count} sets ({cat.percentage}%)
              </span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

/* ─── Body Comp ─────────────────────────────────────────────────────── */
function BodyCompTab() {
  const { data, isLoading } = useQuery<BodyCompositionPoint[]>({
    queryKey: ['analytics-body-composition'],
    queryFn: analyticsApi.bodyComposition,
  });

  if (isLoading) return <Spinner />;
  if (!data?.length) return <div className="text-center py-12 text-slate-500">No body metrics logged yet</div>;

  const latest = data[data.length - 1];
  const bmiLabel =
    latest.bmi == null ? null
    : latest.bmi < 18.5 ? 'Underweight'
    : latest.bmi < 25 ? 'Normal'
    : latest.bmi < 30 ? 'Overweight'
    : 'Obese';
  const bmiColorClass =
    latest.bmi == null ? ''
    : latest.bmi < 18.5 ? 'bg-blue-500/20 text-blue-400'
    : latest.bmi < 25 ? 'bg-green-500/20 text-green-400'
    : latest.bmi < 30 ? 'bg-yellow-500/20 text-yellow-400'
    : 'bg-red-500/20 text-red-400';

  return (
    <div className="space-y-6">
      {bmiLabel && latest.bmi != null && (
        <div className="flex items-center gap-3 flex-wrap">
          <span className="text-slate-400 text-sm">Latest BMI:</span>
          <span className={`px-3 py-1 rounded-full text-sm font-medium ${bmiColorClass}`}>
            {latest.bmi.toFixed(1)} — {bmiLabel}
          </span>
          {latest.weight_kg && (
            <span className="text-slate-400 text-sm">{latest.weight_kg} kg</span>
          )}
        </div>
      )}

      <div className="bg-slate-800 border border-slate-700 rounded-2xl p-5">
        <h3 className="text-sm font-semibold text-slate-300 mb-4">Weight &amp; Body Fat (last 90 days)</h3>
        <ResponsiveContainer width="100%" height={300}>
          <ComposedChart data={data} margin={{ top: 4, right: 40, bottom: 0, left: 0 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
            <XAxis dataKey="date" tick={{ fill: '#94a3b8', fontSize: 10 }} tickFormatter={d => d.slice(5)} />
            <YAxis yAxisId="weight" tick={{ fill: '#94a3b8', fontSize: 11 }} unit=" kg" />
            <YAxis yAxisId="fat" orientation="right" tick={{ fill: '#94a3b8', fontSize: 11 }} unit="%" />
            <Tooltip
              contentStyle={{ backgroundColor: '#1e293b', border: '1px solid #334155', borderRadius: 8 }}
              labelStyle={{ color: '#cbd5e1' }}
            />
            <Line
              yAxisId="weight"
              type="monotone"
              dataKey="weight_kg"
              stroke="#3b82f6"
              strokeWidth={2}
              dot={{ r: 3 }}
              name="Weight (kg)"
              connectNulls
            />
            <Line
              yAxisId="fat"
              type="monotone"
              dataKey="body_fat_pct"
              stroke="#f97316"
              strokeWidth={2}
              dot={{ r: 3 }}
              strokeDasharray="4 2"
              name="Body Fat %"
              connectNulls
            />
          </ComposedChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}

/* ─── Shared ────────────────────────────────────────────────────── */
function StatCard({ label, value, unit }: { label: string; value: number; unit: string }) {
  return (
    <div className="bg-slate-800 border border-slate-700 rounded-2xl p-4">
      <p className="text-slate-400 text-xs mb-1">{label}</p>
      <p className="text-2xl font-bold text-white">{value.toLocaleString()}</p>
      <p className="text-slate-500 text-xs mt-0.5">{unit}</p>
    </div>
  );
}

function Spinner() {
  return (
    <div className="flex justify-center py-12">
      <div className="w-8 h-8 border-2 border-violet-500 border-t-transparent rounded-full animate-spin" />
    </div>
  );
}

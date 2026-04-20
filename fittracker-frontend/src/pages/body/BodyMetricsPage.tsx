import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { Scale, Target, Plus, Trash2, TrendingDown, TrendingUp } from 'lucide-react';
import { bodyApi, type BodyMetric, type BodyGoal } from '@/api/body';
import {
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
} from 'recharts';
import { format } from 'date-fns';
import GoalsSection from '@/components/body/GoalsSection';

export default function BodyMetricsPage() {
  const qc = useQueryClient();
  const [showLogForm, setShowLogForm] = useState(false);
  const [showGoalForm, setShowGoalForm] = useState(false);

  const { data: history } = useQuery({
    queryKey: ['body-metrics'],
    queryFn: () => bodyApi.listMetrics(1, 60),
  });

  const { data: goals } = useQuery({
    queryKey: ['body-goals'],
    queryFn: () => bodyApi.listGoals(),
  });

  const chartData = (history?.items ?? [])
    .slice()
    .reverse()
    .filter((m) => m.weight_kg)
    .map((m) => ({
      date: format(new Date(m.recorded_at), 'MMM d'),
      weight: parseFloat(String(m.weight_kg)),
    }));

  const latest = history?.items[0];

  return (
    <div className="p-6 space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-white">Body Metrics</h1>
          <p className="text-slate-400 text-sm mt-1">Track your body composition over time</p>
        </div>
        <div className="flex gap-2">
          <button
            onClick={() => setShowGoalForm(true)}
            className="px-3 py-2 border border-slate-600 rounded-lg text-slate-300 hover:text-white text-sm transition-colors flex items-center gap-1.5"
          >
            <Target className="w-4 h-4" />
            Add Goal
          </button>
          <button
            onClick={() => setShowLogForm(true)}
            className="px-4 py-2 bg-violet-600 hover:bg-violet-500 text-white rounded-lg text-sm font-medium transition-colors flex items-center gap-1.5"
          >
            <Plus className="w-4 h-4" />
            Log Measurement
          </button>
        </div>
      </div>

      {/* Latest stats */}
      {latest && (
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
          {[
            { label: 'Weight', value: latest.weight_kg ? `${latest.weight_kg} kg` : '—', icon: Scale },
            { label: 'Body Fat', value: latest.body_fat_pct ? `${latest.body_fat_pct}%` : '—', icon: Scale },
            { label: 'BMI', value: latest.bmi ? String(latest.bmi) : '—', icon: Scale },
            { label: 'Muscle Mass', value: latest.muscle_mass_kg ? `${latest.muscle_mass_kg} kg` : '—', icon: Scale },
          ].map(({ label, value }) => (
            <div key={label} className="bg-slate-800 border border-slate-700 rounded-xl p-4 text-center">
              <p className="text-2xl font-bold text-white">{value}</p>
              <p className="text-slate-500 text-xs mt-1">{label}</p>
            </div>
          ))}
        </div>
      )}

      {/* Weight Chart */}
      {chartData.length > 1 && (
        <div className="bg-slate-800 border border-slate-700 rounded-xl p-5">
          <h2 className="text-lg font-semibold text-white mb-4">Weight History</h2>
          <ResponsiveContainer width="100%" height={220}>
            <LineChart data={chartData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
              <XAxis dataKey="date" tick={{ fill: '#64748b', fontSize: 11 }} />
              <YAxis
                domain={['auto', 'auto']}
                tick={{ fill: '#64748b', fontSize: 11 }}
                width={40}
              />
              <Tooltip
                contentStyle={{ background: '#1e293b', border: '1px solid #334155', borderRadius: 8 }}
                labelStyle={{ color: '#94a3b8' }}
                itemStyle={{ color: '#a78bfa' }}
              />
              <Line
                type="monotone"
                dataKey="weight"
                stroke="#7c3aed"
                strokeWidth={2}
                dot={{ r: 3, fill: '#7c3aed' }}
                activeDot={{ r: 5 }}
              />
            </LineChart>
          </ResponsiveContainer>
        </div>
      )}

      {/* Goals */}
      {goals && goals.length > 0 && <GoalsSection goals={goals} />}

      {/* History table */}
      {history && history.items.length > 0 && (
        <div className="bg-slate-800 border border-slate-700 rounded-xl overflow-hidden">
          <div className="px-5 py-4 border-b border-slate-700">
            <h2 className="font-semibold text-white">Measurement History</h2>
          </div>
          <div className="divide-y divide-slate-700">
            {history.items.map((m) => (
              <MetricRow key={m.id} metric={m} onDelete={() => qc.invalidateQueries({ queryKey: ['body-metrics'] })} />
            ))}
          </div>
        </div>
      )}

      {/* Modals */}
      {showLogForm && (
        <LogMetricModal
          onClose={() => setShowLogForm(false)}
          onSaved={() => { setShowLogForm(false); qc.invalidateQueries({ queryKey: ['body-metrics'] }); }}
        />
      )}
      {showGoalForm && (
        <AddGoalModal
          onClose={() => setShowGoalForm(false)}
          onSaved={() => { setShowGoalForm(false); qc.invalidateQueries({ queryKey: ['body-goals'] }); }}
        />
      )}
    </div>
  );
}

// ── MetricRow ─────────────────────────────────────────────────────────────────
function MetricRow({ metric, onDelete }: { metric: BodyMetric; onDelete: () => void }) {
  const deleteMutation = useMutation({
    mutationFn: () => bodyApi.deleteMetric(metric.id),
    onSuccess: onDelete,
  });
  return (
    <div className="flex items-center px-5 py-3 gap-4">
      <span className="text-slate-400 text-sm w-28">
        {format(new Date(metric.recorded_at), 'MMM d, yyyy')}
      </span>
      <div className="flex-1 flex gap-4 text-sm text-white">
        {metric.weight_kg && <span>{metric.weight_kg} kg</span>}
        {metric.body_fat_pct && <span className="text-slate-400">{metric.body_fat_pct}% BF</span>}
        {metric.bmi && <span className="text-slate-400">BMI {metric.bmi}</span>}
      </div>
      <button onClick={() => deleteMutation.mutate()} className="text-slate-600 hover:text-rose-400 transition-colors">
        <Trash2 className="w-4 h-4" />
      </button>
    </div>
  );
}

// ── LogMetricModal ─────────────────────────────────────────────────────────────
function LogMetricModal({ onClose, onSaved }: { onClose: () => void; onSaved: () => void }) {
  const [form, setForm] = useState({ weight_kg: '', body_fat_pct: '', muscle_mass_kg: '', waist_cm: '', notes: '' });

  const mutation = useMutation({
    mutationFn: () =>
      bodyApi.logMetric({
        weight_kg: form.weight_kg ? parseFloat(form.weight_kg) : undefined,
        body_fat_pct: form.body_fat_pct ? parseFloat(form.body_fat_pct) : undefined,
        muscle_mass_kg: form.muscle_mass_kg ? parseFloat(form.muscle_mass_kg) : undefined,
        waist_cm: form.waist_cm ? parseFloat(form.waist_cm) : undefined,
        notes: form.notes || undefined,
      }),
    onSuccess: onSaved,
  });

  return (
    <div className="fixed inset-0 bg-black/60 flex items-center justify-center z-50 p-4">
      <div className="bg-slate-800 border border-slate-700 rounded-2xl p-6 w-full max-w-md space-y-4">
        <h2 className="text-lg font-bold text-white">Log Measurement</h2>
        <div className="grid grid-cols-2 gap-3">
          {[
            { key: 'weight_kg', label: 'Weight (kg)' },
            { key: 'body_fat_pct', label: 'Body Fat (%)' },
            { key: 'muscle_mass_kg', label: 'Muscle Mass (kg)' },
            { key: 'waist_cm', label: 'Waist (cm)' },
          ].map(({ key, label }) => (
            <div key={key}>
              <label className="text-xs text-slate-400 block mb-1">{label}</label>
              <input
                type="number"
                step="0.1"
                value={form[key as keyof typeof form]}
                onChange={(e) => setForm({ ...form, [key]: e.target.value })}
                className="w-full px-3 py-2 bg-slate-700 border border-slate-600 rounded-lg text-white text-sm focus:outline-none focus:border-violet-500"
              />
            </div>
          ))}
        </div>
        <textarea
          placeholder="Notes (optional)"
          value={form.notes}
          onChange={(e) => setForm({ ...form, notes: e.target.value })}
          rows={2}
          className="w-full px-3 py-2 bg-slate-700 border border-slate-600 rounded-lg text-white text-sm focus:outline-none focus:border-violet-500 resize-none"
        />
        <div className="flex gap-3">
          <button onClick={onClose} className="flex-1 py-2.5 border border-slate-600 rounded-lg text-slate-300">Cancel</button>
          <button
            onClick={() => mutation.mutate()}
            disabled={mutation.isPending}
            className="flex-1 py-2.5 bg-violet-600 hover:bg-violet-500 text-white rounded-lg font-medium disabled:opacity-50"
          >
            Save
          </button>
        </div>
      </div>
    </div>
  );
}

// ── AddGoalModal ──────────────────────────────────────────────────────────────
const GOAL_TYPES = ['weight_loss', 'weight_gain', 'body_fat', 'muscle_mass', 'waist'];

function AddGoalModal({ onClose, onSaved }: { onClose: () => void; onSaved: () => void }) {
  const [form, setForm] = useState({ goal_type: 'weight_loss', target_value: '', start_value: '', unit: 'kg' });

  const mutation = useMutation({
    mutationFn: () =>
      bodyApi.createGoal({
        goal_type: form.goal_type,
        target_value: parseFloat(form.target_value),
        start_value: form.start_value ? parseFloat(form.start_value) : undefined,
        unit: form.unit,
      }),
    onSuccess: onSaved,
  });

  return (
    <div className="fixed inset-0 bg-black/60 flex items-center justify-center z-50 p-4">
      <div className="bg-slate-800 border border-slate-700 rounded-2xl p-6 w-full max-w-sm space-y-4">
        <h2 className="text-lg font-bold text-white">Add Body Goal</h2>
        <div>
          <label className="text-xs text-slate-400 block mb-1">Goal Type</label>
          <select
            value={form.goal_type}
            onChange={(e) => setForm({ ...form, goal_type: e.target.value })}
            className="w-full px-3 py-2 bg-slate-700 border border-slate-600 rounded-lg text-white text-sm focus:outline-none"
          >
            {GOAL_TYPES.map(t => <option key={t} value={t}>{t.replace(/_/g, ' ')}</option>)}
          </select>
        </div>
        <div className="grid grid-cols-2 gap-3">
          <div>
            <label className="text-xs text-slate-400 block mb-1">Current Value</label>
            <input type="number" step="0.1" value={form.start_value}
              onChange={e => setForm({ ...form, start_value: e.target.value })}
              className="w-full px-3 py-2 bg-slate-700 border border-slate-600 rounded-lg text-white text-sm focus:outline-none" />
          </div>
          <div>
            <label className="text-xs text-slate-400 block mb-1">Target Value</label>
            <input type="number" step="0.1" value={form.target_value}
              onChange={e => setForm({ ...form, target_value: e.target.value })}
              className="w-full px-3 py-2 bg-slate-700 border border-slate-600 rounded-lg text-white text-sm focus:outline-none" />
          </div>
        </div>
        <div className="flex gap-3">
          <button onClick={onClose} className="flex-1 py-2.5 border border-slate-600 rounded-lg text-slate-300">Cancel</button>
          <button
            onClick={() => mutation.mutate()}
            disabled={mutation.isPending || !form.target_value}
            className="flex-1 py-2.5 bg-violet-600 hover:bg-violet-500 text-white rounded-lg font-medium disabled:opacity-50"
          >
            Add Goal
          </button>
        </div>
      </div>
    </div>
  );
}

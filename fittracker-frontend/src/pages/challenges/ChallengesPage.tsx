import { useState } from 'react'
import { Link } from 'react-router-dom'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { challengesApi, type Challenge, type ChallengeCreate } from '@/api/challenges'
import { format } from 'date-fns'

const TYPE_ICONS: Record<string, string> = {
  total_workouts: '💪',
  total_volume: '📦',
  streak: '🔥',
}

const TYPE_LABELS: Record<string, string> = {
  total_workouts: 'Total Workouts',
  total_volume: 'Total Volume',
  streak: 'Streak',
}

const TYPE_UNITS: Record<string, string> = {
  total_workouts: 'workouts',
  total_volume: 'kg volume',
  streak: 'days',
}

function ProgressBar({ value, max }: { value: number; max: number }) {
  const pct = max > 0 ? Math.min(100, (value / max) * 100) : 0
  return (
    <div className="w-full bg-slate-700 rounded-full h-2">
      <div
        className="bg-violet-500 h-2 rounded-full transition-all"
        style={{ width: `${pct}%` }}
      />
    </div>
  )
}

function ChallengeCard({
  challenge,
  onJoin,
  onLeave,
}: {
  challenge: Challenge
  onJoin: (id: number) => void
  onLeave: (id: number) => void
}) {
  return (
    <div className="bg-slate-800 border border-slate-700 rounded-xl p-5 space-y-4">
      <div className="flex items-start justify-between gap-2">
        <div className="flex items-center gap-2 min-w-0">
          <span className="text-2xl">{TYPE_ICONS[challenge.challenge_type]}</span>
          <div className="min-w-0">
            <h3 className="font-semibold text-white truncate">{challenge.title}</h3>
            {challenge.description && (
              <p className="text-sm text-slate-400 truncate">{challenge.description}</p>
            )}
          </div>
        </div>
        <span className={`text-xs font-medium px-2 py-1 rounded-full flex-shrink-0 ${
          challenge.status === 'active'
            ? 'bg-green-900/50 text-green-400'
            : challenge.status === 'completed'
            ? 'bg-violet-900/50 text-violet-400'
            : 'bg-slate-700 text-slate-400'
        }`}>
          {challenge.status}
        </span>
      </div>

      <div className="flex items-center gap-4 text-xs text-slate-400">
        <span>{TYPE_LABELS[challenge.challenge_type]}</span>
        <span>🎯 {challenge.target_value} {TYPE_UNITS[challenge.challenge_type]}</span>
        <span>👥 {challenge.participant_count}</span>
      </div>

      <div className="text-xs text-slate-400">
        {format(new Date(challenge.start_date), 'MMM d')} – {format(new Date(challenge.end_date), 'MMM d, yyyy')}
      </div>

      {challenge.is_joined && challenge.my_progress !== null && (
        <div className="space-y-1">
          <div className="flex justify-between text-xs text-slate-400">
            <span>My progress</span>
            <span>{challenge.my_progress} / {challenge.target_value} {TYPE_UNITS[challenge.challenge_type]}</span>
          </div>
          <ProgressBar value={challenge.my_progress} max={challenge.target_value} />
          {challenge.my_rank && (
            <p className="text-xs text-violet-400">Rank #{challenge.my_rank}</p>
          )}
        </div>
      )}

      <div className="flex items-center gap-2 pt-1">
        <Link
          to={`/challenges/${challenge.id}`}
          className="text-sm text-violet-400 hover:text-violet-300 transition-colors"
        >
          View Details →
        </Link>
        <div className="ml-auto">
          {challenge.status === 'active' && (
            challenge.is_joined ? (
              <button
                onClick={() => onLeave(challenge.id)}
                className="px-3 py-1.5 text-xs font-medium bg-slate-700 hover:bg-slate-600 text-slate-300 rounded-lg transition-colors"
              >
                Leave
              </button>
            ) : (
              <button
                onClick={() => onJoin(challenge.id)}
                className="px-3 py-1.5 text-xs font-medium bg-violet-600 hover:bg-violet-700 text-white rounded-lg transition-colors"
              >
                Join
              </button>
            )
          )}
        </div>
      </div>
    </div>
  )
}

function CreateChallengeModal({ onClose }: { onClose: () => void }) {
  const queryClient = useQueryClient()
  const [form, setForm] = useState<ChallengeCreate>({
    title: '',
    description: '',
    challenge_type: 'total_workouts',
    target_value: 10,
    start_date: new Date().toISOString().split('T')[0],
    end_date: new Date(Date.now() + 30 * 86400000).toISOString().split('T')[0],
    is_public: true,
  })

  const createMutation = useMutation({
    mutationFn: (data: ChallengeCreate) => challengesApi.create(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['challenges'] })
      onClose()
    },
  })

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    createMutation.mutate(form)
  }

  return (
    <div className="fixed inset-0 bg-black/60 flex items-center justify-center z-50 p-4">
      <div className="bg-slate-800 border border-slate-700 rounded-2xl w-full max-w-lg p-6 space-y-5">
        <div className="flex items-center justify-between">
          <h2 className="text-lg font-bold text-white">Create Challenge</h2>
          <button onClick={onClose} className="text-slate-400 hover:text-white text-xl">✕</button>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-slate-300 mb-1">Title</label>
            <input
              required
              value={form.title}
              onChange={e => setForm(f => ({ ...f, title: e.target.value }))}
              className="w-full bg-slate-700 border border-slate-600 rounded-lg px-3 py-2 text-white placeholder-slate-400 focus:outline-none focus:border-violet-500"
              placeholder="30-day challenge..."
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-slate-300 mb-1">Description</label>
            <textarea
              value={form.description}
              onChange={e => setForm(f => ({ ...f, description: e.target.value }))}
              rows={2}
              className="w-full bg-slate-700 border border-slate-600 rounded-lg px-3 py-2 text-white placeholder-slate-400 focus:outline-none focus:border-violet-500 resize-none"
              placeholder="Optional description..."
            />
          </div>

          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="block text-sm font-medium text-slate-300 mb-1">Type</label>
              <select
                value={form.challenge_type}
                onChange={e => setForm(f => ({ ...f, challenge_type: e.target.value as ChallengeCreate['challenge_type'] }))}
                className="w-full bg-slate-700 border border-slate-600 rounded-lg px-3 py-2 text-white focus:outline-none focus:border-violet-500"
              >
                <option value="total_workouts">💪 Total Workouts</option>
                <option value="total_volume">📦 Total Volume</option>
                <option value="streak">🔥 Streak</option>
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-slate-300 mb-1">
                Target ({TYPE_UNITS[form.challenge_type]})
              </label>
              <input
                type="number"
                min={1}
                required
                value={form.target_value}
                onChange={e => setForm(f => ({ ...f, target_value: Number(e.target.value) }))}
                className="w-full bg-slate-700 border border-slate-600 rounded-lg px-3 py-2 text-white focus:outline-none focus:border-violet-500"
              />
            </div>
          </div>

          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="block text-sm font-medium text-slate-300 mb-1">Start Date</label>
              <input
                type="date"
                required
                value={form.start_date}
                onChange={e => setForm(f => ({ ...f, start_date: e.target.value }))}
                className="w-full bg-slate-700 border border-slate-600 rounded-lg px-3 py-2 text-white focus:outline-none focus:border-violet-500"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-slate-300 mb-1">End Date</label>
              <input
                type="date"
                required
                value={form.end_date}
                onChange={e => setForm(f => ({ ...f, end_date: e.target.value }))}
                className="w-full bg-slate-700 border border-slate-600 rounded-lg px-3 py-2 text-white focus:outline-none focus:border-violet-500"
              />
            </div>
          </div>

          <div className="flex items-center gap-3">
            <label className="relative inline-flex items-center cursor-pointer">
              <input
                type="checkbox"
                checked={form.is_public}
                onChange={e => setForm(f => ({ ...f, is_public: e.target.checked }))}
                className="sr-only peer"
              />
              <div className="w-11 h-6 bg-slate-600 rounded-full peer peer-checked:bg-violet-600 transition-colors after:content-[''] after:absolute after:top-0.5 after:left-0.5 after:bg-white after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:after:translate-x-5" />
            </label>
            <span className="text-sm text-slate-300">Public challenge</span>
          </div>

          {createMutation.error && (
            <p className="text-sm text-red-400">Failed to create challenge. Please try again.</p>
          )}

          <div className="flex gap-3 pt-1">
            <button
              type="button"
              onClick={onClose}
              className="flex-1 px-4 py-2 bg-slate-700 hover:bg-slate-600 text-white rounded-lg font-medium transition-colors"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={createMutation.isPending}
              className="flex-1 px-4 py-2 bg-violet-600 hover:bg-violet-700 disabled:opacity-50 text-white rounded-lg font-medium transition-colors"
            >
              {createMutation.isPending ? 'Creating…' : 'Create'}
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}

type Tab = 'active' | 'mine' | 'completed'

export default function ChallengesPage() {
  const queryClient = useQueryClient()
  const [tab, setTab] = useState<Tab>('active')
  const [showCreate, setShowCreate] = useState(false)

  const queryParams =
    tab === 'mine'
      ? { mine: true }
      : tab === 'completed'
      ? { status: 'completed' }
      : { status: 'active' }

  const { data: challenges, isLoading } = useQuery({
    queryKey: ['challenges', tab],
    queryFn: () => challengesApi.list(queryParams),
  })

  const joinMutation = useMutation({
    mutationFn: (id: number) => challengesApi.join(id),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['challenges'] }),
  })

  const leaveMutation = useMutation({
    mutationFn: (id: number) => challengesApi.leave(id),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['challenges'] }),
  })

  const TABS: { key: Tab; label: string }[] = [
    { key: 'active', label: 'Active' },
    { key: 'mine', label: 'My Challenges' },
    { key: 'completed', label: 'Completed' },
  ]

  return (
    <div className="max-w-3xl mx-auto space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-white">Challenges</h1>
        <button
          onClick={() => setShowCreate(true)}
          className="px-4 py-2 bg-violet-600 hover:bg-violet-700 text-white rounded-lg font-medium transition-colors text-sm"
        >
          + Create Challenge
        </button>
      </div>

      <div className="flex gap-1 bg-slate-800 border border-slate-700 rounded-xl p-1">
        {TABS.map(t => (
          <button
            key={t.key}
            onClick={() => setTab(t.key)}
            className={`flex-1 py-2 text-sm font-medium rounded-lg transition-colors ${
              tab === t.key
                ? 'bg-violet-600 text-white'
                : 'text-slate-400 hover:text-white'
            }`}
          >
            {t.label}
          </button>
        ))}
      </div>

      {isLoading ? (
        <div className="flex justify-center py-12">
          <div className="w-8 h-8 border-2 border-violet-500 border-t-transparent rounded-full animate-spin" />
        </div>
      ) : challenges && challenges.length > 0 ? (
        <div className="space-y-4">
          {challenges.map(c => (
            <ChallengeCard
              key={c.id}
              challenge={c}
              onJoin={id => joinMutation.mutate(id)}
              onLeave={id => leaveMutation.mutate(id)}
            />
          ))}
        </div>
      ) : (
        <div className="text-center py-16">
          <p className="text-4xl mb-4">🏆</p>
          <h2 className="text-lg font-semibold text-white mb-2">No challenges here yet</h2>
          <p className="text-slate-400">
            {tab === 'mine' ? 'Create or join a challenge to get started' : 'No challenges found'}
          </p>
        </div>
      )}

      {showCreate && <CreateChallengeModal onClose={() => setShowCreate(false)} />}
    </div>
  )
}

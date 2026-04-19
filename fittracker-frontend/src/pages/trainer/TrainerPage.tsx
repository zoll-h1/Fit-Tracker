import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { Users, Plus, Star, BookOpen, Lock } from 'lucide-react'
import { trainerApi, type WorkoutProgram, type ClientStats } from '@/api/trainer'
import { useAuthStore } from '@/stores/authStore'

const DIFFICULTY_COLORS: Record<string, string> = {
  beginner: 'bg-green-900/50 text-green-400',
  intermediate: 'bg-yellow-900/50 text-yellow-400',
  advanced: 'bg-red-900/50 text-red-400',
}

// ── Create Program Modal ──────────────────────────────────────────────────────

function CreateProgramModal({ onClose, onCreated }: { onClose: () => void; onCreated: (id: number) => void }) {
  const [title, setTitle] = useState('')
  const [description, setDescription] = useState('')
  const [durationWeeks, setDurationWeeks] = useState(4)
  const [difficulty, setDifficulty] = useState('intermediate')
  const [isPublic, setIsPublic] = useState(false)
  const [error, setError] = useState('')

  const mutation = useMutation({
    mutationFn: () => trainerApi.createProgram({ title, description: description || undefined, duration_weeks: durationWeeks, difficulty, is_public: isPublic }),
    onSuccess: (data) => onCreated(data.id),
    onError: () => setError('Failed to create program'),
  })

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 p-4">
      <div className="bg-slate-800 border border-slate-700 rounded-2xl w-full max-w-md p-6 space-y-4">
        <h2 className="text-xl font-bold text-white">New Program</h2>
        {error && <p className="text-red-400 text-sm">{error}</p>}
        <div className="space-y-3">
          <input
            className="w-full bg-slate-700 border border-slate-600 rounded-lg px-3 py-2 text-white placeholder-slate-400 text-sm"
            placeholder="Program title *"
            value={title}
            onChange={e => setTitle(e.target.value)}
          />
          <textarea
            className="w-full bg-slate-700 border border-slate-600 rounded-lg px-3 py-2 text-white placeholder-slate-400 text-sm resize-none"
            rows={3}
            placeholder="Description (optional)"
            value={description}
            onChange={e => setDescription(e.target.value)}
          />
          <div className="flex gap-3">
            <div className="flex-1">
              <label className="block text-xs text-slate-400 mb-1">Duration (weeks)</label>
              <input
                type="number"
                min={1}
                max={52}
                className="w-full bg-slate-700 border border-slate-600 rounded-lg px-3 py-2 text-white text-sm"
                value={durationWeeks}
                onChange={e => setDurationWeeks(Number(e.target.value))}
              />
            </div>
            <div className="flex-1">
              <label className="block text-xs text-slate-400 mb-1">Difficulty</label>
              <select
                className="w-full bg-slate-700 border border-slate-600 rounded-lg px-3 py-2 text-white text-sm"
                value={difficulty}
                onChange={e => setDifficulty(e.target.value)}
              >
                <option value="beginner">Beginner</option>
                <option value="intermediate">Intermediate</option>
                <option value="advanced">Advanced</option>
              </select>
            </div>
          </div>
          <label className="flex items-center gap-2 cursor-pointer">
            <input type="checkbox" checked={isPublic} onChange={e => setIsPublic(e.target.checked)} className="rounded" />
            <span className="text-sm text-slate-300">Make public (visible to all users)</span>
          </label>
        </div>
        <div className="flex gap-3 pt-2">
          <button onClick={onClose} className="flex-1 py-2 rounded-lg border border-slate-600 text-slate-300 text-sm hover:bg-slate-700 transition-colors">
            Cancel
          </button>
          <button
            onClick={() => mutation.mutate()}
            disabled={!title.trim() || mutation.isPending}
            className="flex-1 py-2 rounded-lg bg-blue-600 hover:bg-blue-700 disabled:opacity-50 text-white text-sm font-medium transition-colors"
          >
            {mutation.isPending ? 'Creating…' : 'Create'}
          </button>
        </div>
      </div>
    </div>
  )
}

// ── Assign Modal ──────────────────────────────────────────────────────────────

function AssignModal({ programId, onClose }: { programId: number; onClose: () => void }) {
  const [username, setUsername] = useState('')
  const [success, setSuccess] = useState(false)
  const [error, setError] = useState('')
  const qc = useQueryClient()

  const mutation = useMutation({
    mutationFn: () => trainerApi.assignProgram(programId, username.trim()),
    onSuccess: () => { setSuccess(true); qc.invalidateQueries({ queryKey: ['trainer-clients'] }) },
    onError: (e: any) => setError(e?.response?.data?.detail ?? 'Failed to assign'),
  })

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 p-4">
      <div className="bg-slate-800 border border-slate-700 rounded-2xl w-full max-w-sm p-6 space-y-4">
        <h2 className="text-lg font-bold text-white">Assign Program</h2>
        {success ? (
          <div className="text-green-400 text-sm">Assigned successfully!</div>
        ) : (
          <>
            {error && <p className="text-red-400 text-sm">{error}</p>}
            <input
              className="w-full bg-slate-700 border border-slate-600 rounded-lg px-3 py-2 text-white placeholder-slate-400 text-sm"
              placeholder="Client username"
              value={username}
              onChange={e => setUsername(e.target.value)}
            />
          </>
        )}
        <div className="flex gap-3">
          <button onClick={onClose} className="flex-1 py-2 rounded-lg border border-slate-600 text-slate-300 text-sm hover:bg-slate-700 transition-colors">
            {success ? 'Close' : 'Cancel'}
          </button>
          {!success && (
            <button
              onClick={() => mutation.mutate()}
              disabled={!username.trim() || mutation.isPending}
              className="flex-1 py-2 rounded-lg bg-blue-600 hover:bg-blue-700 disabled:opacity-50 text-white text-sm font-medium transition-colors"
            >
              {mutation.isPending ? 'Assigning…' : 'Assign'}
            </button>
          )}
        </div>
      </div>
    </div>
  )
}

// ── Program Card ──────────────────────────────────────────────────────────────

function ProgramCard({ program, isOwner }: { program: WorkoutProgram; isOwner?: boolean }) {
  const navigate = useNavigate()
  const [showAssign, setShowAssign] = useState(false)

  return (
    <>
      <div
        className="bg-slate-800 border border-slate-700 rounded-xl p-5 cursor-pointer hover:border-slate-600 transition-colors space-y-3"
        onClick={() => navigate(`/trainer/programs/${program.id}`)}
      >
        <div className="flex items-start justify-between gap-2">
          <div>
            <h3 className="font-semibold text-white">{program.title}</h3>
            {program.description && <p className="text-sm text-slate-400 mt-0.5 line-clamp-2">{program.description}</p>}
          </div>
          <div className="flex items-center gap-1 flex-shrink-0">
            {!program.is_public && <Lock className="w-4 h-4 text-slate-500" />}
            <span className={`text-xs font-medium px-2 py-0.5 rounded-full ${DIFFICULTY_COLORS[program.difficulty] ?? 'bg-slate-700 text-slate-300'}`}>
              {program.difficulty}
            </span>
          </div>
        </div>
        <div className="flex items-center gap-4 text-xs text-slate-400">
          <span>📅 {program.duration_weeks}w</span>
          <span>📋 {program.days_count} days</span>
          <span>👥 {program.assignment_count} clients</span>
        </div>
        {isOwner && (
          <button
            onClick={e => { e.stopPropagation(); setShowAssign(true) }}
            className="w-full py-1.5 rounded-lg border border-slate-600 text-slate-300 text-xs hover:bg-slate-700 transition-colors"
          >
            Assign to Client
          </button>
        )}
      </div>
      {showAssign && <AssignModal programId={program.id} onClose={() => setShowAssign(false)} />}
    </>
  )
}

// ── Tabs ──────────────────────────────────────────────────────────────────────

function ProgramsTab({ isTrainer }: { isTrainer: boolean }) {
  const navigate = useNavigate()
  const [showCreate, setShowCreate] = useState(false)
  const qc = useQueryClient()

  const { data: programs = [], isLoading } = useQuery({
    queryKey: ['trainer-programs'],
    queryFn: trainerApi.listPrograms,
    enabled: isTrainer,
  })

  if (!isTrainer) {
    return (
      <div className="text-center py-16 text-slate-400">
        <BookOpen className="w-12 h-12 mx-auto mb-3 opacity-40" />
        <p>Become a trainer to manage programs.</p>
      </div>
    )
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <p className="text-slate-400 text-sm">{programs.length} program{programs.length !== 1 ? 's' : ''}</p>
        <button
          onClick={() => setShowCreate(true)}
          className="flex items-center gap-2 px-4 py-2 rounded-lg bg-blue-600 hover:bg-blue-700 text-white text-sm font-medium transition-colors"
        >
          <Plus className="w-4 h-4" /> New Program
        </button>
      </div>
      {isLoading ? (
        <p className="text-slate-400 text-sm">Loading…</p>
      ) : programs.length === 0 ? (
        <div className="text-center py-12 text-slate-500">
          <BookOpen className="w-10 h-10 mx-auto mb-2 opacity-40" />
          <p>No programs yet. Create your first one!</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {programs.map(p => <ProgramCard key={p.id} program={p} isOwner />)}
        </div>
      )}
      {showCreate && (
        <CreateProgramModal
          onClose={() => setShowCreate(false)}
          onCreated={(id) => {
            setShowCreate(false)
            qc.invalidateQueries({ queryKey: ['trainer-programs'] })
            navigate(`/trainer/programs/${id}`)
          }}
        />
      )}
    </div>
  )
}

function ClientsTab({ isTrainer }: { isTrainer: boolean }) {
  const { data: clients = [], isLoading } = useQuery<ClientStats[]>({
    queryKey: ['trainer-clients'],
    queryFn: trainerApi.getClients,
    enabled: isTrainer,
  })

  if (!isTrainer) {
    return (
      <div className="text-center py-16 text-slate-400">
        <Users className="w-12 h-12 mx-auto mb-3 opacity-40" />
        <p>Become a trainer to view clients.</p>
      </div>
    )
  }

  if (isLoading) return <p className="text-slate-400 text-sm">Loading…</p>

  if (clients.length === 0) {
    return (
      <div className="text-center py-12 text-slate-500">
        <Users className="w-10 h-10 mx-auto mb-2 opacity-40" />
        <p>No clients yet. Assign a program to get started.</p>
      </div>
    )
  }

  return (
    <div className="overflow-x-auto">
      <table className="w-full text-sm">
        <thead>
          <tr className="border-b border-slate-700 text-left text-slate-400">
            <th className="pb-3 pr-4">Username</th>
            <th className="pb-3 pr-4">Total Workouts</th>
            <th className="pb-3 pr-4">This Week</th>
            <th className="pb-3 pr-4">Streak</th>
            <th className="pb-3 pr-4">Level</th>
            <th className="pb-3">Programs</th>
          </tr>
        </thead>
        <tbody className="divide-y divide-slate-800">
          {clients.map(c => (
            <tr key={c.user_id} className="text-slate-300">
              <td className="py-3 pr-4 font-medium text-white">{c.username}</td>
              <td className="py-3 pr-4">{c.total_workouts}</td>
              <td className="py-3 pr-4">{c.this_week_workouts}</td>
              <td className="py-3 pr-4">{c.current_streak > 0 ? `🔥 ${c.current_streak}d` : '—'}</td>
              <td className="py-3 pr-4">
                <span className="w-6 h-6 rounded-full bg-violet-600 inline-flex items-center justify-center text-xs font-bold text-white">{c.level}</span>
              </td>
              <td className="py-3 text-xs text-slate-400">{c.assigned_programs.join(', ') || '—'}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}

function DiscoverTab() {
  const { data: programs = [], isLoading } = useQuery({
    queryKey: ['public-programs'],
    queryFn: trainerApi.listPublicPrograms,
  })

  if (isLoading) return <p className="text-slate-400 text-sm">Loading…</p>

  if (programs.length === 0) {
    return (
      <div className="text-center py-12 text-slate-500">
        <Star className="w-10 h-10 mx-auto mb-2 opacity-40" />
        <p>No public programs available yet.</p>
      </div>
    )
  }

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
      {programs.map(p => <ProgramCard key={p.id} program={p} />)}
    </div>
  )
}

// ── Main Page ─────────────────────────────────────────────────────────────────

type Tab = 'programs' | 'clients' | 'discover'

export default function TrainerPage() {
  const [tab, setTab] = useState<Tab>('programs')
  const { user, updateUser } = useAuthStore()
  const qc = useQueryClient()
  const isTrainer = user?.role === 'trainer' || user?.role === 'admin'

  const becomeMutation = useMutation({
    mutationFn: trainerApi.becomeTrainer,
    onSuccess: (data) => {
      updateUser({ role: data.role })
      qc.invalidateQueries({ queryKey: ['trainer-programs'] })
    },
  })

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between flex-wrap gap-4">
        <div>
          <h1 className="text-2xl font-bold text-white flex items-center gap-2">
            <Users className="w-6 h-6 text-blue-400" /> Trainer Hub
          </h1>
          {isTrainer && (
            <p className="text-slate-400 text-sm mt-0.5">Manage programs, clients, and discover new content.</p>
          )}
        </div>
        {!isTrainer && (
          <button
            onClick={() => becomeMutation.mutate()}
            disabled={becomeMutation.isPending}
            className="flex items-center gap-2 px-5 py-2.5 rounded-lg bg-blue-600 hover:bg-blue-700 disabled:opacity-50 text-white font-medium transition-colors"
          >
            <Star className="w-4 h-4" />
            {becomeMutation.isPending ? 'Upgrading…' : 'Become a Trainer'}
          </button>
        )}
        {isTrainer && (
          <span className="px-3 py-1 rounded-full bg-blue-900/50 text-blue-400 text-sm font-medium border border-blue-800">
            ✓ Trainer
          </span>
        )}
      </div>

      {/* Tabs */}
      <div className="flex gap-1 border-b border-slate-700">
        {(['programs', 'clients', 'discover'] as Tab[]).map(t => (
          <button
            key={t}
            onClick={() => setTab(t)}
            className={`px-4 py-2 text-sm font-medium capitalize transition-colors border-b-2 -mb-px ${
              tab === t ? 'border-blue-500 text-white' : 'border-transparent text-slate-400 hover:text-white'
            }`}
          >
            {t}
          </button>
        ))}
      </div>

      {/* Tab Content */}
      {tab === 'programs' && <ProgramsTab isTrainer={isTrainer} />}
      {tab === 'clients' && <ClientsTab isTrainer={isTrainer} />}
      {tab === 'discover' && <DiscoverTab />}
    </div>
  )
}

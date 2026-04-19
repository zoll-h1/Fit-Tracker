import { useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { ArrowLeft, Trash2, UserPlus, ChevronDown, ChevronUp } from 'lucide-react'
import { trainerApi, type ProgramDay } from '@/api/trainer'
import { useAuthStore } from '@/stores/authStore'

const DIFFICULTY_COLORS: Record<string, string> = {
  beginner: 'bg-green-900/50 text-green-400',
  intermediate: 'bg-yellow-900/50 text-yellow-400',
  advanced: 'bg-red-900/50 text-red-400',
}

const DAY_NAMES = ['', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']

function AssignModal({ programId, onClose }: { programId: number; onClose: () => void }) {
  const [username, setUsername] = useState('')
  const [success, setSuccess] = useState(false)
  const [error, setError] = useState('')

  const mutation = useMutation({
    mutationFn: () => trainerApi.assignProgram(programId, username.trim()),
    onSuccess: () => setSuccess(true),
    onError: (e: any) => setError(e?.response?.data?.detail ?? 'Failed to assign'),
  })

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 p-4">
      <div className="bg-slate-800 border border-slate-700 rounded-2xl w-full max-w-sm p-6 space-y-4">
        <h2 className="text-lg font-bold text-white">Assign to Client</h2>
        {success ? (
          <p className="text-green-400 text-sm">Program assigned successfully!</p>
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

function DayCard({ day }: { day: ProgramDay }) {
  const [expanded, setExpanded] = useState(true)

  return (
    <div className="bg-slate-800 border border-slate-700 rounded-xl overflow-hidden">
      <button
        className="w-full flex items-center justify-between px-4 py-3 hover:bg-slate-700/50 transition-colors"
        onClick={() => setExpanded(v => !v)}
      >
        <div className="flex items-center gap-2">
          <span className="text-xs font-medium px-2 py-0.5 rounded bg-slate-700 text-slate-300">
            {DAY_NAMES[day.day_number] ?? `Day ${day.day_number}`}
          </span>
          <span className="text-sm font-medium text-white">{day.name ?? `Week ${day.week_number} · Day ${day.day_number}`}</span>
          <span className="text-xs text-slate-500">{day.exercises.length} exercises</span>
        </div>
        {expanded ? <ChevronUp className="w-4 h-4 text-slate-400" /> : <ChevronDown className="w-4 h-4 text-slate-400" />}
      </button>
      {expanded && day.exercises.length > 0 && (
        <div className="border-t border-slate-700 divide-y divide-slate-700/50">
          {day.exercises.map(ex => (
            <div key={ex.id} className="px-4 py-2.5 flex items-center justify-between">
              <div>
                <p className="text-sm text-white font-medium">{ex.exercise_name}</p>
                <p className="text-xs text-slate-400 mt-0.5">
                  {ex.sets} sets
                  {ex.reps ? ` × ${ex.reps} reps` : ''}
                  {ex.weight_note ? ` @ ${ex.weight_note}` : ''}
                </p>
              </div>
              <span className="text-xs text-slate-500">{ex.rest_seconds}s rest</span>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}

export default function ProgramDetailPage() {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const qc = useQueryClient()
  const { user } = useAuthStore()
  const [showAssign, setShowAssign] = useState(false)

  const programId = Number(id)

  const { data: program, isLoading, error } = useQuery({
    queryKey: ['program', programId],
    queryFn: () => trainerApi.getProgram(programId),
    enabled: !!programId,
  })

  const deleteMutation = useMutation({
    mutationFn: () => trainerApi.deleteProgram(programId),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['trainer-programs'] })
      navigate('/trainer')
    },
  })

  if (isLoading) {
    return <div className="flex items-center justify-center h-64 text-slate-400">Loading…</div>
  }

  if (error || !program) {
    return <div className="text-center py-16 text-slate-400">Program not found.</div>
  }

  const isOwner = user?.id === program.trainer_id || user?.role === 'admin'

  // Group days by week
  const weeks: Record<number, typeof program.days> = {}
  for (const day of program.days) {
    if (!weeks[day.week_number]) weeks[day.week_number] = []
    weeks[day.week_number].push(day)
  }
  const weekNumbers = Object.keys(weeks).map(Number).sort((a, b) => a - b)

  return (
    <div className="space-y-6 max-w-3xl">
      {/* Back */}
      <button onClick={() => navigate('/trainer')} className="flex items-center gap-2 text-slate-400 hover:text-white text-sm transition-colors">
        <ArrowLeft className="w-4 h-4" /> Back to Trainer Hub
      </button>

      {/* Header */}
      <div className="bg-slate-800 border border-slate-700 rounded-2xl p-6 space-y-3">
        <div className="flex items-start justify-between gap-4 flex-wrap">
          <div className="min-w-0">
            <h1 className="text-2xl font-bold text-white">{program.title}</h1>
            {program.description && <p className="text-slate-400 mt-1">{program.description}</p>}
          </div>
          <div className="flex items-center gap-2 flex-wrap">
            <span className={`text-xs font-medium px-2 py-1 rounded-full ${DIFFICULTY_COLORS[program.difficulty] ?? 'bg-slate-700 text-slate-300'}`}>
              {program.difficulty}
            </span>
            <span className="text-xs text-slate-400 bg-slate-700 px-2 py-1 rounded-full">
              {program.duration_weeks} weeks
            </span>
            <span className="text-xs text-slate-400 bg-slate-700 px-2 py-1 rounded-full">
              {program.days.length} days
            </span>
          </div>
        </div>

        <div className="flex gap-3 pt-2 flex-wrap">
          {isOwner && (
            <>
              <button
                onClick={() => setShowAssign(true)}
                className="flex items-center gap-2 px-4 py-2 rounded-lg bg-blue-600 hover:bg-blue-700 text-white text-sm font-medium transition-colors"
              >
                <UserPlus className="w-4 h-4" /> Assign to Client
              </button>
              <button
                onClick={() => { if (confirm('Delete this program?')) deleteMutation.mutate() }}
                disabled={deleteMutation.isPending}
                className="flex items-center gap-2 px-4 py-2 rounded-lg border border-red-800 hover:bg-red-900/30 text-red-400 text-sm transition-colors"
              >
                <Trash2 className="w-4 h-4" /> Delete
              </button>
            </>
          )}
        </div>
      </div>

      {/* Weeks */}
      {weekNumbers.length === 0 ? (
        <div className="text-center py-12 text-slate-500">
          <p>No days have been added to this program yet.</p>
        </div>
      ) : (
        weekNumbers.map(wk => (
          <div key={wk} className="space-y-3">
            <h2 className="text-lg font-semibold text-white">Week {wk}</h2>
            <div className="space-y-2">
              {weeks[wk].map(d => <DayCard key={d.id} day={d} />)}
            </div>
          </div>
        ))
      )}

      {showAssign && <AssignModal programId={programId} onClose={() => setShowAssign(false)} />}
    </div>
  )
}

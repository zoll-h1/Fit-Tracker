import { useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { ArrowLeft, Trash2, UserPlus, ChevronDown, ChevronUp, Plus, X, Search } from 'lucide-react'
import { trainerApi, type ProgramDay, type ProgramExercise } from '@/api/trainer'
import { exercisesApi } from '@/api/exercises'
import { useAuthStore } from '@/stores/authStore'

const DIFFICULTY_COLORS: Record<string, string> = {
  beginner: 'bg-green-900/50 text-green-400',
  intermediate: 'bg-yellow-900/50 text-yellow-400',
  advanced: 'bg-red-900/50 text-red-400',
}

const DAY_NAMES = ['', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']

// ── Add Exercise Modal ────────────────────────────────────────────────────────

function AddExerciseModal({ dayId, onClose, onAdded }: { dayId: number; onClose: () => void; onAdded: (ex: ProgramExercise) => void }) {
  const [search, setSearch] = useState('')
  const [selectedId, setSelectedId] = useState<number | null>(null)
  const [sets, setSets] = useState(3)
  const [reps, setReps] = useState('8-12')
  const [weightNote, setWeightNote] = useState('')
  const [restSeconds, setRestSeconds] = useState(90)
  const [error, setError] = useState('')

  const { data: exercises = [] } = useQuery({
    queryKey: ['exercise-library', search],
    queryFn: () => exercisesApi.list({ search: search || undefined, per_page: 30 }),
    select: (d: any) => d.items ?? d,
  })

  const mutation = useMutation({
    mutationFn: () => trainerApi.addExercise(dayId, {
      exercise_id: selectedId!,
      sets,
      reps: reps || undefined,
      weight_note: weightNote || undefined,
      rest_seconds: restSeconds,
    }),
    onSuccess: (ex) => { onAdded(ex); onClose() },
    onError: (e: any) => setError(e?.response?.data?.detail ?? 'Failed to add exercise'),
  })

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 p-4">
      <div className="bg-slate-800 border border-slate-700 rounded-2xl w-full max-w-lg flex flex-col max-h-[90vh]">
        <div className="p-5 border-b border-slate-700 flex items-center justify-between">
          <h2 className="text-lg font-bold text-white">Add Exercise</h2>
          <button onClick={onClose} className="text-slate-400 hover:text-white"><X className="w-5 h-5" /></button>
        </div>
        {error && <p className="mx-5 mt-3 text-red-400 text-sm">{error}</p>}
        <div className="p-5 space-y-4 overflow-y-auto flex-1">
          {/* Search */}
          <div className="relative">
            <Search className="absolute left-3 top-2.5 w-4 h-4 text-slate-400" />
            <input
              className="w-full bg-slate-700 border border-slate-600 rounded-lg pl-9 pr-3 py-2 text-white placeholder-slate-400 text-sm"
              placeholder="Search exercises…"
              value={search}
              onChange={e => setSearch(e.target.value)}
            />
          </div>

          {/* Exercise list */}
          <div className="space-y-1 max-h-52 overflow-y-auto">
            {exercises.map((ex: any) => (
              <button
                key={ex.id}
                onClick={() => setSelectedId(ex.id)}
                className={`w-full text-left px-3 py-2 rounded-lg text-sm transition-colors ${
                  selectedId === ex.id
                    ? 'bg-blue-600 text-white'
                    : 'text-slate-300 hover:bg-slate-700'
                }`}
              >
                <span className="font-medium">{ex.name}</span>
                {ex.muscle_primary && <span className="text-xs ml-2 opacity-60">{ex.muscle_primary}</span>}
              </button>
            ))}
          </div>

          {/* Config */}
          {selectedId && (
            <div className="grid grid-cols-2 gap-3 pt-2 border-t border-slate-700">
              <div>
                <label className="block text-xs text-slate-400 mb-1">Sets</label>
                <input type="number" min={1} max={20} className="w-full bg-slate-700 border border-slate-600 rounded-lg px-3 py-2 text-white text-sm"
                  value={sets} onChange={e => setSets(Number(e.target.value))} />
              </div>
              <div>
                <label className="block text-xs text-slate-400 mb-1">Reps</label>
                <input className="w-full bg-slate-700 border border-slate-600 rounded-lg px-3 py-2 text-white text-sm placeholder-slate-500"
                  placeholder="8-12" value={reps} onChange={e => setReps(e.target.value)} />
              </div>
              <div>
                <label className="block text-xs text-slate-400 mb-1">Weight Note</label>
                <input className="w-full bg-slate-700 border border-slate-600 rounded-lg px-3 py-2 text-white text-sm placeholder-slate-500"
                  placeholder="RPE 7 / 70% 1RM" value={weightNote} onChange={e => setWeightNote(e.target.value)} />
              </div>
              <div>
                <label className="block text-xs text-slate-400 mb-1">Rest (sec)</label>
                <input type="number" min={0} className="w-full bg-slate-700 border border-slate-600 rounded-lg px-3 py-2 text-white text-sm"
                  value={restSeconds} onChange={e => setRestSeconds(Number(e.target.value))} />
              </div>
            </div>
          )}
        </div>

        <div className="p-5 border-t border-slate-700 flex gap-3">
          <button onClick={onClose} className="flex-1 py-2 rounded-lg border border-slate-600 text-slate-300 text-sm hover:bg-slate-700 transition-colors">
            Cancel
          </button>
          <button
            onClick={() => mutation.mutate()}
            disabled={!selectedId || mutation.isPending}
            className="flex-1 py-2 rounded-lg bg-blue-600 hover:bg-blue-700 disabled:opacity-50 text-white text-sm font-medium transition-colors"
          >
            {mutation.isPending ? 'Adding…' : 'Add Exercise'}
          </button>
        </div>
      </div>
    </div>
  )
}

// ── Add Day Modal ─────────────────────────────────────────────────────────────

function AddDayModal({ programId, onClose, onAdded }: { programId: number; onClose: () => void; onAdded: (day: ProgramDay) => void }) {
  const [weekNumber, setWeekNumber] = useState(1)
  const [dayNumber, setDayNumber] = useState(1)
  const [name, setName] = useState('')
  const [error, setError] = useState('')

  const mutation = useMutation({
    mutationFn: () => trainerApi.addDay(programId, { week_number: weekNumber, day_number: dayNumber, name: name || undefined }),
    onSuccess: (day) => { onAdded(day); onClose() },
    onError: (e: any) => setError(e?.response?.data?.detail ?? 'Failed to add day'),
  })

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 p-4">
      <div className="bg-slate-800 border border-slate-700 rounded-2xl w-full max-w-sm p-6 space-y-4">
        <h2 className="text-lg font-bold text-white">Add Training Day</h2>
        {error && <p className="text-red-400 text-sm">{error}</p>}
        <div className="space-y-3">
          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="block text-xs text-slate-400 mb-1">Week</label>
              <input type="number" min={1} className="w-full bg-slate-700 border border-slate-600 rounded-lg px-3 py-2 text-white text-sm"
                value={weekNumber} onChange={e => setWeekNumber(Number(e.target.value))} />
            </div>
            <div>
              <label className="block text-xs text-slate-400 mb-1">Day</label>
              <select className="w-full bg-slate-700 border border-slate-600 rounded-lg px-3 py-2 text-white text-sm"
                value={dayNumber} onChange={e => setDayNumber(Number(e.target.value))}>
                {DAY_NAMES.slice(1).map((d, i) => (
                  <option key={i + 1} value={i + 1}>{d}</option>
                ))}
              </select>
            </div>
          </div>
          <div>
            <label className="block text-xs text-slate-400 mb-1">Day Name (optional)</label>
            <input className="w-full bg-slate-700 border border-slate-600 rounded-lg px-3 py-2 text-white text-sm placeholder-slate-500"
              placeholder="e.g. Push Day, Upper Body…" value={name} onChange={e => setName(e.target.value)} />
          </div>
        </div>
        <div className="flex gap-3 pt-1">
          <button onClick={onClose} className="flex-1 py-2 rounded-lg border border-slate-600 text-slate-300 text-sm hover:bg-slate-700 transition-colors">
            Cancel
          </button>
          <button
            onClick={() => mutation.mutate()}
            disabled={mutation.isPending}
            className="flex-1 py-2 rounded-lg bg-blue-600 hover:bg-blue-700 disabled:opacity-50 text-white text-sm font-medium transition-colors"
          >
            {mutation.isPending ? 'Adding…' : 'Add Day'}
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

// ── Day Card ──────────────────────────────────────────────────────────────────

function DayCard({ day, isOwner, programId }: { day: ProgramDay; isOwner: boolean; programId: number }) {
  const [expanded, setExpanded] = useState(true)
  const [showAddExercise, setShowAddExercise] = useState(false)
  const qc = useQueryClient()

  const deleteDayMutation = useMutation({
    mutationFn: () => trainerApi.deleteDay(day.id),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['program', programId] }),
  })

  const deleteExerciseMutation = useMutation({
    mutationFn: (exId: number) => trainerApi.deleteExercise(exId),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['program', programId] }),
  })

  return (
    <>
      <div className="bg-slate-800 border border-slate-700 rounded-xl overflow-hidden">
        <div className="flex items-center justify-between px-4 py-3 hover:bg-slate-700/30 transition-colors">
          <button
            className="flex items-center gap-2 flex-1 text-left"
            onClick={() => setExpanded(v => !v)}
          >
            <span className="text-xs font-medium px-2 py-0.5 rounded bg-slate-700 text-slate-300">
              {DAY_NAMES[day.day_number] ?? `Day ${day.day_number}`}
            </span>
            <span className="text-sm font-medium text-white">{day.name ?? `Week ${day.week_number} · Day ${day.day_number}`}</span>
            <span className="text-xs text-slate-500">{day.exercises.length} exercises</span>
            {expanded ? <ChevronUp className="w-4 h-4 text-slate-400 ml-1" /> : <ChevronDown className="w-4 h-4 text-slate-400 ml-1" />}
          </button>
          {isOwner && (
            <div className="flex items-center gap-1 ml-2">
              <button
                onClick={() => setShowAddExercise(true)}
                className="flex items-center gap-1 px-2 py-1 rounded-lg text-xs text-blue-400 hover:bg-blue-900/30 transition-colors"
                title="Add exercise"
              >
                <Plus className="w-3.5 h-3.5" /> Add
              </button>
              <button
                onClick={() => { if (confirm('Delete this day and all its exercises?')) deleteDayMutation.mutate() }}
                className="p-1 rounded text-slate-500 hover:text-red-400 hover:bg-red-900/20 transition-colors"
                title="Delete day"
              >
                <Trash2 className="w-3.5 h-3.5" />
              </button>
            </div>
          )}
        </div>

        {expanded && (
          <div className="border-t border-slate-700">
            {day.exercises.length === 0 ? (
              <div className="px-4 py-3 text-xs text-slate-500 italic">
                No exercises yet.{isOwner && ' Click "Add" to add exercises.'}
              </div>
            ) : (
              <div className="divide-y divide-slate-700/50">
                {day.exercises.map(ex => (
                  <div key={ex.id} className="px-4 py-2.5 flex items-center justify-between group">
                    <div>
                      <p className="text-sm text-white font-medium">{ex.exercise_name}</p>
                      <p className="text-xs text-slate-400 mt-0.5">
                        {ex.sets} sets
                        {ex.reps ? ` × ${ex.reps} reps` : ''}
                        {ex.weight_note ? ` @ ${ex.weight_note}` : ''}
                        {' · '}{ex.rest_seconds}s rest
                      </p>
                    </div>
                    {isOwner && (
                      <button
                        onClick={() => { if (confirm('Remove this exercise?')) deleteExerciseMutation.mutate(ex.id) }}
                        className="opacity-0 group-hover:opacity-100 p-1 rounded text-slate-500 hover:text-red-400 transition-all"
                      >
                        <X className="w-3.5 h-3.5" />
                      </button>
                    )}
                  </div>
                ))}
              </div>
            )}
          </div>
        )}
      </div>

      {showAddExercise && (
        <AddExerciseModal
          dayId={day.id}
          onClose={() => setShowAddExercise(false)}
          onAdded={() => qc.invalidateQueries({ queryKey: ['program', programId] })}
        />
      )}
    </>
  )
}

// ── Main Page ─────────────────────────────────────────────────────────────────

export default function ProgramDetailPage() {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const qc = useQueryClient()
  const { user } = useAuthStore()
  const [showAssign, setShowAssign] = useState(false)
  const [showAddDay, setShowAddDay] = useState(false)

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
                onClick={() => setShowAddDay(true)}
                className="flex items-center gap-2 px-4 py-2 rounded-lg bg-green-700 hover:bg-green-600 text-white text-sm font-medium transition-colors"
              >
                <Plus className="w-4 h-4" /> Add Day
              </button>
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
        <div className="text-center py-12 border border-dashed border-slate-700 rounded-xl text-slate-500">
          <p className="text-lg mb-1">No days yet</p>
          {isOwner && (
            <p className="text-sm">Click <span className="text-green-400">"Add Day"</span> to start building your program.</p>
          )}
        </div>
      ) : (
        weekNumbers.map(wk => (
          <div key={wk} className="space-y-3">
            <h2 className="text-lg font-semibold text-white">Week {wk}</h2>
            <div className="space-y-2">
              {weeks[wk].map(d => (
                <DayCard key={d.id} day={d} isOwner={isOwner} programId={programId} />
              ))}
            </div>
          </div>
        ))
      )}

      {showAssign && <AssignModal programId={programId} onClose={() => setShowAssign(false)} />}
      {showAddDay && (
        <AddDayModal
          programId={programId}
          onClose={() => setShowAddDay(false)}
          onAdded={() => qc.invalidateQueries({ queryKey: ['program', programId] })}
        />
      )}
    </div>
  )
}

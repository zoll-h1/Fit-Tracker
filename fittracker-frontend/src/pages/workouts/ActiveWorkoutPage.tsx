import { useEffect, useRef, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Timer, Plus, CheckCircle, X, Dumbbell, Heart } from 'lucide-react';
import { useMutation } from '@tanstack/react-query';
import { workoutsApi, type WorkoutSession, type WorkoutExercise, type WorkoutSet } from '@/api/workouts';
import { useWorkoutStore } from '@/stores/workoutStore';
import AddExerciseModal from '@/components/workout/AddExerciseModal';
import RestTimerModal from '@/components/workout/RestTimerModal';
import FinishWorkoutModal from '@/components/workout/FinishWorkoutModal';

function formatTime(seconds: number): string {
  const h = Math.floor(seconds / 3600);
  const m = Math.floor((seconds % 3600) / 60);
  const s = seconds % 60;
  if (h > 0) return `${h}:${String(m).padStart(2, '0')}:${String(s).padStart(2, '0')}`;
  return `${String(m).padStart(2, '0')}:${String(s).padStart(2, '0')}`;
}

export default function ActiveWorkoutPage() {
  const navigate = useNavigate();
  const {
    activeSession,
    elapsedSeconds,
    setElapsed,
    addExercise,
    removeExercise,
    addSet,
    updateSet,
    removeSet,
    restTimer,
    clearRestTimer,
    clearSession,
  } = useWorkoutStore();

  const [showAddExercise, setShowAddExercise] = useState(false);
  const [showFinish, setShowFinish] = useState(false);
  const [sessionType, setSessionType] = useState<'strength' | 'cardio'>('strength');
  const [distanceKm, setDistanceKm] = useState('');
  const [avgPace, setAvgPace] = useState('');
  const [heartRate, setHeartRate] = useState('');
  const intervalRef = useRef<ReturnType<typeof setInterval> | null>(null);

  useEffect(() => {
    if (!activeSession) {
      navigate('/workouts');
      return;
    }
    intervalRef.current = setInterval(() => setElapsed(elapsedSeconds + 1), 1000);
    return () => {
      if (intervalRef.current) clearInterval(intervalRef.current);
    };
  }, [activeSession, elapsedSeconds]);

  if (!activeSession) return null;

  const handleFinish = async () => {
    if (sessionType === 'cardio') {
      try {
        await workoutsApi.updateCardio(activeSession.id, {
          session_type: 'cardio',
          distance_km: distanceKm ? parseFloat(distanceKm) : undefined,
          avg_pace_min_km: avgPace ? parseFloat(avgPace) : undefined,
          avg_heart_rate: heartRate ? parseInt(heartRate) : undefined,
        });
      } catch {
        // non-blocking
      }
    }
    setShowFinish(true);
  };

  return (
    <div className="p-4 pb-24 space-y-4 max-w-2xl mx-auto">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-xl font-bold text-white">{activeSession.name}</h1>
          <div className="flex items-center gap-2 text-slate-400 text-sm mt-0.5">
            <Timer className="w-4 h-4" />
            <span>{formatTime(elapsedSeconds)}</span>
          </div>
        </div>
        <button
          onClick={handleFinish}
          className="px-4 py-2 bg-violet-600 hover:bg-violet-500 text-white rounded-lg font-medium text-sm transition-colors"
        >
          Finish
        </button>
      </div>

      {/* Session type toggle */}
      <div className="flex gap-2">
        {(['strength', 'cardio'] as const).map((type) => (
          <button
            key={type}
            onClick={() => setSessionType(type)}
            className={`px-4 py-1.5 rounded-lg text-sm font-medium transition-colors capitalize ${
              sessionType === type
                ? 'bg-violet-600 text-white'
                : 'bg-slate-800 border border-slate-700 text-slate-400 hover:text-white'
            }`}
          >
            {type}
          </button>
        ))}
      </div>

      {/* Cardio fields */}
      {sessionType === 'cardio' && (
        <div className="bg-slate-800 border border-violet-500/30 rounded-xl p-4 space-y-3">
          <div className="flex items-center gap-2 text-violet-400 text-sm font-medium mb-1">
            <Heart className="w-4 h-4" />
            Cardio Data
          </div>
          <div className="grid grid-cols-3 gap-3">
            <div>
              <label className="text-xs text-slate-400 block mb-1">Distance (km)</label>
              <input
                type="number"
                value={distanceKm}
                onChange={(e) => setDistanceKm(e.target.value)}
                placeholder="0.0"
                step="0.1"
                className="w-full bg-slate-700 border border-slate-600 rounded px-2 py-1.5 text-white text-sm focus:outline-none focus:border-violet-500"
              />
            </div>
            <div>
              <label className="text-xs text-slate-400 block mb-1">Avg Pace (min/km)</label>
              <input
                type="number"
                value={avgPace}
                onChange={(e) => setAvgPace(e.target.value)}
                placeholder="0.0"
                step="0.1"
                className="w-full bg-slate-700 border border-slate-600 rounded px-2 py-1.5 text-white text-sm focus:outline-none focus:border-violet-500"
              />
            </div>
            <div>
              <label className="text-xs text-slate-400 block mb-1">Heart Rate (BPM)</label>
              <input
                type="number"
                value={heartRate}
                onChange={(e) => setHeartRate(e.target.value)}
                placeholder="0"
                className="w-full bg-slate-700 border border-slate-600 rounded px-2 py-1.5 text-white text-sm focus:outline-none focus:border-violet-500"
              />
            </div>
          </div>
        </div>
      )}

      {/* Exercises */}
      {activeSession.exercises.length === 0 ? (
        <div className="flex flex-col items-center justify-center py-16 text-slate-500">
          <Dumbbell className="w-12 h-12 mb-4 opacity-40" />
          <p className="text-sm">Add your first exercise to get started</p>
        </div>
      ) : (
        activeSession.exercises.map((we) => (
          <ExerciseBlock
            key={we.id}
            sessionId={activeSession.id}
            workoutExercise={we}
            onAddSet={(set) => addSet(we.id, set)}
            onUpdateSet={(set) => updateSet(we.id, set)}
            onRemoveSet={(setId) => removeSet(we.id, setId)}
            onRemoveExercise={() => removeExercise(we.id)}
          />
        ))
      )}

      {/* Add Exercise Button */}
      <button
        onClick={() => setShowAddExercise(true)}
        className="w-full py-3 border-2 border-dashed border-slate-700 hover:border-violet-500 rounded-xl text-slate-400 hover:text-violet-400 transition-colors flex items-center justify-center gap-2 text-sm font-medium"
      >
        <Plus className="w-4 h-4" />
        Add Exercise
      </button>

      {/* Modals */}
      {showAddExercise && (
        <AddExerciseModal
          sessionId={activeSession.id}
          currentCount={activeSession.exercises.length}
          onAdd={(exercise) => { addExercise(exercise); setShowAddExercise(false); }}
          onClose={() => setShowAddExercise(false)}
        />
      )}
      {restTimer.active && (
        <RestTimerModal
          remaining={restTimer.remaining}
          onClose={clearRestTimer}
        />
      )}
      {showFinish && (
        <FinishWorkoutModal
          session={activeSession}
          elapsed={elapsedSeconds}
          onClose={() => setShowFinish(false)}
          onFinished={() => { clearSession(); navigate('/workouts'); }}
        />
      )}
    </div>
  );
}

// ── ExerciseBlock ─────────────────────────────────────────────────────────────

interface ExerciseBlockProps {
  sessionId: number;
  workoutExercise: WorkoutExercise;
  onAddSet: (set: WorkoutSet) => void;
  onUpdateSet: (set: WorkoutSet) => void;
  onRemoveSet: (setId: number) => void;
  onRemoveExercise: () => void;
}

function ExerciseBlock({
  sessionId,
  workoutExercise: we,
  onAddSet,
  onUpdateSet,
  onRemoveSet,
  onRemoveExercise,
}: ExerciseBlockProps) {
  const { startRestTimer } = useWorkoutStore();

  const addSetMutation = useMutation({
    mutationFn: () =>
      workoutsApi.addSet(sessionId, we.id, {
        set_number: we.sets.length + 1,
        set_type: 'normal',
      }),
    onSuccess: onAddSet,
  });

  const removeExMutation = useMutation({
    mutationFn: () => workoutsApi.removeExercise(sessionId, we.id),
    onSuccess: onRemoveExercise,
  });

  return (
    <div className="bg-slate-800 border border-slate-700 rounded-xl p-4 space-y-3">
      {/* Exercise header */}
      <div className="flex items-center justify-between">
        <h3 className="font-semibold text-white">Exercise #{we.exercise_order}</h3>
        <button
          onClick={() => removeExMutation.mutate()}
          className="text-slate-500 hover:text-rose-400 transition-colors"
        >
          <X className="w-4 h-4" />
        </button>
      </div>

      {/* Set table header */}
      {we.sets.length > 0 && (
        <div className="grid grid-cols-4 gap-2 text-xs text-slate-500 px-1">
          <span>Set</span>
          <span>Previous</span>
          <span>kg</span>
          <span>Reps</span>
        </div>
      )}

      {/* Sets */}
      {we.sets.map((ws) => (
        <SetRow
          key={ws.id}
          sessionId={sessionId}
          exerciseId={we.id}
          set={ws}
          onUpdate={onUpdateSet}
          onRemove={() => { onRemoveSet(ws.id); }}
          onComplete={() => startRestTimer(we.rest_seconds, we.id)}
        />
      ))}

      {/* Add set */}
      <button
        onClick={() => addSetMutation.mutate()}
        disabled={addSetMutation.isPending}
        className="w-full py-2 text-sm text-violet-400 hover:text-violet-300 border border-violet-500/30 hover:border-violet-500 rounded-lg transition-colors flex items-center justify-center gap-1"
      >
        <Plus className="w-3.5 h-3.5" />
        Add Set
      </button>
    </div>
  );
}

// ── SetRow ────────────────────────────────────────────────────────────────────

interface SetRowProps {
  sessionId: number;
  exerciseId: number;
  set: WorkoutSet;
  onUpdate: (set: WorkoutSet) => void;
  onRemove: () => void;
  onComplete: () => void;
}

function SetRow({ sessionId, exerciseId, set, onUpdate, onRemove, onComplete }: SetRowProps) {
  const [weight, setWeight] = useState(set.weight_kg ? String(set.weight_kg) : '');
  const [reps, setReps] = useState(set.reps ? String(set.reps) : '');

  const completeMutation = useMutation({
    mutationFn: () =>
      workoutsApi.updateSet(sessionId, exerciseId, set.id, {
        ...set,
        weight_kg: weight ? parseFloat(weight) : null,
        reps: reps ? parseInt(reps) : null,
        completed: true,
      }),
    onSuccess: (updated) => {
      onUpdate(updated);
      if (!set.completed) onComplete();
    },
  });

  const deleteMutation = useMutation({
    mutationFn: () => workoutsApi.deleteSet(sessionId, exerciseId, set.id),
    onSuccess: onRemove,
  });

  return (
    <div
      className={`grid grid-cols-4 gap-2 items-center px-1 py-1 rounded-lg transition-colors ${
        set.completed ? 'bg-emerald-500/10' : ''
      }`}
    >
      <div className="flex items-center gap-1.5">
        <span className="text-slate-400 text-sm w-5">{set.set_number}</span>
        {set.is_pr && (
          <span className="text-[10px] font-bold text-amber-400 bg-amber-400/10 px-1 rounded">PR</span>
        )}
      </div>
      <span className="text-slate-500 text-xs">—</span>
      <input
        type="number"
        value={weight}
        onChange={(e) => setWeight(e.target.value)}
        placeholder="0"
        disabled={set.completed}
        className="w-full bg-slate-700 border border-slate-600 rounded px-2 py-1 text-white text-sm focus:outline-none focus:border-violet-500 disabled:opacity-50"
      />
      <div className="flex items-center gap-1">
        <input
          type="number"
          value={reps}
          onChange={(e) => setReps(e.target.value)}
          placeholder="0"
          disabled={set.completed}
          className="w-full bg-slate-700 border border-slate-600 rounded px-2 py-1 text-white text-sm focus:outline-none focus:border-violet-500 disabled:opacity-50"
        />
        <button
          onClick={() => set.completed ? deleteMutation.mutate() : completeMutation.mutate()}
          className={`ml-1 transition-colors ${
            set.completed
              ? 'text-emerald-400 hover:text-rose-400'
              : 'text-slate-500 hover:text-emerald-400'
          }`}
        >
          <CheckCircle className="w-5 h-5" />
        </button>
      </div>
    </div>
  );
}

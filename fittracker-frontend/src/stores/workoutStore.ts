import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import type { WorkoutSession, WorkoutExercise, WorkoutSet } from '@/api/workouts';

interface WorkoutState {
  activeSession: WorkoutSession | null;
  elapsedSeconds: number;
  restTimer: { active: boolean; remaining: number; exerciseId: number | null };

  setActiveSession: (session: WorkoutSession | null) => void;
  updateSession: (session: WorkoutSession) => void;
  addExercise: (exercise: WorkoutExercise) => void;
  removeExercise: (exerciseId: number) => void;
  addSet: (exerciseId: number, set: WorkoutSet) => void;
  updateSet: (exerciseId: number, set: WorkoutSet) => void;
  removeSet: (exerciseId: number, setId: number) => void;
  setElapsed: (s: number) => void;
  startRestTimer: (seconds: number, exerciseId: number) => void;
  tickRestTimer: () => void;
  clearRestTimer: () => void;
  clearSession: () => void;
}

export const useWorkoutStore = create<WorkoutState>()(
  persist(
    (set, get) => ({
      activeSession: null,
      elapsedSeconds: 0,
      restTimer: { active: false, remaining: 0, exerciseId: null },

      setActiveSession: (session) => set({ activeSession: session, elapsedSeconds: 0 }),

      updateSession: (session) => set({ activeSession: session }),

      addExercise: (exercise) =>
        set((s) => {
          if (!s.activeSession) return {};
          return {
            activeSession: {
              ...s.activeSession,
              exercises: [...s.activeSession.exercises, exercise],
            },
          };
        }),

      removeExercise: (exerciseId) =>
        set((s) => {
          if (!s.activeSession) return {};
          return {
            activeSession: {
              ...s.activeSession,
              exercises: s.activeSession.exercises.filter((e) => e.id !== exerciseId),
            },
          };
        }),

      addSet: (exerciseId, newSet) =>
        set((s) => {
          if (!s.activeSession) return {};
          return {
            activeSession: {
              ...s.activeSession,
              exercises: s.activeSession.exercises.map((e) =>
                e.id === exerciseId ? { ...e, sets: [...e.sets, newSet] } : e,
              ),
            },
          };
        }),

      updateSet: (exerciseId, updatedSet) =>
        set((s) => {
          if (!s.activeSession) return {};
          return {
            activeSession: {
              ...s.activeSession,
              exercises: s.activeSession.exercises.map((e) =>
                e.id === exerciseId
                  ? { ...e, sets: e.sets.map((ws) => (ws.id === updatedSet.id ? updatedSet : ws)) }
                  : e,
              ),
            },
          };
        }),

      removeSet: (exerciseId, setId) =>
        set((s) => {
          if (!s.activeSession) return {};
          return {
            activeSession: {
              ...s.activeSession,
              exercises: s.activeSession.exercises.map((e) =>
                e.id === exerciseId
                  ? { ...e, sets: e.sets.filter((ws) => ws.id !== setId) }
                  : e,
              ),
            },
          };
        }),

      setElapsed: (s) => set({ elapsedSeconds: s }),

      startRestTimer: (seconds, exerciseId) =>
        set({ restTimer: { active: true, remaining: seconds, exerciseId } }),

      tickRestTimer: () =>
        set((s) => {
          const remaining = Math.max(0, s.restTimer.remaining - 1);
          return {
            restTimer: {
              ...s.restTimer,
              remaining,
              active: remaining > 0,
            },
          };
        }),

      clearRestTimer: () =>
        set({ restTimer: { active: false, remaining: 0, exerciseId: null } }),

      clearSession: () =>
        set({
          activeSession: null,
          elapsedSeconds: 0,
          restTimer: { active: false, remaining: 0, exerciseId: null },
        }),
    }),
    {
      name: 'fittracker-workout',
      partialize: (s) => ({ activeSession: s.activeSession, elapsedSeconds: s.elapsedSeconds }),
    },
  ),
);

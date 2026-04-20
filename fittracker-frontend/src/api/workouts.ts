import { apiClient } from './client';

export interface WorkoutSet {
  id: number;
  set_number: number;
  set_type: string;
  reps: number | null;
  weight_kg: number | null;
  duration_seconds: number | null;
  distance_km: number | null;
  rpe: number | null;
  completed: boolean;
  completed_at: string | null;
  is_pr: boolean;
}

export interface WorkoutExercise {
  id: number;
  exercise_library_id: number;
  exercise_order: number;
  notes: string | null;
  rest_seconds: number;
  superset_group: number | null;
  sets: WorkoutSet[];
}

export interface WorkoutSession {
  id: number;
  name: string;
  notes: string | null;
  started_at: string;
  finished_at: string | null;
  duration_seconds: number | null;
  total_volume_kg: number;
  total_sets: number;
  total_reps: number;
  calories_burned: number | null;
  status: string;
  session_type: string;
  distance_km: number | null;
  avg_pace_min_km: number | null;
  avg_heart_rate: number | null;
  max_heart_rate: number | null;
  exercises: WorkoutExercise[];
}

export interface WorkoutListItem {
  id: number;
  name: string;
  started_at: string;
  finished_at: string | null;
  duration_seconds: number | null;
  total_volume_kg: number;
  total_sets: number;
  total_reps: number;
  status: string;
}

export interface WorkoutHistoryResponse {
  total: number;
  page: number;
  per_page: number;
  items: WorkoutListItem[];
}

export const workoutsApi = {
  start: (name: string, template_id?: number, session_type = 'strength'): Promise<WorkoutSession> =>
    apiClient.post<WorkoutSession>('/api/workouts', { name, template_id, session_type }).then(r => r.data),

  list: (page = 1, per_page = 10, status?: string): Promise<WorkoutHistoryResponse> => {
    const params = new URLSearchParams({ page: String(page), per_page: String(per_page) });
    if (status) params.set('status', status);
    return apiClient.get<WorkoutHistoryResponse>(`/api/workouts?${params}`).then(r => r.data);
  },

  get: (id: number): Promise<WorkoutSession> =>
    apiClient.get<WorkoutSession>(`/api/workouts/${id}`).then(r => r.data),

  finish: (id: number, notes?: string): Promise<WorkoutSession> =>
    apiClient.post<WorkoutSession>(`/api/workouts/${id}/finish`, { notes }).then(r => r.data),

  cancel: (id: number): Promise<void> =>
    apiClient.delete(`/api/workouts/${id}`).then(() => undefined),

  addExercise: (
    sessionId: number,
    exercise_library_id: number,
    exercise_order: number,
    rest_seconds = 60,
  ): Promise<WorkoutExercise> =>
    apiClient
      .post<WorkoutExercise>(`/api/workouts/${sessionId}/exercises`, {
        exercise_library_id,
        exercise_order,
        rest_seconds,
      })
      .then(r => r.data),

  removeExercise: (sessionId: number, exerciseId: number): Promise<void> =>
    apiClient.delete(`/api/workouts/${sessionId}/exercises/${exerciseId}`).then(() => undefined),

  addSet: (
    sessionId: number,
    exerciseId: number,
    data: {
      set_number: number;
      set_type?: string;
      reps?: number;
      weight_kg?: number;
    },
  ): Promise<WorkoutSet> =>
    apiClient
      .post<WorkoutSet>(`/api/workouts/${sessionId}/exercises/${exerciseId}/sets`, data)
      .then(r => r.data),

  updateSet: (
    sessionId: number,
    exerciseId: number,
    setId: number,
    data: Partial<WorkoutSet>,
  ): Promise<WorkoutSet> =>
    apiClient
      .patch<WorkoutSet>(`/api/workouts/${sessionId}/exercises/${exerciseId}/sets/${setId}`, data)
      .then(r => r.data),

  deleteSet: (sessionId: number, exerciseId: number, setId: number): Promise<void> =>
    apiClient
      .delete(`/api/workouts/${sessionId}/exercises/${exerciseId}/sets/${setId}`)
      .then(() => undefined),

  update: (id: number, data: { name?: string; notes?: string }): Promise<WorkoutSession> =>
    apiClient.patch<WorkoutSession>(`/api/workouts/${id}`, data).then(r => r.data),

  updateCardio: (id: number, data: { session_type?: string; distance_km?: number; avg_pace_min_km?: number; avg_heart_rate?: number; max_heart_rate?: number }): Promise<WorkoutSession> =>
    apiClient.patch<WorkoutSession>(`/api/workouts/${id}/cardio`, data).then(r => r.data),

  setSupersetGroup: (exerciseId: number, supersetGroup: number | null): Promise<void> =>
    apiClient.patch(`/api/workouts/exercises/${exerciseId}/superset`, { superset_group: supersetGroup }).then(() => undefined),

  delete: (id: number): Promise<void> =>
    apiClient.delete(`/api/workouts/${id}`).then(() => undefined),
};

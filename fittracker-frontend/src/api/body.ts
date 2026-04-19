import { apiClient } from './client';

export interface BodyMetric {
  id: number;
  weight_kg: number | null;
  body_fat_pct: number | null;
  muscle_mass_kg: number | null;
  bmi: number | null;
  waist_cm: number | null;
  chest_cm: number | null;
  hip_cm: number | null;
  notes: string | null;
  recorded_at: string;
}

export interface BodyMetricCreate {
  weight_kg?: number;
  body_fat_pct?: number;
  muscle_mass_kg?: number;
  waist_cm?: number;
  chest_cm?: number;
  hip_cm?: number;
  notes?: string;
}

export interface BodyGoal {
  id: number;
  goal_type: string;
  target_value: number;
  start_value: number | null;
  current_value: number | null;
  unit: string;
  deadline: string | null;
  status: string;
  completed_at: string | null;
  created_at: string;
  progress_pct: number | null;
}

export interface BodyGoalCreate {
  goal_type: string;
  target_value: number;
  start_value?: number;
  unit?: string;
  deadline?: string;
}

export const bodyApi = {
  logMetric: (data: BodyMetricCreate): Promise<BodyMetric> =>
    apiClient.post<BodyMetric>('/api/body/metrics', data).then(r => r.data),

  listMetrics: (page = 1, per_page = 30) =>
    apiClient.get<{ total: number; page: number; per_page: number; items: BodyMetric[] }>(
      `/api/body/metrics?page=${page}&per_page=${per_page}`
    ).then(r => r.data),

  latestMetric: (): Promise<BodyMetric> =>
    apiClient.get<BodyMetric>('/api/body/metrics/latest').then(r => r.data),

  deleteMetric: (id: number): Promise<void> =>
    apiClient.delete(`/api/body/metrics/${id}`).then(() => undefined),

  listGoals: (status?: string): Promise<BodyGoal[]> => {
    const params = status ? `?status=${status}` : '';
    return apiClient.get<BodyGoal[]>(`/api/body/goals${params}`).then(r => r.data);
  },

  createGoal: (data: BodyGoalCreate): Promise<BodyGoal> =>
    apiClient.post<BodyGoal>('/api/body/goals', data).then(r => r.data),

  updateGoal: (id: number, data: Partial<BodyGoal>): Promise<BodyGoal> =>
    apiClient.patch<BodyGoal>(`/api/body/goals/${id}`, data).then(r => r.data),

  deleteGoal: (id: number): Promise<void> =>
    apiClient.delete(`/api/body/goals/${id}`).then(() => undefined),
};

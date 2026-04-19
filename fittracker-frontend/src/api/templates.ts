import { apiClient } from './client';

export interface TemplateExercise {
  id: number;
  exercise_library_id: number;
  exercise_name: string | null;
  exercise_order: number;
  target_sets: number | null;
  target_reps: number | null;
  target_weight_kg: number | null;
  rest_seconds: number;
  notes: string | null;
}

export interface Template {
  id: number;
  user_id: number;
  name: string;
  description: string | null;
  is_public: boolean;
  estimated_duration_min: number | null;
  times_used: number;
  created_at: string;
  exercise_count: number;
}

export interface TemplateDetail extends Template {
  exercises: TemplateExercise[];
  creator_username: string | null;
}

export interface TemplateCreate {
  name: string;
  description?: string;
  is_public?: boolean;
  estimated_duration_min?: number;
  exercises?: Array<{
    exercise_library_id: number;
    exercise_order?: number;
    target_sets?: number;
    target_reps?: number;
    target_weight_kg?: number;
    rest_seconds?: number;
    notes?: string;
  }>;
}

export const templatesApi = {
  list: (params: { mine?: boolean; public?: boolean } = {}): Promise<Template[]> => {
    const q = new URLSearchParams();
    if (params.mine !== undefined) q.set('mine', String(params.mine));
    if (params.public !== undefined) q.set('public', String(params.public));
    return apiClient.get<Template[]>(`/api/templates?${q}`).then(r => r.data);
  },
  get: (id: number): Promise<TemplateDetail> =>
    apiClient.get<TemplateDetail>(`/api/templates/${id}`).then(r => r.data),
  create: (data: TemplateCreate): Promise<TemplateDetail> =>
    apiClient.post<TemplateDetail>('/api/templates', data).then(r => r.data),
  update: (id: number, data: Partial<TemplateCreate>): Promise<TemplateDetail> =>
    apiClient.put<TemplateDetail>(`/api/templates/${id}`, data).then(r => r.data),
  delete: (id: number): Promise<void> =>
    apiClient.delete(`/api/templates/${id}`).then(() => undefined),
  start: (id: number): Promise<{ id: number; name: string }> =>
    apiClient.post(`/api/templates/${id}/start`).then(r => r.data),
  saveAsTemplate: (workoutId: number, data: { name: string; description?: string; is_public?: boolean }): Promise<Template> =>
    apiClient.post<Template>(`/api/workouts/${workoutId}/save-as-template`, data).then(r => r.data),
};

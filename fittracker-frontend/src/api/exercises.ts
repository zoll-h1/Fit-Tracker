import { apiClient } from './client';

export interface Exercise {
  id: number;
  name: string;
  slug: string;
  muscle_primary: string | null;
  muscle_secondary: string | null;
  equipment: string | null;
  force_type: string | null;
  difficulty: string;
  category: string;
  description: string | null;
  instructions: string | null;
  video_url: string | null;
  image_url: string | null;
  is_custom: boolean;
  met_value: number;
  created_at: string;
}

export interface ExerciseListResponse {
  total: number;
  page: number;
  per_page: number;
  items: Exercise[];
}

export interface ExerciseFilters {
  page?: number;
  per_page?: number;
  search?: string;
  category?: string;
  muscle?: string;
  equipment?: string;
  difficulty?: string;
}

export const exercisesApi = {
  list: (filters: ExerciseFilters = {}): Promise<ExerciseListResponse> => {
    const params = new URLSearchParams();
    Object.entries(filters).forEach(([k, v]) => {
      if (v !== undefined && v !== '') params.set(k, String(v));
    });
    return apiClient.get<ExerciseListResponse>(`/api/exercises?${params}`).then(r => r.data);
  },

  get: (id: number): Promise<Exercise> =>
    apiClient.get<Exercise>(`/api/exercises/${id}`).then(r => r.data),
};

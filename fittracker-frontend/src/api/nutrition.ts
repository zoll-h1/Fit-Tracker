import { apiClient } from './client';

export interface Food {
  id: number;
  name: string;
  brand: string | null;
  calories_per_100g: number;
  protein_g: number;
  carbs_g: number;
  fat_g: number;
  fiber_g: number;
  sugar_g: number;
  sodium_mg: number;
  is_custom: boolean;
}

export interface MealLog {
  id: number;
  food_id: number;
  food_name?: string;
  meal_type: string;
  quantity_g: number;
  logged_at: string;
  calories: number;
  protein_g: number;
  carbs_g: number;
  fat_g: number;
  fiber_g: number;
}

export interface MealTypeGroup {
  meal_type: string;
  items: MealLog[];
  subtotal_calories: number;
  subtotal_protein_g: number;
  subtotal_carbs_g: number;
  subtotal_fat_g: number;
}

export interface DailySummary {
  date: string;
  total_calories: number;
  total_protein_g: number;
  total_carbs_g: number;
  total_fat_g: number;
  total_fiber_g: number;
  meals: MealTypeGroup[];
}

export interface NutritionGoal {
  calories_target: number;
  protein_g: number;
  carbs_g: number;
  fat_g: number;
  fiber_g: number;
  updated_at: string;
}

export interface WeeklyAdherence {
  days: { date: string; calories: number; target: number; adherence_pct: number }[];
  avg_adherence_pct: number;
}

export const nutritionApi = {
  logMeal: (food_id: number, meal_type: string, quantity_g: number, logged_at?: string): Promise<MealLog> =>
    apiClient.post<MealLog>('/api/nutrition/log', { food_id, meal_type, quantity_g, logged_at }).then(r => r.data),

  deleteLog: (id: number): Promise<void> =>
    apiClient.delete(`/api/nutrition/log/${id}`).then(() => undefined),

  daily: (date?: string): Promise<DailySummary> => {
    const params = date ? `?date=${date}` : '';
    return apiClient.get<DailySummary>(`/api/nutrition/daily${params}`).then(r => r.data);
  },

  weekly: (): Promise<WeeklyAdherence> =>
    apiClient.get<WeeklyAdherence>('/api/nutrition/weekly').then(r => r.data),

  getGoals: (): Promise<NutritionGoal> =>
    apiClient.get<NutritionGoal>('/api/nutrition/goals').then(r => r.data),

  updateGoals: (goals: Omit<NutritionGoal, 'updated_at'>): Promise<NutritionGoal> =>
    apiClient.put<NutritionGoal>('/api/nutrition/goals', goals).then(r => r.data),
};

export const foodsApi = {
  search: (search?: string, page = 1, per_page = 20) => {
    const params = new URLSearchParams({ page: String(page), per_page: String(per_page) });
    if (search) params.set('search', search);
    return apiClient.get<{ total: number; items: Food[] }>(`/api/foods?${params}`).then(r => r.data);
  },
};

import apiClient from './client';

export interface WorkoutProgram {
  id: number;
  trainer_id: number;
  title: string;
  description?: string;
  duration_weeks: number;
  difficulty: string;
  is_public: boolean;
  created_at: string;
  days_count: number;
  assignment_count: number;
}

export interface ProgramDetail extends Omit<WorkoutProgram, 'days_count' | 'assignment_count'> {
  days: ProgramDay[];
}

export interface ProgramDay {
  id: number;
  week_number: number;
  day_number: number;
  name?: string;
  exercises: ProgramExercise[];
}

export interface ProgramExercise {
  id: number;
  exercise_id: number;
  exercise_name: string;
  exercise_order: number;
  sets: number;
  reps?: string;
  weight_note?: string;
  rest_seconds: number;
}

export interface ClientStats {
  user_id: number;
  username: string;
  total_workouts: number;
  this_week_workouts: number;
  current_streak: number;
  level: number;
  assigned_programs: string[];
}

export interface TrainerApplication {
  id: number;
  user_id: number;
  motivation: string;
  credentials: string;
  status: 'pending' | 'approved' | 'rejected';
  admin_note?: string;
  created_at: string;
  reviewed_at?: string;
}

export const trainerApi = {
  // Applications
  applyToBeTrainer: (data: { motivation: string; credentials: string }): Promise<TrainerApplication> =>
    apiClient.post('/api/trainer/apply', data).then(r => r.data),
  getMyApplication: (): Promise<TrainerApplication | null> =>
    apiClient.get('/api/trainer/my-application').then(r => r.data),

  // Programs
  listPrograms: (): Promise<WorkoutProgram[]> => apiClient.get('/api/trainer/programs').then(r => r.data),
  listPublicPrograms: (): Promise<WorkoutProgram[]> => apiClient.get('/api/trainer/programs/public').then(r => r.data),
  getProgram: (id: number): Promise<ProgramDetail> => apiClient.get(`/api/trainer/programs/${id}`).then(r => r.data),
  createProgram: (data: { title: string; description?: string; duration_weeks: number; difficulty: string; is_public: boolean }): Promise<ProgramDetail> =>
    apiClient.post('/api/trainer/programs', data).then(r => r.data),
  deleteProgram: (id: number) => apiClient.delete(`/api/trainer/programs/${id}`),
  assignProgram: (programId: number, clientUsername: string) =>
    apiClient.post(`/api/trainer/programs/${programId}/assign`, { client_username: clientUsername }).then(r => r.data),

  // Days
  addDay: (programId: number, data: { week_number: number; day_number: number; name?: string }): Promise<ProgramDay> =>
    apiClient.post(`/api/trainer/programs/${programId}/days`, data).then(r => r.data),
  deleteDay: (dayId: number) => apiClient.delete(`/api/trainer/days/${dayId}`),

  // Exercises in days
  addExercise: (dayId: number, data: { exercise_id: number; sets: number; reps?: string; weight_note?: string; rest_seconds: number }): Promise<ProgramExercise> =>
    apiClient.post(`/api/trainer/days/${dayId}/exercises`, data).then(r => r.data),
  deleteExercise: (exerciseId: number) => apiClient.delete(`/api/trainer/exercises/${exerciseId}`),

  // Clients
  getClients: (): Promise<ClientStats[]> => apiClient.get('/api/trainer/clients').then(r => r.data),
  getMyAssignments: () => apiClient.get('/api/trainer/my-assignments').then(r => r.data),
};


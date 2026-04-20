import { apiClient } from './client';

export interface Challenge {
  id: number;
  creator_id: number;
  title: string;
  description: string | null;
  challenge_type: 'total_workouts' | 'total_volume' | 'streak';
  target_value: number;
  start_date: string;
  end_date: string;
  is_public: boolean;
  status: 'active' | 'completed' | 'cancelled';
  winner_user_id: number | null;
  created_at: string;
  participant_count: number;
  is_joined: boolean;
  my_progress: number | null;
  my_rank: number | null;
}

export interface LeaderboardEntry {
  user_id: number;
  username: string;
  avatar_url: string | null;
  current_progress: number;
  rank: number | null;
  joined_at: string;
}

export interface ChallengeCreate {
  title: string;
  description?: string;
  challenge_type: 'total_workouts' | 'total_volume' | 'streak';
  target_value: number;
  start_date: string;
  end_date: string;
  is_public?: boolean;
}

export const challengesApi = {
  list: (params: { status?: string; mine?: boolean } = {}): Promise<Challenge[]> => {
    const q = new URLSearchParams();
    if (params.status) q.set('status', params.status);
    if (params.mine !== undefined) q.set('mine', String(params.mine));
    return apiClient.get<Challenge[]>(`/api/challenges?${q}`).then(r => r.data);
  },
  get: (id: number): Promise<Challenge & { participants: LeaderboardEntry[] }> =>
    apiClient.get(`/api/challenges/${id}`).then(r => r.data),
  create: (data: ChallengeCreate): Promise<Challenge> =>
    apiClient.post<Challenge>('/api/challenges', data).then(r => r.data),
  update: (id: number, data: Partial<ChallengeCreate>): Promise<Challenge> =>
    apiClient.put<Challenge>(`/api/challenges/${id}`, data).then(r => r.data),
  delete: (id: number): Promise<void> =>
    apiClient.delete(`/api/challenges/${id}`).then(() => undefined),
  join: (id: number): Promise<void> =>
    apiClient.post(`/api/challenges/${id}/join`).then(() => undefined),
  leave: (id: number): Promise<void> =>
    apiClient.delete(`/api/challenges/${id}/leave`).then(() => undefined),
  leaderboard: (id: number): Promise<LeaderboardEntry[]> =>
    apiClient.get<LeaderboardEntry[]>(`/api/challenges/${id}/leaderboard`).then(r => r.data),
};

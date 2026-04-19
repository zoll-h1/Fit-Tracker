import { apiClient } from './client';

export interface GamificationProfile {
  total_xp: number;
  current_level: number;
  level_name: string;
  xp_in_level: number;
  xp_for_next: number | null;
  xp_pct: number;
  current_streak_days: number;
  longest_streak_days: number;
  weekly_xp: number;
  monthly_xp: number;
}

export interface Achievement {
  id: number;
  key: string;
  name: string;
  description: string;
  icon_name: string | null;
  category: string;
  xp_reward: number;
  requirement_type: string;
  requirement_value: number;
  rarity: string;
  earned: boolean;
  earned_at: string | null;
}

export interface LeaderboardEntry {
  rank: number;
  user_id: number;
  username: string;
  total_xp: number;
  current_level: number;
  level_name: string;
}

export interface StreakInfo {
  current_streak: number;
  longest_streak: number;
  last_workout_date: string | null;
}

export const gamificationApi = {
  profile: (): Promise<GamificationProfile> =>
    apiClient.get<GamificationProfile>('/api/gamification/profile').then(r => r.data),

  allAchievements: (): Promise<Achievement[]> =>
    apiClient.get<Achievement[]>('/api/gamification/achievements').then(r => r.data),

  myAchievements: (): Promise<Achievement[]> =>
    apiClient.get<Achievement[]>('/api/gamification/achievements/my').then(r => r.data),

  leaderboard: (limit = 20): Promise<LeaderboardEntry[]> =>
    apiClient.get<LeaderboardEntry[]>(`/api/gamification/leaderboard?limit=${limit}`).then(r => r.data),

  streaks: (): Promise<StreakInfo> =>
    apiClient.get<StreakInfo>('/api/gamification/streaks').then(r => r.data),
};

export interface DashboardStats {
  this_week_workouts: number;
  this_month_workouts: number;
  total_workouts: number;
  total_volume_kg: number;
  avg_workout_duration_min: number;
  current_streak: number;
  this_week_calories: number;
  recent_prs: { exercise: string; weight_kg: number; date: string }[];
}

export interface StrengthPoint { date: string; max_weight_kg: number; total_volume: number; }
export interface VolumePoint { date: string; volume_kg: number; workout_count: number; }
export interface MuscleGroup { muscle_group: string; sets_count: number; percentage: number; }
export interface PRRecord { exercise_id: number; exercise_name: string; weight_kg: number; reps: number | null; achieved_at: string; }
export interface CalendarDay { date: string; has_workout: boolean; }
export interface StreakCalendar { current_streak: number; longest_streak: number; calendar: CalendarDay[]; }

export const analyticsApi = {
  dashboard: (): Promise<DashboardStats> =>
    apiClient.get<DashboardStats>('/api/analytics/dashboard').then(r => r.data),

  strength: (exercise_id: number, period = '90d') =>
    apiClient.get<{ chart: StrengthPoint[]; pr_weight: number | null; pr_date: string | null }>(
      `/api/analytics/strength?exercise_id=${exercise_id}&period=${period}`
    ).then(r => r.data),

  volume: (period = '30d'): Promise<VolumePoint[]> =>
    apiClient.get<VolumePoint[]>(`/api/analytics/volume?period=${period}`).then(r => r.data),

  muscles: (period = '30d'): Promise<MuscleGroup[]> =>
    apiClient.get<MuscleGroup[]>(`/api/analytics/muscles?period=${period}`).then(r => r.data),

  personalRecords: (): Promise<PRRecord[]> =>
    apiClient.get<PRRecord[]>('/api/analytics/personal-records').then(r => r.data),

  streak: (): Promise<StreakCalendar> =>
    apiClient.get<StreakCalendar>('/api/analytics/streak').then(r => r.data),

  workouts: (period = '30d') =>
    apiClient.get<{ date: string; count: number }[]>(`/api/analytics/workouts?period=${period}`).then(r => r.data),
};

export interface Notification {
  id: number;
  notification_type: string;
  title: string;
  body: string;
  is_read: boolean;
  action_url: string | null;
  created_at: string;
}

export const notificationsApi = {
  list: (unread_only = false): Promise<Notification[]> =>
    apiClient.get<Notification[]>(`/api/notifications?unread_only=${unread_only}`).then(r => r.data),

  unreadCount: (): Promise<number> =>
    apiClient.get<{ count: number }>('/api/notifications/unread-count').then(r => r.data.count),

  markRead: (id: number): Promise<Notification> =>
    apiClient.put<Notification>(`/api/notifications/${id}/read`).then(r => r.data),

  markAllRead: (): Promise<void> =>
    apiClient.put('/api/notifications/read-all').then(() => undefined),

  delete: (id: number): Promise<void> =>
    apiClient.delete(`/api/notifications/${id}`).then(() => undefined),
};

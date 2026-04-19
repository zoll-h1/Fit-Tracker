import { apiClient } from './client';

export interface FeedItem {
  id: number;
  user_id: number;
  username: string;
  avatar_url: string | null;
  activity_type: 'workout' | 'pr' | 'achievement';
  title: string;
  body: string | null;
  likes_count: number;
  comments_count: number;
  is_liked_by_me: boolean;
  created_at: string;
}

export interface PublicProfile {
  id: number;
  username: string;
  full_name: string | null;
  avatar_url: string | null;
  created_at: string;
  followers_count: number;
  following_count: number;
  is_following: boolean;
}

export interface FollowUser {
  id: number;
  username: string;
  full_name: string | null;
  avatar_url: string | null;
}

export interface Comment {
  id: number;
  feed_id: number;
  user_id: number;
  username: string;
  content: string;
  created_at: string;
}

export const socialApi = {
  feed: (skip = 0, limit = 20): Promise<FeedItem[]> =>
    apiClient.get<FeedItem[]>(`/api/social/feed?skip=${skip}&limit=${limit}`).then(r => r.data),
  follow: (userId: number) => apiClient.post(`/api/social/follow/${userId}`),
  unfollow: (userId: number) => apiClient.delete(`/api/social/follow/${userId}`),
  followers: (): Promise<FollowUser[]> => apiClient.get<FollowUser[]>('/api/social/followers').then(r => r.data),
  following: (): Promise<FollowUser[]> => apiClient.get<FollowUser[]>('/api/social/following').then(r => r.data),
  toggleLike: (feedId: number): Promise<{ liked: boolean; likes_count: number }> =>
    apiClient.post<{ liked: boolean; likes_count: number }>(`/api/social/feed/${feedId}/like`).then(r => r.data),
  addComment: (feedId: number, content: string): Promise<Comment> =>
    apiClient.post<Comment>(`/api/social/feed/${feedId}/comments`, { content }).then(r => r.data),
  getComments: (feedId: number): Promise<Comment[]> =>
    apiClient.get<Comment[]>(`/api/social/feed/${feedId}/comments`).then(r => r.data),
  deleteComment: (feedId: number, commentId: number) =>
    apiClient.delete(`/api/social/feed/${feedId}/comments/${commentId}`),
  publicProfile: (userId: number): Promise<PublicProfile> =>
    apiClient.get<PublicProfile>(`/api/users/${userId}/profile`).then(r => r.data),
  searchUsers: (q: string): Promise<FollowUser[]> =>
    apiClient.get<FollowUser[]>(`/api/users/search?q=${encodeURIComponent(q)}`).then(r => r.data),
};

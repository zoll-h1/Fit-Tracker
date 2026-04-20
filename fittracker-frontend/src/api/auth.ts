import apiClient from './client'
import type { LoginRequest, RegisterRequest, TokenResponse, User } from '@/types/auth'

export const authApi = {
  register: async (data: RegisterRequest): Promise<TokenResponse> => {
    const res = await apiClient.post('/api/auth/register', data)
    return res.data
  },

  login: async (data: LoginRequest): Promise<TokenResponse> => {
    const res = await apiClient.post('/api/auth/login', data)
    return res.data
  },

  refresh: async (refreshToken: string): Promise<TokenResponse> => {
    const res = await apiClient.post('/api/auth/refresh', { refresh_token: refreshToken })
    return res.data
  },

  logout: async (refreshToken: string): Promise<void> => {
    await apiClient.post('/api/auth/logout', { refresh_token: refreshToken })
  },

  me: async (): Promise<User> => {
    const res = await apiClient.get('/api/auth/me')
    return res.data
  },

  updateMe: async (data: Partial<User>): Promise<User> => {
    const res = await apiClient.patch('/api/auth/me', data)
    return res.data
  },
}

export const usersApi = {
  updateProfile: async (data: Partial<User>): Promise<User> => {
    const res = await apiClient.put('/api/users/profile', data)
    return res.data
  },

  uploadAvatar: async (file: File): Promise<User> => {
    const formData = new FormData()
    formData.append('file', file)
    const res = await apiClient.post('/api/users/avatar', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
    return res.data
  },
}

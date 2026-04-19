export interface User {
  id: number
  username: string
  email: string
  full_name: string | null
  date_of_birth: string | null
  gender: string | null
  bio: string | null
  avatar_url: string | null
  height_cm: number | null
  weight_kg: number | null
  unit_system: string
  timezone: string
  language: string
  role: string
  is_active: boolean
  is_email_verified: boolean
  created_at: string
}

export interface TokenResponse {
  access_token: string
  refresh_token: string
  token_type: string
  user: User
}

export interface LoginRequest {
  email: string
  password: string
}

export interface RegisterRequest {
  username: string
  email: string
  password: string
  full_name?: string
  date_of_birth?: string
  gender?: string
  unit_system?: string
}

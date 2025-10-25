/**
 * Authentication types based on actual backend API
 * Backend: POST /api/auth/login, GET /api/auth/me
 */

export interface User {
  id: number
  username: string
  full_name: string
  is_active: boolean
  created_at: string
  last_login: string | null
}

export interface LoginRequest {
  username: string
  password: string
  remember_me?: boolean
}

export interface LoginResponse {
  success: boolean
  timestamp: string
  message: string
  access_token: string
  token_type: string
  expires_in: number
  user_info: User
}

export interface LogoutResponse {
  success: boolean
  timestamp: string
  message: string
}

export interface TokenValidationResponse {
  success: boolean
  timestamp: string
  message: string
}

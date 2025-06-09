/**
 * API相关的类型定义
 */

// 通用响应类型
export interface ApiResponse<T = unknown> {
  data?: T
  message?: string
  status?: number
  [key: string]: unknown
}

// 用户相关类型
export interface UserInfo {
  username: string
  authority: string
  [key: string]: unknown
}

export interface LoginResponse {
  token?: string
  user?: UserInfo
  message?: string
}

export interface UserListResponse {
  users: UserInfo[]
}

// 权限相关类型
export interface AuthorityInfo {
  name: string
  menus: string
  [key: string]: unknown
}

export interface AuthorityListResponse {
  authorities: AuthorityInfo[]
}

// 搜索相关类型
export interface SearchSuggestion {
  word: string
  [key: string]: unknown
}

export interface SugListResponse {
  suggestions: SearchSuggestion[]
}

// 秘密相关类型
export interface SecretInfo {
  state?: string
  message?: string
  [key: string]: unknown
}

export interface SecretResponse {
  secret: SecretInfo
}

// HTTP方法类型
export type HttpMethod = 'GET' | 'POST' | 'PUT' | 'DELETE'

/**
 * 包含应用中所有基础api
 */
import ajax from './ajax'
import md5 from 'md5'
import type { LoginResponse, UserListResponse, AuthorityListResponse } from './types'

// 登入
export const reqLogin = (username: string, password: string) => {
  const hashedPassword = md5(password)
  return ajax<LoginResponse>('/api/login', { username, password: hashedPassword }, 'POST')
}

// 获取用户列表
export const reqUserList = () => 
  ajax<UserListResponse>('/api/user', { type: 'get' }, 'POST')

// 更新用户
export const reqUpdateUser = (username: string, password: string, authority: string) => {
  const hashedPassword = md5(password)
  return ajax('/api/user', { type: 'update', username, password: hashedPassword, authority }, 'POST')
}

// 删除用户
export const reqDelUser = (username: string) => {
  return ajax('/api/user', { type: 'del', username }, 'POST')
}

// 获取角色列表
export const reqAuthorityList = () => 
  ajax<AuthorityListResponse>('/api/authority', { type: 'get' }, 'POST')

// 更新角色
export const reqUpdateAuthority = (name: string, menus = '') => {
  return ajax('/api/authority', { type: 'update', name, menus }, 'POST')
}

// 删除角色
export const reqDelAuthority = (name: string) => {
  return ajax('/api/authority', { type: 'del', name }, 'POST')
}

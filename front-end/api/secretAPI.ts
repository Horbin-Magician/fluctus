/**
 * 包含应用中所有与秘密树洞有关的api
 */
import ajax from './ajax'
import type { SecretResponse } from './types'

// 获取秘密信息
export const getSecret = () => {
  return ajax<SecretResponse>('/api/secret', { type: 'get' }, 'POST')
}

// 更新秘密信息
export const updateSecret = (state?: string, message?: string) => {
  return ajax('/api/secret', { type: 'update', state, message }, 'POST')
}

// 更新状态
export const updateState = (state: string) => {
  return updateSecret(state)
}

// 更新消息
export const updateMessage = (message: string) => {
  return updateSecret(undefined, message)
}

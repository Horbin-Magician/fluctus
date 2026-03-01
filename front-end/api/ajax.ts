/**
 * 能发送异步ajax请求的函数模块
 * 函数返回promise对象
 */
import type { HttpMethod, ApiResponse } from './types'
import storageUtils from '@/utils/storageUtils'

function getResponseStatus(error: unknown): number | null {
  if (!error || typeof error !== 'object') return null
  const candidate = error as { status?: number; statusCode?: number; response?: { status?: number } }
  if (typeof candidate.status === 'number') return candidate.status
  if (typeof candidate.statusCode === 'number') return candidate.statusCode
  if (candidate.response && typeof candidate.response.status === 'number') return candidate.response.status
  return null
}

function handleUnauthorizedResponse() {
  if (!import.meta.client) return
  storageUtils.removeUser()
  if (window.location.pathname !== '/') {
    window.location.href = '/'
  }
}

/**
 * 通用Ajax请求函数
 * @param url - 请求URL
 * @param data - 请求数据
 * @param method - 请求方法
 * @returns Promise<ApiResponse>
 */
export default async function ajax<T = unknown>(
  url: string, 
  data: Record<string, unknown> = {}, 
  method: HttpMethod = 'GET'
): Promise<ApiResponse<T>> {
  try {
    // 在生产环境中添加API基础URL
    const baseURL = process.env.NODE_ENV === 'production' ? 'https://api.fluctus.cc' : ''
    const fullUrl = baseURL + url

    let response: ApiResponse<T>

    if (method === 'GET') {
      // GET请求将数据作为查询参数
      response = await $fetch(fullUrl, {
        method: 'GET',
        query: data,
        credentials: 'include'
      })
    } else {
      // POST/PUT/DELETE请求将数据作为请求体
      response = await $fetch(fullUrl, {
        method,
        body: data,
        credentials: 'include'
      })
    }

    return response
  } catch (error) {
    const status = getResponseStatus(error)
    if (status === 401) {
      handleUnauthorizedResponse()
    } else {
      console.error('Ajax request failed:', error)
    }
    throw error
  }
}

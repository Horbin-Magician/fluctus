/**
 * 能发送异步ajax请求的函数模块
 * 函数返回promise对象
 */
import type { HttpMethod, ApiResponse } from './types'

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
    // TODO: 统一处理错误
    console.error('Ajax request failed:', error)
    throw error
  }
}

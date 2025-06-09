/**
 * 包含应用中所有与搜索有关的api
 */
import ajax from './ajax'
import type { SugListResponse } from './types'

// 获取提示内容
export const reqSugList = (word: string) => {
  return ajax<SugListResponse>('/api/search/baidu', { word }, 'POST')
}

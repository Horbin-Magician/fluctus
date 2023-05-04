/*
包含应用中所有与收藏夹有关的api
 */
import ajax from './ajax'


//获取提示内容
export const reqSugList = (word) => {
  return ajax('/api/search/baidu', {'word':word}, 'POST')
}
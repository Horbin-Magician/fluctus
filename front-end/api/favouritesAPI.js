/*
包含应用中所有与收藏夹有关的api
 */
import ajax from './ajax'


//获取收藏类
export const reqFavTypeList = () => {
  return ajax('/api/favourites/favtype', {'type':'get'}, 'POST')
}
//获取收藏项
export const reqFavItemList = (favType=undefined) => ajax('/api/favourites/favitem', {'type':'get', favType}, 'POST')

//删除收藏类
export const reqDelType = (title) => {
  return ajax('/api/favourites/favtype', {'type':'del', title}, 'POST')
}
//更新收藏类
export const reqUpdateType = (title, rank, oldTitle=undefined) => {
  return ajax('/api/favourites/favtype', {'type':'update', title, rank, oldTitle}, 'POST')
}
//移动收藏类
export const reqMoveType = (fType, tType) => {
  return ajax('/api/favourites/favtype', {'type':'move', fType, tType}, 'POST')
}
//删除收藏项
export const reqDelItem = (url) => ajax('/api/favourites/favitem', {'type':'del', url}, 'POST')
//更新收藏项
export const reqUpdateItem = (url, favType, title, rank, iconUrl, description, oldUrl=undefined) => {
  return ajax('/api/favourites/favitem', {'type':'update', url, favType, title, rank, iconUrl, description, oldUrl}, 'POST')
}
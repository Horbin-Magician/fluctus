/*
包含应用中所有基础api
 */
import ajax from './ajax'
import md5 from 'md5'


//登入
export const reqLogin = (username, password) => {
    password = md5(password)
    return ajax('/api/login', {username, password}, 'POST')
}
//获取用户列表
export const reqUserList = () => ajax('/api/user', {'type':'get'}, 'POST')
//更新用户
export const reqUpdateUser = (username, password, authority) => {
    password = md5(password)
    return ajax('/api/user', {'type':'update', username, password, authority}, 'POST')
}
//删除用户
export const reqDelUser = (username) => {
    return ajax('/api/user', {'type':'del', username}, 'POST')
}
//获取角色列表
export const reqAuthorityList = () => ajax('/api/authority', {'type':'get'}, 'POST')
//更新角色
export const reqUpdateAuthority = (name, menus='') => {
    return ajax('/api/authority', {'type':'update', name, menus}, 'POST')
}
//删除角色
export const reqDelAuthority = (name) => {
    return ajax('/api/authority', {'type':'del', name}, 'POST')
}
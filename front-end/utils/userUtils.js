import { reqLogin } from '@/api/baseAPI'
import memoryUtils from './memoryUtils'
import storageUtils from './storageUtils'
/**
 * 用户登录
 */
let updateFuns = []    //用户状态更新回调函数
let isLogining = false //是否正在登录

//添加回调
export const addUpdateFun = (fun) =>{
  updateFuns.push(fun)
}

//更新时调用回调
const update = ()=>{
  updateFuns.forEach(e=>{
    e()
  })
}

/**
 * 
 * @param {*用户名} username 
 * @param {*密码} password 
 * @returns 结果promise
 */
export const userlogin = (username, password) => {
  isLogining = true
  return new Promise((resolve) => {
    reqLogin(username, password).then(data => {
      if (data && data.status === '0') {//登入成功
        const authority = data.authority
        memoryUtils.userdata = { username, password, authority}
        storageUtils.saveUser({ username, password, authority })
        data['message'] = "登录成功，欢迎回来~"
      } else {//账号或密码错误
        const user = storageUtils.getUser()
        if (user.username){
          storageUtils.removeUser()
          memoryUtils.userdata = null
          data['message'] = "登录已失效，请重新登陆！"
        }
        else data['message'] = "登录失败，账号或密码错误！";
      }
      update()//更新
      isLogining = false
      resolve(data)
    })
  })
}

/**
 * 注销登录
 */
export const userlogout = () => {
  storageUtils.removeUser()
  memoryUtils.userdata = null
  update()//更新
  return true
}

/**
 * 检查storage,并初始化用户信息
 */
export const initUser = () => {
  return new Promise((resolve) => {
    const user = storageUtils.getUser()
    if (user.username) return resolve(userlogin(user.username, user.password))
    return resolve(null)
  })
}

/**
 * 检查是否的登录
 * @returns true or false
 */
export const checkLogin = () => {
  return memoryUtils.userdata && memoryUtils.userdata.username;
}

/**
 * 检查是否的登录
 * @returns true or false
 */
export const checkLoginPromise = () => {
  return new Promise((resolve) => {
    const check = () => {
      if (!isLogining) {
        resolve(memoryUtils.userdata && memoryUtils.userdata.username); // 解决Promise，返回用户数据
      } else {
        setTimeout(check, 50); // 如果仍在登录中，50毫秒后再次检查
      }
    };
    check(); // 开始检查登录状态
  });
}
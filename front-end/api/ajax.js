/*
能发送异步ajax请求的函数模块
函数返回promise对象
 */
import axios from 'axios'

axios.defaults.withCredentials = true;

export default function ajax(url, data = {}, type = 'GET') {
  if(process.env.NODE_ENV == 'production') url = 'https://api.fluctus.cc' + url
  return new Promise((resolve) => {
    let promise
    if (type === 'GET') { //发送GET请求
      promise = axios.get(url, {
        params: data
      })
    } else { //发送POST请求
      promise = axios.post(url, data)
    }
    //获取promise，统一处理error
    promise.then(response => {
      resolve(response.data)
    }).catch(() => {
      // TODO 统一处理error
    })
  })
}
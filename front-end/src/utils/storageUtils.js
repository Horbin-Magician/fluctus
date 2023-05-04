/*
进行local数据存储管理的工具模块
*/
const USER_KEY = 'user_key'
const THEME_KEY = "theme_key"
const SEARCH_SOURCE_KEY = "search_source_key"

//保存用户信息
function saveUser(userdata) {
  localStorage.setItem(USER_KEY, JSON.stringify(userdata))
}
//获取用户信息
function getUser() {
  return JSON.parse(localStorage.getItem(USER_KEY) || '{}')
}
//去除用户信息
function removeUser() {
  localStorage.removeItem(USER_KEY)
}

function setTheme(theme) {
  localStorage.setItem(THEME_KEY, theme)
}

function getTheme() {
  return localStorage.getItem(THEME_KEY)
}

function setDefaultSearchSource(theme) {
  localStorage.setItem(SEARCH_SOURCE_KEY, theme)
}

function getDefaultSearchSource() {
  return localStorage.getItem(SEARCH_SOURCE_KEY)
}

const exportObject = { saveUser, getUser, removeUser, setTheme, getTheme, setDefaultSearchSource, getDefaultSearchSource }
export default exportObject
import { checkLoginPromise } from '@/utils/userUtils'
import { useMessage } from 'naive-ui'

export default defineNuxtRouteMiddleware(async (to, from) => {
  if (process.server) return

  const isLogged = await checkLoginPromise()
  if (!isLogged) {
    const message = useMessage()
    message.error("请先登录！")

    return navigateTo('/')
  }
})
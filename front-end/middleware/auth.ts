import { checkLoginPromise } from '@/utils/userUtils'
import { useMessage } from 'naive-ui'

export default defineNuxtRouteMiddleware(async () => {
  if (import.meta.server) return

  const isLogged = await checkLoginPromise()
  if (!isLogged) {
    const message = useMessage()
    message.error("请先登录！")

    return navigateTo('/')
  }
})
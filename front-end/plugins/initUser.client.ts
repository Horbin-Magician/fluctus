import { initUser } from '@/utils/userUtils'

export default defineNuxtPlugin((nuxtApp) => {
  // Initialize user session on client start
  initUser()
})

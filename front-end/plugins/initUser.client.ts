import { initUser } from '@/utils/userUtils'

export default defineNuxtPlugin(async () => {
  // Initialize user session on client start
  await initUser()
})

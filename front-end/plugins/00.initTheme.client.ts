import storageUtils from '@/utils/storageUtils'

export default defineNuxtPlugin(() => {
  const body = document.body
  if (!body) {
    return
  }

  const storedTheme = storageUtils.getTheme()
  const theme = storedTheme || body.getAttribute('theme') || 'light'
  body.setAttribute('theme', theme)
})

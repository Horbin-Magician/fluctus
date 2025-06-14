// https://nuxt.com/docs/api/configuration/nuxt-config
export default defineNuxtConfig({
  ssr: false,
  build: { transpile: ['naive-ui', "vueuc"] },
  compatibilityDate: '2025-05-15',
  devtools: { enabled: true },
  modules: ['@nuxt/eslint'],

  vite: {
    server: {
      proxy: {
        "/api": "http://127.0.0.1:5000",
      },
    },
  },

  app: {
    head: {
      title: '云边小铺',
    }
  }
})

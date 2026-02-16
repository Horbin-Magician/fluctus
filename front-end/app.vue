<script setup>
  import { ref, onMounted, onUnmounted } from 'vue';
  import { NMessageProvider, NConfigProvider, darkTheme } from 'naive-ui';
  import './assets/css/main.css'

  const isDark = ref(false)
  let observer = null

  function buildThemeOverrides() {
    const styles = getComputedStyle(document.body)
    const primary = styles.getPropertyValue('--color-primary').trim()
    const primaryHover = styles.getPropertyValue('--color-light').trim()
    const primarySuppl = styles.getPropertyValue('--color-light-light').trim()
    const background = styles.getPropertyValue('--color-background').trim()
    const backgroundSoft = styles.getPropertyValue('--color-background-soft').trim()
    const text = styles.getPropertyValue('--color-text').trim()
    const textSub = styles.getPropertyValue('--color-text-sub').trim()
    const textSubSub = styles.getPropertyValue('--color-text-sub-sub').trim()
    const border = styles.getPropertyValue('--color-border').trim()

    return {
      common: {
        primaryColor: primary || '#45a3fa',
        primaryColorHover: primaryHover || primary || '#45a3fa',
        primaryColorPressed: primary || '#45a3fa',
        primaryColorSuppl: primarySuppl || primary || '#45a3fa',
        bodyColor: background || '#f8f8f8',
        cardColor: backgroundSoft || '#ffffff',
        modalColor: backgroundSoft || '#ffffff',
        textColor1: text || '#1a1a1a',
        textColor2: textSub || '#5c5b5b',
        textColor3: textSubSub || '#bbbbbb',
        borderColor: border || '#e0e0e0'
      }
    }
  }

  function checkTheme() {
    isDark.value = document.body.getAttribute('theme') === 'dark'
    themeOverrides.value = buildThemeOverrides()
  }

  onMounted(() => {
    checkTheme()
    observer = new MutationObserver(checkTheme)
    observer.observe(document.body, { attributes: true, attributeFilter: ['theme'] })
  })

  onUnmounted(() => {
    observer?.disconnect()
  })

  const themeOverrides = ref(buildThemeOverrides())
</script>

<template>
  <n-config-provider
    abstract
    :theme="isDark ? darkTheme : null"
    :theme-overrides="themeOverrides"
  >
    <n-message-provider>
      <NuxtRouteAnnouncer />
      <AppHeader />
      <NuxtPage class="content"/>
      <AppFooter />
    </n-message-provider>
  </n-config-provider>
</template>

<style scoped>
.content {
  min-height: calc(100vh - 30px);
}
</style>

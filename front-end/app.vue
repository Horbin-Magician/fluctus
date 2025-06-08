<script setup>
  import { NMessageProvider } from 'naive-ui';
  import './assets/main.css'
</script>

<template>
  <n-message-provider>
    <NuxtRouteAnnouncer />
    <AppHeader />
    <NuxtPage class="content"/>
    <AppFooter />
  </n-message-provider>
</template>

<style scoped>
.content {
  min-height: calc(100vh - 80px);
}
</style>
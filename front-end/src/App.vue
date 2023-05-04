<script setup>
  import { NMessageProvider } from 'naive-ui';
  import { RouterView } from 'vue-router';

  import MyHeader from './components/Header.vue';
  import MyFooter from './components/Footer.vue';

</script>

<template>
  <n-message-provider>
    <MyHeader/>
    <div class="content">
      <router-view></router-view>
    </div>
    <MyFooter/>
  </n-message-provider>
</template>

<style scoped>
.content {
  min-height: calc(100vh - 80px);
}
</style>
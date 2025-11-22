<!-- 页头 Header -->
<template>
  <header>
    <div class="logo">
      <svg class="icon" aria-hidden="true" @click="onLogoClicked">
        <use xlink:href="#icon-logo" />
      </svg>
    </div>
    <div class="left-bar">
      <div class="nav">
        <div v-for="(value, key) in router_items" :key="key">
          <NuxtLink v-if="value.shown" :to="value.path" class="link"> {{ key }} </NuxtLink>
        </div>
        <div v-if="!nav_track_left.startsWith('-')" class="nav-track" />
      </div>
      <ThemeToggle />
    </div>
  </header>
  <n-modal v-model:show="showLoginModal" transform-origin="center">
    <div class="login">
      <form @keyup.enter="onLogin">
        <input id='name' v-model='user_name' type="text" name='name' placeholder="账号">
        <input id='pwd' v-model='user_key' type="password" name='pwd' placeholder="密码">
        <a @click="onLogin"> 登录 </a>
      </form>
    </div>
  </n-modal>
  <n-modal v-model:show="showLogoutModal" preset="dialog" :closable="false" type="warning" title="注销"
    content="是否注销当前登陆？" positive-text="确认" negative-text="取消" @positive-click="logout" />
</template>

<script setup>
import { ref, reactive } from 'vue'
import { NModal, useMessage } from 'naive-ui'
import '@/assets/icons/iconfont'
import { userlogin, initUser, checkLogin, userlogout, addUpdateFun } from '@/utils/userUtils';
import ThemeToggle from '@/components/ThemeToggle.vue'

const route = useRoute()
const message = useMessage()

const router_items = reactive({
  '首页': { path: '/', shown: true },
  '日历': { path: '/calendar', shown: false },
  '关于': { path: '/about', shown: true }
})

const navLinks = computed(() => Object.entries(router_items)
  .filter(([_, v]) => v.shown)
  .map(([_, value]) => [value.path.slice(1)]))
const now_page = computed(() => route.path.slice(1).split('/')[0])
const nav_track_left = computed(() => {
  const idx = navLinks.value.findIndex(([key]) => key === (now_page.value))
  return `${10 + idx * 70}px`
})

const showLoginModal = ref(false)
const showLogoutModal = ref(false)
const user_name = ref('')
const user_key = ref('')

addUpdateFun(() => {
  if (checkLogin()) {
    router_items['日历'].shown = true
  } else {
    router_items['日历'].shown = false
  }
})

// 初始化User信息
initUser().then(data => {
  if (data && data.status == 0) message.success(data.message)
})

function onLogin() {
  userlogin(user_name.value, user_key.value).then(data => {
    if (data.status == '0') {
      showLoginModal.value = false
      message.success(data.message)
    } else {
      message.error(data.message)
    }
  })
}

function onLogoClicked() {
  return checkLogin() ? showLogoutModal.value = true : showLoginModal.value = true
}

function logout() {
  userlogout()
  message.success("注销成功！")
}
</script>

<style scoped>
header {
  position: fixed;
  top: 10px;
  left: 50%;
  transform: translateX(-50%);
  width: 600px;
  height: 50px;
  border-radius: 20px;
  display: flex;
  justify-content: space-between;
  background-color: var(--color-background);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  z-index: 2;
}

@keyframes shake {
  0% {
    transform: rotate(0);
  }

  50% {
    transform: rotate(-20deg);
  }

  100% {
    transform: rotate(0);
  }
}

.logo {
  height: 50px;
  margin-left: 20px;
  margin-right: 20px;
  transform-origin: center center;
}

.logo svg {
  width: 50px;
  height: 50px;
  color: var(--color-light);
  fill: currentColor;
}

.logo:hover {
  animation: shake 0.2s linear;
  cursor: pointer;
  filter: drop-shadow(0px 0px 1px var(--color-light));
}

.left-bar {
  display: flex;
  align-items: center;
  margin-right: 20px;
}

.nav {
  display: flex;
  justify-content: center;
  height: 50px;
  position: relative;
}

.nav .link {
  color: var(--color-text);
  display: block;
  text-align: center;
  line-height: 50px;
  width: 70px;
  transition: all 0.2s ease;
  border-bottom: 2px solid transparent;
}

.nav .link:hover {
  color: var(--color-light);
  text-shadow: 0px 0px 1px var(--color-light);
}

.nav-track {
  position: absolute;
  background-color: var(--color-light);
  height: 4px;
  border-radius: 2px;
  width: 50px;
  left: v-bind('nav_track_left');
  bottom: 0px;
  transition: .3s;
}

.login {
  display: flex;
  flex-direction: column;
  align-items: center;
  width: 300px;
  padding: 30px 30px 20px 30px;
  border-radius: 20px;
  color: var(--color-text);
  background-color: var(--color-background);
}

.login input {
  outline: none;
  border: none;
  border-bottom: 1px solid var(--color-text);
  width: 100%;
  padding: 5px 0;
  margin-bottom: 20px;
  text-align: center;
  transition: all 0.3s;
  color: var(--color-text);
  background-color: transparent;
}

.login input:focus {
  border-bottom: 1px solid var(--color-light);
}

.login a {
  display: block;
  text-align: center;
  color: var(--color-background);
  width: 100%;
  height: 40px;
  transition: all 0.3s;
  border-radius: 20px;
  background-color: var(--color-light);
  line-height: 40px;
}

.login a:hover {
  cursor: pointer;
  box-shadow: 0 0 5px var(--color-light);
}

/* 去掉input框的异常样式（小眼睛、自动填充） */
#n1::-webkit-outer-spin-button,
#n1::-webkit-inner-spin-button {
  -webkit-appearance: none !important;
  margin: 0;
}

input[type=password]::-ms-reveal {
  display: none;
}

input:-internal-autofill-previewed,
input:-internal-autofill-selected {
  transition: background-color 5000s ease-out 0.5s;
}
</style>

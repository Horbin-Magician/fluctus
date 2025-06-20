<!-- 页头 Header -->
<script setup>
import { ref, h, reactive } from 'vue'
import { NModal, useMessage, NDropdown, NIcon } from 'naive-ui'
import {
  CloudOutline as PanIcon,
  BookOutline as BlogIcon,
  Apps as AppsIcon,
  Sunny as SunIcon,
  Moon as MoonIcon,
} from "@vicons/ionicons5";
import '@/assets/icons/iconfont'
import { userlogin, initUser, checkLogin, userlogout, addUpdateFun } from '@/utils/userUtils';
import storageUtils from '@/utils/storageUtils';

const route = useRoute()
const message = useMessage()
const docBody = document.body

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
const theme = ref(docBody.getAttribute('theme'))
const user_name = ref('')
const user_key = ref('')

function renderIcon(icon) {
  return () => {
    return h(NIcon, null, {
      default: () => h(icon)
    });
  };
}

const app_options = [
  { label: '网盘', key: 'pan', icon: renderIcon(PanIcon) },
  { label: '博客', key: 'blog', icon: renderIcon(BlogIcon) }
]

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

// 初始化theme信息
const theme_storaged = storageUtils.getTheme()
if (theme_storaged != null && theme_storaged != theme.value) {
  docBody.setAttribute('theme', theme_storaged)
  theme.value = theme_storaged
}

// 定义函数
const switchDocumentTheme = () => {
  theme.value = (theme.value == "light") ? "dark" : "light"
  docBody.setAttribute('theme', theme.value)
  storageUtils.setTheme(theme.value)
}

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

function handleAppSelect(key) {
  if (key == "pan") {
    window.location.href = 'https://pan.fluctus.cc/'
  } else if (key == "blog") {
    window.location.href = 'https://blog.fluctus.cc/'
  }
}
</script>

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
      <div class="theme" @click="switchDocumentTheme">
        <div class="icon">
          <n-icon v-if="theme == 'light'" size="26">
            <SunIcon />
          </n-icon>
          <n-icon v-if="theme == 'dark'" size="26">
            <MoonIcon />
          </n-icon>
        </div>
      </div>
      <div class="app">
        <n-dropdown trigger="hover" :options="app_options" :show-arrow="true" @select="handleAppSelect">
          <n-icon size="26">
            <AppsIcon />
          </n-icon>
        </n-dropdown>
      </div>
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

<style scoped>
header {
  height: 50px;
  margin: 0 auto;
  display: flex;
  justify-content: space-between;
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
}

.logo:hover {
  animation: shake 0.2s linear;
  cursor: pointer;
  filter: drop-shadow(0px 0px 1px var(--color-light));
}

.left-bar {
  display: flex;
  align-items: center;
}

.nav {
  display: flex;
  justify-content: center;
  height: 50px;
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

.app {
  width: 26px;
  height: 26px;
  margin-left: 20px;
  margin-right: 20px;
}

.app:hover {
  cursor: pointer;
  color: var(--color-light);
  filter: drop-shadow(0px 0px 1px var(--color-light));
}

.theme {
  width: 26px;
  height: 26px;
  margin-left: 10px;
  transition: transform 0.2s ease;
  transform-origin: center center;
}

.theme:hover {
  cursor: pointer;
  transform: rotate(180deg);
  color: var(--color-light);
  filter: drop-shadow(0px 0px 1px var(--color-light));
}

.icon {
  width: 26px;
  height: 26px;
  overflow: hidden;
  fill: currentColor;
}

.logo-login svg {
  height: 60px;
  width: 60px;
  color: var(--color-light);
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

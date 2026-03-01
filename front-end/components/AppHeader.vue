<!-- 页头 Header -->
<template>
  <header :class="{ 'header-hidden': isHeaderHidden }">
    <div class="logo">
      <n-dropdown v-if="isLoggedIn" :options="dropdownOptions" trigger="hover" show-arrow
          @select="onDropdownSelect">
          <svg class="icon" aria-hidden="true">
            <use xlink:href="#icon-logo" />
          </svg>
      </n-dropdown>
      <svg v-else class="icon" aria-hidden="true" @click="showLoginModal = true">
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
import { h, ref, reactive, onMounted, onUnmounted } from 'vue'
import { NModal, NDropdown, NIcon, useMessage } from 'naive-ui'
import { SettingsOutline, LogOutOutline } from '@vicons/ionicons5'
import '@/assets/icons/iconfont'
import { userlogin, checkLogin, userlogout, addUpdateFun } from '@/utils/userUtils';
import storageUtils from '@/utils/storageUtils';
import ThemeToggle from '@/components/ThemeToggle.vue'

const route = useRoute()
const message = useMessage()

const router_items = reactive({
  '首页': { path: '/', shown: true },
  '日历': { path: '/calendar', shown: !!storageUtils.getUser().username },
  '旅记': { path: '/travel', shown: !!storageUtils.getUser().username },
  '博客': { path: '/blog', shown: true }
})

const navLinks = computed(() => Object.entries(router_items)
  .filter(([_, v]) => v.shown)
  .map(([_, value]) => [value.path.slice(1)]))
const now_page = computed(() => route.path.slice(1).split('/')[0])
const isMobile = ref(false)
const nav_link_width = computed(() => isMobile.value ? '56px' : '70px')
const nav_track_width = computed(() => isMobile.value ? '40px' : '50px')
const nav_track_left = computed(() => {
  const idx = navLinks.value.findIndex(([key]) => key === (now_page.value))
  const linkWidth = isMobile.value ? 56 : 70
  const trackWidth = isMobile.value ? 40 : 50
  const offset = (linkWidth - trackWidth) / 2
  return `${offset + idx * linkWidth}px`
})

const showLoginModal = ref(false)
const showLogoutModal = ref(false)
const user_name = ref('')
const user_key = ref('')
const isHeaderHidden = ref(false)
const isLoggedIn = ref(checkLogin())

function renderIcon(icon) {
  return () => h(NIcon, null, { default: () => h(icon) })
}

const dropdownOptions = [
  {
    label: '后台管理',
    key: 'admin',
    icon: renderIcon(SettingsOutline)
  },
  {
    label: '注销',
    key: 'logout',
    icon: renderIcon(LogOutOutline)
  }
]

function handleScroll() {
  isHeaderHidden.value = window.scrollY > 0
}

function updateViewportState() {
  isMobile.value = window.innerWidth <= 640
}

onMounted(() => {
  window.addEventListener('scroll', handleScroll)
  window.addEventListener('resize', updateViewportState)
  handleScroll()
  updateViewportState()
})

onUnmounted(() => {
  window.removeEventListener('scroll', handleScroll)
  window.removeEventListener('resize', updateViewportState)
})

addUpdateFun(() => {
  const loggedIn = checkLogin()
  isLoggedIn.value = loggedIn
  router_items['日历'].shown = loggedIn
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

function onDropdownSelect(key) {
  if (key === 'admin') {
    navigateTo('/admin')
  } else if (key === 'logout') {
    showLogoutModal.value = true
  }
}

function logout() {
  userlogout()
  showLogoutModal.value = false
  message.success("注销成功！")
  navigateTo('/')
}
</script>

<style scoped>
header {
  position: fixed;
  top: 10px;
  left: 50%;
  transform: translateX(-50%) translateY(0);
  width: min(600px, calc(100vw - 16px));
  height: 50px;
  border-radius: 20px;
  display: flex;
  justify-content: space-between;
  border: 1px solid var(--color-border);
  background-color: var(--color-background);
  box-shadow: 0 2px 8px var(--color-shadow);
  z-index: 2;
  transition: transform 0.5s cubic-bezier(0.4, 0, 0.2, 1);
}

header.header-hidden {
  transform: translateX(-50%) translateY(-80px);
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
  flex-shrink: 0;
}

.logo :deep(> *) {
  outline: none;
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
  min-width: 0;
}

.nav {
  display: flex;
  justify-content: center;
  height: 50px;
  position: relative;
  min-width: 0;
}

.nav .link {
  color: var(--color-text);
  display: block;
  text-align: center;
  line-height: 50px;
  width: v-bind('nav_link_width');
  transition: all 0.2s ease;
  border-bottom: 2px solid transparent;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
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
  width: v-bind('nav_track_width');
  left: v-bind('nav_track_left');
  bottom: 0px;
  transition: .3s;
}

@media (max-width: 640px) {
  header {
    top: 8px;
    height: 46px;
    border-radius: 16px;
  }

  .logo {
    height: 46px;
    margin-left: 10px;
    margin-right: 8px;
  }

  .logo svg {
    width: 42px;
    height: 42px;
    margin-top: 2px;
  }

  .left-bar {
    margin-right: 10px;
    gap: 2px;
  }

  .nav {
    height: 46px;
  }

  .nav .link {
    line-height: 46px;
    font-size: 13px;
  }

  .nav-track {
    bottom: 1px;
  }
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

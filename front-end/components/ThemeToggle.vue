<!-- 主题切换按钮 Theme Toggle -->
<script setup>
import { ref } from 'vue'
import { NIcon } from 'naive-ui'
import { Sunny as SunIcon, Moon as MoonIcon } from "@vicons/ionicons5"
import storageUtils from '@/utils/storageUtils'

const docBody = document.body
const theme = ref(docBody.getAttribute('theme'))

// 初始化theme信息
const theme_storaged = storageUtils.getTheme()
if (theme_storaged != null && theme_storaged != theme.value) {
  docBody.setAttribute('theme', theme_storaged)
  theme.value = theme_storaged
}

// 切换主题
const switchDocumentTheme = () => {
  theme.value = (theme.value == "light") ? "dark" : "light"
  docBody.setAttribute('theme', theme.value)
  storageUtils.setTheme(theme.value)
}
</script>

<template>
  <div class="theme-toggle" @click="switchDocumentTheme">
    <div class="toggle-track">
      <div class="toggle-thumb" :class="{ 'dark': theme === 'dark' }">
        <n-icon size="18">
          <SunIcon v-if="theme === 'light'" />
          <MoonIcon v-else />
        </n-icon>
      </div>
      <div class="toggle-icons">
        <n-icon class="sun-bg" size="14">
          <SunIcon />
        </n-icon>
        <n-icon class="moon-bg" size="14">
          <MoonIcon />
        </n-icon>
      </div>
    </div>
  </div>
</template>

<style scoped>
.theme-toggle {
  margin-left: 10px;
  cursor: pointer;
}

.toggle-track {
  position: relative;
  width: 50px;
  height: 26px;
  background: linear-gradient(to right, #ffd700 0%, #87ceeb 100%);
  border-radius: 13px;
  transition: all 0.4s ease;
  box-shadow: inset 0 2px 4px rgba(0, 0, 0, 0.2);
  overflow: hidden;
}

.toggle-track:hover {
  box-shadow: inset 0 2px 4px rgba(0, 0, 0, 0.2), 
              0 0 8px var(--color-light);
}

.toggle-icons {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 6px;
  pointer-events: none;
}

.sun-bg {
  color: #fff;
  opacity: 0.6;
  transition: all 0.4s ease;
}

.moon-bg {
  color: #fff;
  opacity: 0.6;
  transition: all 0.4s ease;
}

.toggle-thumb {
  position: absolute;
  top: 2px;
  left: 2px;
  width: 22px;
  height: 22px;
  background: #fff;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.4s cubic-bezier(0.68, -0.55, 0.265, 1.55);
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.3);
  color: #ffa500;
}

.toggle-thumb.dark {
  left: 26px;
  color: #4169e1;
  transform: rotate(360deg);
}

.toggle-thumb:hover {
  transform: scale(1.1);
}

.toggle-thumb.dark:hover {
  transform: scale(1.1) rotate(360deg);
}
</style>

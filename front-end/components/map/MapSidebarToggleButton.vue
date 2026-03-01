<template>
  <button class="sidebar-toggle-btn" :class="{ 'sidebar-open': sidebarOpen }" @click="$emit('toggle-sidebar')">
    {{ sidebarOpen ? '◀' : '▶' }}
  </button>
</template>

<script setup>
defineProps({
  sidebarOpen: { type: Boolean, default: true }
})

defineEmits(['toggle-sidebar'])
</script>

<style scoped>
.sidebar-toggle-btn {
  position: absolute;
  top: 70px;
  left: 16px;
  z-index: 99;
  background: color-mix(in srgb, var(--color-background-soft) 95%, transparent);
  backdrop-filter: blur(10px);
  border: none;
  width: 36px;
  height: 36px;
  border-radius: 10px;
  cursor: pointer;
  box-shadow: 0 2px 8px var(--color-shadow);
  font-size: 14px;
  color: var(--color-text);
  transition: opacity 0.3s ease;
  display: flex;
  align-items: center;
  justify-content: center;
}

.sidebar-toggle-btn.sidebar-open {
  opacity: 0;
  pointer-events: none;
}

@media (max-width: 768px) {
  .sidebar-toggle-btn {
    left: 16px;
  }
}
</style>

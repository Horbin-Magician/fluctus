<template>
  <div class="search-source-container" :class="{ expanded: isExpanded }" tabindex="-1" @focusout="handleFocusOut">
    <svg class="search-icon current-source" :title="searchSources[currentSource]?.name" @click="toggleExpanded">
      <use :xlink:href="`#icon-${currentSource}`" />
    </svg>

    <transition name="slide">
      <div v-if="isExpanded" class="source-options">
        <svg v-for="sourceKey in availableSources" :key="sourceKey" class="search-icon source-option"
          :title="searchSources[sourceKey]?.name" @click="selectSource(sourceKey)">
          <use :xlink:href="`#icon-${sourceKey}`" />
        </svg>
      </div>
    </transition>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import type { SearchSource } from '@/composables/useSearch'

interface Props {
  currentSource: string
  searchSources: Record<string, SearchSource>
}

interface Emits {
  (e: 'change', sourceKey: string): void
}

const props = defineProps<Props>()
const emit = defineEmits<Emits>()

const isExpanded = ref(false)

const availableSources = computed(() =>
  Object.keys(props.searchSources).filter(key => key !== props.currentSource)
)

const toggleExpanded = () => {
  isExpanded.value = !isExpanded.value
}

const selectSource = (sourceKey: string) => {
  emit('change', sourceKey)
  isExpanded.value = false
}

const handleFocusOut = () => {
  isExpanded.value = false
}
</script>

<style scoped>
.search-source-container {
  display: flex;
  align-items: center;
  height: 28px;
  border-radius: 14px;
  overflow: hidden;
  transition: width 0.2s ease-out;
  width: 28px;
}

.search-source-container.expanded {
  width: 100px;
}

.search-icon {
  width: 28px;
  height: 28px;
  border-radius: 14px;
  color: var(--color-light);
  fill: var(--color-light);
  cursor: pointer;
  flex-shrink: 0;
}

.search-icon:hover {
  filter: drop-shadow(0px 0px 1px var(--color-light));
}

.current-source {
  z-index: 2;
}

.source-options {
  display: flex;
  align-items: center;
  margin-left: 4px;
  gap: 4px;
}

.source-option {
  opacity: 0.8;
}

.source-option:hover {
  opacity: 1;
}

.slide-enter-active,
.slide-leave-active {
  transition: all 0.2s ease-out;
}

.slide-enter-from,
.slide-leave-to {
  opacity: 0;
  transform: translateX(-10px);
}
</style>

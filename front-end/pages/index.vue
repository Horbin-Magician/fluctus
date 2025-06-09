<!-- 主页 Home -->
<template>
  <div class="container">
    <svg id="homelogo">
      <use xlink:href="#icon-homelogo" />
    </svg>
    
    <div 
      class="search-div" 
      :style="{ height: searchDivHeight }"
      tabindex="0" 
      @keyup.up.prevent="navigateUp"
      @keyup.down.prevent="navigateDown"
      @keyup.enter="performSearch"
      @focusin="searchIsFocused = true"
      @focusout="searchIsFocused = false"
    >
      <div class="search-input-container">
        <SearchSourceSelector
          :current-source="currentSearchSource"
          :search-sources="searchSources"
          @change="changeSearchSource"
        />
        
        <input 
          v-model="searchValue"
          class="search-input"
          @keydown="preventArrowKeys"
        >
        
        <n-icon 
          size="28" 
          class="search-button" 
          @mousedown="performSearch"
        >
          <SearchIcon />
        </n-icon>
      </div>
      
      <!-- 搜索建议列表 -->
      <div v-if="sugList.length > 0" class="suggestions-container">
        <div
          v-for="(suggestion, index) in sugList"
          :key="index"
          :class="['suggestion-item', { selected: selectedSugIndex === index }]"
          @mouseenter="setSelectedIndex(index)"
          @click="performSearch"
        >
          {{ suggestion.q }}
        </div>
      </div>
      
      <!-- 错误提示 -->
      <div v-if="error" class="error-message">
        {{ error }}
      </div>
    </div>
    
    <div class="overlay" />
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { NIcon } from 'naive-ui'
import { Search as SearchIcon } from '@vicons/ionicons5'
import '@/assets/icons/iconfont'
import { useSearch } from '@/composables/useSearch'
import SearchSourceSelector from '@/components/SearchSourceSelector.vue'

// 使用搜索 composable
const {
  searchValue,
  sugList,
  selectedSugIndex,
  error,
  currentSearchSource,
  searchSources,
  performSearch,
  navigateUp,
  navigateDown,
  changeSearchSource,
  setSelectedIndex
} = useSearch()

const searchIsFocused = ref(false)

// 计算搜索框高度
const searchDivHeight = computed(() => {
  const baseHeight = 40
  const suggestionHeight = 34
  if (!searchIsFocused.value || sugList.value.length === 0) {
    return `${baseHeight}px`
  }
  const totalHeight = baseHeight + (sugList.value.length * suggestionHeight) + 8
  return `${totalHeight}px`
})

// 阻止上下箭头键的默认行为
const preventArrowKeys = (event: KeyboardEvent) => {
  if (event.key === 'ArrowUp' || event.key === 'ArrowDown') {
    event.preventDefault()
  }
}
</script>

<style scoped>
.container {
  height: calc(100vh - 80px);
  display: grid;
  grid-template-rows: 24vh 100px 60px;
  place-items: center;
}

#homelogo {
  grid-row-start: 2;
  height: 100px;
  width: 200px;
  fill: var(--color-light);
  animation: floatImage 4s ease-in-out infinite;
}

.search-div {
  margin-top: 10px;
  padding: 0 4px;
  grid-row-start: 3;
  align-self: flex-start;
  border: 2px solid var(--color-light);
  border-radius: 20px;
  transition: all 0.2s ease-out;
  overflow: hidden;
  background-color: var(--color-background);
  z-index: 200;
  min-height: 40px;
}

.search-div:hover,
.search-div:focus-within {
  box-shadow: 0 0 5px var(--color-light);
}

.search-div:focus-within ~ .overlay {
  z-index: 100;
  background: rgba(0, 0, 0, 0.3);
}

.search-div:focus-within .search-input-container {
  width: 500px;
}

.search-input-container {
  display: flex;
  height: 36px;
  align-items: center;
  width: 400px;
  justify-content: space-between;
  transition: all 0.2s ease-out;
  gap: 8px;
  padding: 2px 0;
}

.search-input {
  background-color: transparent;
  border: none;
  outline: none;
  text-align: center;
  height: 100%;
  font-size: 16px;
  color: var(--color-text);
  flex-grow: 1;
  min-width: 0;
}

.search-input::placeholder {
  color: var(--color-text-sub);
  opacity: 0.6;
}

.search-button {
  color: var(--color-light);
  cursor: pointer;
  transition: all 0.2s ease;
}

.search-button:hover {
  filter: drop-shadow(0px 0px 1px var(--color-light));
  transform: scale(1.05);
}

.search-button.loading {
  animation: spin 1s linear infinite;
}

.suggestions-container {
  border-top: 1px solid var(--color-border, #e0e0e0);
  margin-top: 4px;
}

.suggestion-item {
  width: 100%;
  height: 34px;
  line-height: 34px;
  text-align: center;
  font-size: 16px;
  color: var(--color-text-sub);
  cursor: pointer;
  transition: background-color 0.15s ease;
}

.suggestion-item:hover,
.suggestion-item.selected {
  background-color: var(--color-light-light, rgba(64, 158, 255, 0.1));
  color: var(--color-text);
}

.suggestion-item:last-child {
  border-radius: 0 0 16px 16px;
}

.error-message {
  padding: 8px;
  text-align: center;
  color: var(--color-error, #f56565);
  font-size: 14px;
  border-top: 1px solid var(--color-border, #e0e0e0);
}

.overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  transition: 0.3s ease-out;
  z-index: -1;
}

@keyframes floatImage {
  0% { transform: translateY(0); }
  50% { transform: translateY(-4px); }
  100% { transform: translateY(0); }
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

/* 响应式设计 */
@media (max-width: 768px) {
  .container {
    grid-template-rows: 20vh 80px 60px;
  }
  
  #homelogo {
    height: 80px;
    width: 160px;
  }
  
  .search-input-container {
    width: 300px;
  }
  
  .search-input-container:focus-within {
    width: 350px;
  }
}

@media (max-width: 480px) {
  .search-input-container {
    width: 280px;
  }
  
  .search-input-container:focus-within {
    width: 300px;
  }
  
  .suggestion-item {
    font-size: 14px;
  }
}
</style>

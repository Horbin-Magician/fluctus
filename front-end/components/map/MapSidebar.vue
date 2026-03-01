<template>
  <div class="sidebar" :class="{ collapsed: !sidebarOpen }">
    <div class="sidebar-content">
      <div class="sidebar-header">
        <button class="back-btn" @click="$emit('back')">
          <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24"
            fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"
            stroke-linejoin="round">
            <polyline points="15 18 9 12 15 6"/>
          </svg>
        </button>
        <div class="sidebar-diary-info">
          <span class="sidebar-diary-name">{{ diaryName }}</span>
          <span v-if="diaryTripTime" class="sidebar-diary-trip-time">{{ diaryTripTime }}</span>
          <span v-if="diarySummary" class="sidebar-diary-summary">{{ diarySummary }}</span>
        </div>
        <button class="sidebar-edit-btn" title="编辑日记信息" @click="$emit('edit-diary')">
          <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24"
            fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"
            stroke-linejoin="round">
            <path d="M12 20h9"/>
            <path d="M16.5 3.5a2.12 2.12 0 0 1 3 3L7 19l-4 1 1-4 12.5-12.5z"/>
          </svg>
        </button>
        <button class="sidebar-close-btn" @click="$emit('toggle-sidebar')">×</button>
      </div>

      <div ref="searchSectionRef" class="sidebar-section">
        <div class="search-box">
          <input
            id="search_input"
            :value="searchKeyword"
            type="text"
            placeholder="搜索地点、景点、餐厅..."
            @input="handleKeywordInput"
            @blur="$emit('search-blur')"
            @keyup.enter="$emit('search')"
          >
          <button class="search-btn" @click="$emit('search')">
            <SearchOutline class="search-icon" />
          </button>
        </div>
        <div v-if="searchResults.length > 0" class="search-results">
          <div
            v-for="(result, index) in searchResults"
            :key="index"
            class="search-result-item"
            @mousedown.prevent="$emit('suggestion-mousedown')"
            @click="$emit('select-search-result', result)"
          >
            <div class="result-name">{{ result.name }}</div>
            <div class="result-address">{{ result.address }}</div>
          </div>
        </div>
      </div>

      <div class="sidebar-divider"/>

      <div class="sidebar-section">
        <div class="sidebar-section-title clickable" @click="$emit('toggle-places')">
          <h3>日记地点 ({{ places.length }})</h3>
          <span class="favorites-toggle">{{ showPlaces ? '收起' : '展开' }}</span>
        </div>
        <div v-if="showPlaces" class="favorites-list route-days">
          <div
            v-for="day in displayDays"
            :key="`day-${day}`"
            class="route-day-group"
            :class="{ 'is-drag-over': dragOverDay === day }"
            @dragover.prevent="$emit('day-dragover', day, $event)"
            @drop="$emit('day-drop', day)"
          >
            <div class="route-day-title">第 {{ day }} 天</div>
            <template
              v-for="(place, index) in getPlacesByDay(day)"
              :key="place.id"
            >
              <div
                class="favorite-item"
                :class="{
                  'is-dragging': draggingPlaceId === place.id,
                  'drop-before': isDropIndicator(day, place.id, 'before'),
                  'drop-after': isDropIndicator(day, place.id, 'after')
                }"
                draggable="true"
                @dragstart="$emit('place-dragstart', place.id)"
                @dragend="$emit('place-dragend')"
                @dragover.prevent.stop="$emit('place-dragover', day, place.id, $event)"
                @drop.stop="$emit('place-drop', day, place.id)"
                @click="$emit('go-to-place', place)"
              >
                <div class="favorite-info">
                  <div class="favorite-name">{{ place.name }}</div>
                  <div class="favorite-address">{{ getPlaceSubtitle(place) }}</div>
                </div>
                <button class="remove-favorite" @click.stop="$emit('remove-place', place.id)">
                  <TrashOutline class="remove-icon" />
                </button>
              </div>
              <div
                v-if="index < getPlacesByDay(day).length - 1"
                class="route-leg"
                @dragover.prevent.stop="$emit('route-leg-dragover', day, index)"
                @drop.stop="$emit('route-leg-drop', day, index)"
              >
                {{ getAdjacentDrivingText(day, index) }}
              </div>
            </template>
            <div
              v-if="isDropIndicator(day, null, 'end')"
              class="route-drop-indicator"
            >
              <span>插入末尾</span>
            </div>
            <div v-if="getPlacesByDay(day).length === 0" class="route-day-empty">拖拽地点到这一天</div>
          </div>
          <button class="route-add-day-btn" @click="$emit('add-route-day')">+ 新增一天</button>
          <div v-if="places.length === 0" class="no-favorites">暂无地点，搜索并添加吧</div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { SearchOutline, TrashOutline } from '@vicons/ionicons5'

defineProps({
  sidebarOpen: { type: Boolean, default: true },
  diaryName: { type: String, default: '' },
  diaryTripTime: { type: String, default: '' },
  diarySummary: { type: String, default: '' },
  searchKeyword: { type: String, default: '' },
  searchResults: { type: Array, default: () => [] },
  showPlaces: { type: Boolean, default: true },
  places: { type: Array, default: () => [] },
  displayDays: { type: Array, default: () => [] },
  getPlacesByDay: { type: Function, required: true },
  dragOverDay: { type: [Number, String, null], default: null },
  draggingPlaceId: { type: [Number, String, null], default: null },
  isDropIndicator: { type: Function, required: true },
  getAdjacentDrivingText: { type: Function, required: true },
  getPlaceSubtitle: { type: Function, required: true },
})

const emit = defineEmits([
  'back',
  'edit-diary',
  'toggle-sidebar',
  'update:search-keyword',
  'keyword-input',
  'search-blur',
  'search',
  'suggestion-mousedown',
  'select-search-result',
  'toggle-places',
  'day-dragover',
  'day-drop',
  'place-dragstart',
  'place-dragend',
  'place-dragover',
  'place-drop',
  'route-leg-dragover',
  'route-leg-drop',
  'add-route-day',
  'remove-place',
  'go-to-place',
])

const searchSectionRef = ref(null)

const handleKeywordInput = (event) => {
  emit('update:search-keyword', event.target.value)
  emit('keyword-input')
}

const getSearchSectionElement = () => searchSectionRef.value

defineExpose({
  getSearchSectionElement,
})
</script>

<style scoped>
.sidebar {
  position: absolute;
  top: 70px;
  left: 16px;
  width: min(340px, calc(100vw - 32px));
  max-height: calc(100% - 86px);
  background: color-mix(in srgb, var(--color-background-soft) 92%, transparent);
  backdrop-filter: blur(12px);
  border: 1px solid var(--color-border);
  box-shadow: 0 10px 28px var(--color-shadow);
  border-radius: 12px;
  z-index: 100;
  transform: translateX(0);
  opacity: 1;
  visibility: visible;
  transition: transform 0.28s cubic-bezier(0.22, 0.61, 0.36, 1), opacity 0.22s ease;
  will-change: transform, opacity;
  overflow: hidden;
}

.sidebar.collapsed {
  transform: translateX(calc(-100% - 20px));
  opacity: 0;
  visibility: hidden;
  pointer-events: none;
}

.sidebar-content {
  padding: 0;
  position: relative;
  max-height: calc(100% - 2px);
  overflow-y: auto;
}

.sidebar-content::-webkit-scrollbar {
  width: 6px;
}

.sidebar-content::-webkit-scrollbar-track {
  background: transparent;
}

.sidebar-content::-webkit-scrollbar-thumb {
  background: color-mix(in srgb, var(--color-text-sub-sub) 50%, transparent);
  border-radius: 999px;
}

.sidebar-header {
  position: sticky;
  top: 0;
  z-index: 2;
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 14px 16px;
  background: color-mix(in srgb, var(--color-background-soft) 92%, transparent);
  backdrop-filter: blur(8px);
  border-bottom: 1px solid var(--color-border);
}

.back-btn {
  background: none;
  border: none;
  cursor: pointer;
  display: flex;
  align-items: center;
  color: var(--color-text-sub);
  padding: 4px;
  border-radius: 6px;
  transition: background 0.2s, color 0.2s;
  flex-shrink: 0;
}

.back-btn:hover {
  background: var(--color-light-light);
  color: var(--color-text);
}

.sidebar-diary-name {
  font-size: 15px;
  font-weight: 500;
  color: var(--color-text);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.sidebar-diary-info {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.sidebar-diary-trip-time {
  font-size: 12px;
  color: var(--color-text-sub);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.sidebar-diary-summary {
  font-size: 12px;
  color: var(--color-text-sub-sub);
  display: -webkit-box;
  line-clamp: 2;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.sidebar-close-btn {
  background: none;
  border: none;
  font-size: 18px;
  color: var(--color-text-sub-sub);
  cursor: pointer;
  width: 28px;
  height: 28px;
  border-radius: 6px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: background 0.2s, color 0.2s;
  flex-shrink: 0;
}

.sidebar-edit-btn {
  background: none;
  border: none;
  color: var(--color-text-sub-sub);
  cursor: pointer;
  width: 28px;
  height: 28px;
  border-radius: 6px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: background 0.2s, color 0.2s;
  flex-shrink: 0;
}

.sidebar-edit-btn:hover {
  background: var(--color-light-light);
  color: var(--color-text);
}

.sidebar-close-btn:hover {
  background: var(--color-light-light);
  color: var(--color-text);
}

.sidebar-section {
  margin-bottom: 12px;
  padding: 0 16px;
}

.sidebar-section:first-child {
  padding-top: 12px;
}

.sidebar-section-title {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
  padding: 0;
}

.sidebar-section-title h3 {
  margin: 0;
  font-size: 16px;
  color: var(--color-text);
}

.sidebar-section-title.clickable {
  cursor: pointer;
}

.favorites-toggle {
  font-size: 12px;
  color: var(--color-text-sub-sub);
}

.sidebar-divider {
  height: 1px;
  background: var(--color-border);
  margin: 12px 16px;
}

.search-box {
  margin-top: 12px;
  display: flex;
  gap: 8px;
}

.search-box input {
  flex: 1;
  padding: 8px 12px;
  border: 1px solid var(--color-border);
  border-radius: 6px;
  font-size: 14px;
  color: var(--color-text);
  background: var(--color-background-soft);
  outline: none;
}

.search-box input:focus {
  border-color: var(--color-primary);
}

.search-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 8px 12px;
  border: none;
  border-radius: 6px;
  background: var(--color-primary);
  color: var(--color-background);
  cursor: pointer;
}

.search-icon {
  width: 16px;
  height: 16px;
}

.search-results {
  max-height: 300px;
  overflow-y: auto;
  margin: 10px -16px 0;
  padding: 0 16px;
}

.search-result-item {
  padding: 10px;
  border-bottom: 1px solid var(--color-border);
  cursor: pointer;
  transition: background 0.2s;
}

.search-result-item:hover {
  background: var(--color-light-light);
}

.result-name {
  font-size: 14px;
  font-weight: 500;
  color: var(--color-text);
}

.result-address {
  font-size: 12px;
  color: var(--color-text-sub-sub);
  margin-top: 2px;
}

.favorites-list {
  max-height: 300px;
  overflow-y: auto;
  margin: 0 -16px;
  padding: 0 16px;
}

.route-days {
  max-height: 360px;
}

.route-day-group {
  border: 1px solid var(--color-border);
  border-radius: 10px;
  padding: 8px;
  margin-bottom: 10px;
  background: color-mix(in srgb, var(--color-background-soft) 70%, transparent);
}

.route-day-group.is-drag-over {
  border-color: var(--color-primary);
  box-shadow: 0 0 0 1px color-mix(in srgb, var(--color-primary) 50%, transparent) inset;
}

.route-day-title {
  font-size: 12px;
  color: var(--color-text-sub);
  font-weight: 600;
  margin-bottom: 6px;
  padding: 2px 4px;
}

.route-day-empty {
  font-size: 12px;
  color: var(--color-text-sub-sub);
  text-align: center;
  padding: 10px 4px 6px;
}

.route-leg {
  margin: -2px 4px 8px;
  padding-left: 10px;
  font-size: 11px;
  color: var(--color-text-sub-sub);
}

.route-drop-indicator {
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 3px 2px 8px;
  height: 12px;
}

.route-drop-indicator::before,
.route-drop-indicator::after {
  content: '';
  flex: 1;
  border-top: 2px solid var(--color-primary);
  opacity: 0.9;
}

.route-drop-indicator::before {
  margin-right: 6px;
}

.route-drop-indicator::after {
  margin-left: 6px;
}

.route-drop-indicator span {
  flex: 0 0 auto;
  font-size: 10px;
  line-height: 1;
  color: var(--color-primary);
  background: var(--color-background-soft);
  padding: 0 4px;
  border-radius: 999px;
  border: 1px solid color-mix(in srgb, var(--color-primary) 30%, transparent);
}

.route-add-day-btn {
  width: 100%;
  border: 1px dashed var(--color-border);
  background: var(--color-background-soft);
  color: var(--color-text-sub);
  border-radius: 8px;
  padding: 6px 10px;
  font-size: 12px;
  cursor: pointer;
  margin-top: 4px;
}

.route-add-day-btn:hover {
  border-color: var(--color-primary);
  color: var(--color-primary);
}

.favorite-item {
  position: relative;
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 11px 12px;
  margin-bottom: 8px;
  border: 1px solid var(--color-border);
  border-radius: 12px;
  background: var(--color-background);
  cursor: pointer;
  transition: transform 0.2s ease, box-shadow 0.2s ease, background 0.2s ease, border-color 0.2s ease;
}

.favorite-item.is-dragging {
  opacity: 0.5;
}

.favorite-item.drop-before::before,
.favorite-item.drop-after::after {
  content: '';
  position: absolute;
  left: -2px;
  right: -2px;
  height: 0;
  border-top: 2px solid var(--color-primary);
  pointer-events: none;
  z-index: 2;
}

.favorite-item.drop-before::before {
  top: -5px;
}

.favorite-item.drop-after::after {
  bottom: -5px;
}

.favorite-item:hover {
  background: var(--color-light-light);
  border-color: color-mix(in srgb, var(--color-primary) 30%, var(--color-border));
  transform: translateY(-1px);
  box-shadow: 0 4px 12px var(--color-shadow);
}

.favorite-info {
  flex: 1;
  min-width: 0;
}

.favorite-name {
  font-size: 14px;
  color: var(--color-text);
}

.favorite-address {
  font-size: 12px;
  color: var(--color-text-sub-sub);
  margin-top: 2px;
}

.no-favorites {
  text-align: center;
  color: var(--color-text-sub-sub);
  padding: 20px 0;
  font-size: 13px;
}

.remove-favorite {
  display: flex;
  align-items: center;
  justify-content: center;
  background: none;
  border: none;
  cursor: pointer;
  padding: 4px;
  opacity: 0.5;
  transition: opacity 0.2s;
}

.remove-icon {
  width: 14px;
  height: 14px;
}

.remove-favorite:hover {
  opacity: 1;
}

@media (max-width: 768px) {
  .sidebar {
    width: calc(100% - 32px);
    left: 16px;
  }
}

.search-results::-webkit-scrollbar,
.favorites-list::-webkit-scrollbar {
  width: 6px;
}

.search-results::-webkit-scrollbar-track,
.favorites-list::-webkit-scrollbar-track {
  background: var(--color-background);
  border-radius: 3px;
}

.search-results::-webkit-scrollbar-thumb,
.favorites-list::-webkit-scrollbar-thumb {
  background: color-mix(in srgb, var(--color-text-sub-sub) 80%, transparent);
  border-radius: 3px;
}

.search-results::-webkit-scrollbar-thumb:hover,
.favorites-list::-webkit-scrollbar-thumb:hover {
  background: color-mix(in srgb, var(--color-text-sub) 80%, transparent);
}
</style>

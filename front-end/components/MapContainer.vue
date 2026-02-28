<template>
  <div class="map-container">
    <div id="amap"/>

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
          <button class="sidebar-edit-btn" title="编辑日记信息" @click="_emit('edit-diary')">
            <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24"
              fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"
              stroke-linejoin="round">
              <path d="M12 20h9"/>
              <path d="M16.5 3.5a2.12 2.12 0 0 1 3 3L7 19l-4 1 1-4 12.5-12.5z"/>
            </svg>
          </button>
          <button class="sidebar-close-btn" @click="toggleSidebar">×</button>
        </div>
        <div ref="searchSectionRef" class="sidebar-section">
          <div class="search-box">
            <input
              id="search_input"
              v-model="searchKeyword"
              type="text"
              placeholder="搜索地点、景点、餐厅..."
              @input="handleKeywordInput"
              @blur="handleSearchBlur"
              @keyup.enter="handleSearch"
            >
            <button class="search-btn" @click="handleSearch">
              <SearchOutline class="search-icon" />
            </button>
          </div>
          <div v-if="searchResults.length > 0" class="search-results">
            <div
              v-for="(result, index) in searchResults"
              :key="index"
              class="search-result-item"
              @mousedown.prevent="beginSuggestionSelection"
              @click="selectSearchResult(result)"
            >
              <div class="result-name">{{ result.name }}</div>
              <div class="result-address">{{ result.address }}</div>
            </div>
          </div>
        </div>
        <div class="sidebar-divider"/>
        <div class="sidebar-section">
          <div class="sidebar-section-title clickable" @click="showPlaces = !showPlaces">
            <h3>日记地点 ({{ places.length }})</h3>
            <span class="favorites-toggle">{{ showPlaces ? '收起' : '展开' }}</span>
          </div>
          <div v-if="showPlaces" class="favorites-list route-days">
            <div
              v-for="day in displayDays"
              :key="`day-${day}`"
              class="route-day-group"
              :class="{ 'is-drag-over': dragOverDay === day }"
              @dragover.prevent="onDayDragOver(day)"
              @drop="onDayDrop(day)"
            >
              <div class="route-day-title">第 {{ day }} 天</div>
              <div
                v-for="place in getPlacesByDay(day)"
                :key="place.id"
                class="favorite-item"
                :class="{ 'is-dragging': draggingPlaceId === place.id }"
                draggable="true"
                @dragstart="onPlaceDragStart(place.id)"
                @dragend="onPlaceDragEnd"
                @dragover.prevent="onPlaceDragOver(day, place.id)"
                @drop.stop="onPlaceDrop(day, place.id)"
                @click="goToPlace(place)"
              >
                <div class="favorite-info">
                  <div class="favorite-name">{{ place.name }}</div>
                  <div class="favorite-address">{{ place.address }}</div>
                </div>
                <button class="remove-favorite" @click.stop="$emit('remove-place', place.id)">
                  <TrashOutline class="remove-icon" />
                </button>
              </div>
              <div v-if="getPlacesByDay(day).length === 0" class="route-day-empty">拖拽地点到这一天</div>
            </div>
            <button class="route-add-day-btn" @click="addRouteDay">+ 新增一天</button>
            <div v-if="places.length === 0" class="no-favorites">暂无地点，搜索并添加吧</div>
          </div>
        </div>
      </div>
    </div>

    <button class="sidebar-toggle-btn" :class="{ 'sidebar-open': sidebarOpen }" @click="toggleSidebar">
      {{ sidebarOpen ? '◀' : '▶' }}
    </button>

    <div v-if="selectedMarker" class="marker-info-panel">
      <div class="marker-info-header">
        <h3>{{ selectedMarker.name }}</h3>
        <button class="close-btn" @click="closeMarkerInfo">×</button>
      </div>
      <div class="marker-info-content">
        <p><strong>地址:</strong> {{ selectedMarker.address }}</p>
        <p v-if="selectedMarker.tel"><strong>电话:</strong> {{ selectedMarker.tel }}</p>
        <p v-if="selectedMarker.type"><strong>类型:</strong> {{ selectedMarker.type }}</p>
        <p
          v-if="!isEditingDescription"
          :class="isPlaceInDiary(selectedMarker) ? 'marker-description-editable' : (selectedMarker.description ? '' : 'marker-description-empty')"
          @click="isPlaceInDiary(selectedMarker) ? startDescriptionEdit() : null"
        >
          <strong>简介:</strong>
          {{ selectedMarker.description || (isPlaceInDiary(selectedMarker) ? '暂无简介，点击编辑' : '暂无简介') }}
        </p>
        <div v-if="selectedMarker.images?.length" class="marker-image-section">
          <p class="marker-image-label"><strong>图片:</strong></p>
          <div class="marker-image-list">
            <a
              v-for="(image, index) in selectedMarker.images"
              :key="`${selectedMarker.id || selectedMarker.name}-${index}`"
              class="marker-image-link"
              :href="image"
              target="_blank"
              rel="noopener noreferrer"
            >
              <img :src="image" :alt="`${selectedMarker.name}-图片${index + 1}`" loading="lazy">
            </a>
          </div>
        </div>
        <div v-if="isPlaceInDiary(selectedMarker) && isEditingDescription" class="marker-description-section">
          <div class="marker-description-editor">
            <textarea
              v-model="descriptionDraft"
              class="marker-description-input"
              rows="3"
              maxlength="500"
              placeholder="输入你对这个地点的简介或备注"
            />
            <div class="marker-description-count">{{ descriptionDraft.length }}/500</div>
            <div class="marker-description-actions">
              <button class="marker-description-btn subtle" @click="cancelDescriptionEdit">取消</button>
              <button class="marker-description-btn primary" @click="saveDescriptionEdit">保存</button>
            </div>
          </div>
        </div>
        <div v-if="isPlaceInDiary(selectedMarker)" class="marker-type-section">
          <p class="marker-type-label"><strong>标记图标:</strong></p>
          <div class="marker-type-options">
            <button
              v-for="opt in markerTypeOptions"
              :key="opt.code"
              class="marker-type-btn"
              :class="{ active: getPlaceTypecode(selectedMarker) === opt.code }"
              :style="getPlaceTypecode(selectedMarker) === opt.code
                ? { borderColor: opt.color, background: opt.color, color: '#fff' }
                : { '--hover-color': opt.color }"
              :title="opt.label"
              @click="$emit('update-place-type', getPlaceDbId(selectedMarker), opt.code)"
            >
              <component :is="opt.icon" class="marker-type-icon" />
            </button>
          </div>
        </div>
        <div class="marker-actions">
          <button
            v-if="!isPlaceInDiary(selectedMarker)"
            class="action-btn favorite-btn"
            @click="$emit('add-place', selectedMarker)"
          >
            + 添加到日记
          </button>
          <button
            v-else
            class="action-btn favorite-btn active"
            @click="$emit('remove-place', getPlaceDbId(selectedMarker))"
          >
            - 从日记移除
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, watch, createVNode, render as vueRender } from "vue";
import {
  Restaurant as RestaurantIcon,
  Cart as CartIcon,
  Bed as BedIcon,
  Leaf as LeafIcon,
  Bus as BusIcon,
  Location as LocationIcon,
  SearchOutline,
  TrashOutline
} from "@vicons/ionicons5";
import { preloadAmap } from '@/utils/amapLoader';

// 将 xicons Vue 组件渲染为 SVG innerHTML 字符串
const renderIconSvgContent = (iconComp) => {
  const container = document.createElement('div');
  const vnode = createVNode(iconComp);
  vueRender(vnode, container);
  const svg = container.querySelector('svg');
  return svg ? svg.innerHTML : '';
};

const props = defineProps({
  places: { type: Array, default: () => [] },
  diaryName: { type: String, default: '' },
  diaryTripTime: { type: String, default: '' },
  diarySummary: { type: String, default: '' },
  initialView: { type: Object, default: null }
})
const _emit = defineEmits(['add-place', 'remove-place', 'update-place-type', 'update-place-description', 'update-route-plan', 'edit-diary', 'back', 'view-change'])

const searchKeyword = ref('');
const searchResults = ref([]);
const selectedMarker = ref(null);
const isEditingDescription = ref(false);
const descriptionDraft = ref('');
const showPlaces = ref(true);
const sidebarOpen = ref(true);
const searchSectionRef = ref(null);
const localPlaces = ref([]);
const draggingPlaceId = ref(null);
const dragOverDay = ref(null);
const manualDayCount = ref(1);

let map = null;
let AMap = null;
let placeSearch = null;
let autoComplete = null;
let autocompleteTimer = null;
let suggestionSelectionTimer = null;
let isSelectingSuggestion = false;
const mapReady = ref(false);
const searchMarkers = [];
const diaryMarkers = [];

const hasValidView = (view) => {
  const center = view?.center;
  const zoom = view?.zoom;
  return Array.isArray(center)
    && center.length === 2
    && Number.isFinite(center[0])
    && Number.isFinite(center[1])
    && Number.isFinite(zoom);
};

const parseDiaryTripDays = (tripTime) => {
  if (typeof tripTime !== 'string' || !tripTime.trim()) return 1;
  const matched = tripTime.trim().match(/^(\d{4}-\d{2}-\d{2})(?:\s*(?:至|~|-)\s*(\d{4}-\d{2}-\d{2}))?$/);
  if (!matched) return 1;
  const start = Date.parse(`${matched[1]}T00:00:00`);
  const end = Date.parse(`${(matched[2] || matched[1])}T00:00:00`);
  if (Number.isNaN(start) || Number.isNaN(end)) return 1;
  const minTime = Math.min(start, end);
  const maxTime = Math.max(start, end);
  const dayMs = 24 * 60 * 60 * 1000;
  return Math.max(1, Math.floor((maxTime - minTime) / dayMs) + 1);
};

const normalizeRoutePlaces = (places) => {
  if (!Array.isArray(places)) return [];
  return places.map((place, index) => ({
    ...place,
    routeDay: Number.isFinite(Number(place?.routeDay)) && Number(place.routeDay) >= 1
      ? Math.floor(Number(place.routeDay))
      : 1,
    routeOrder: Number.isFinite(Number(place?.routeOrder))
      ? Number(place.routeOrder)
      : index,
  }));
};

const tripDays = computed(() => parseDiaryTripDays(props.diaryTripTime));

const maxAssignedDay = computed(() => {
  if (localPlaces.value.length === 0) return 1;
  return Math.max(...localPlaces.value.map((place) => Number.isFinite(Number(place.routeDay)) ? Number(place.routeDay) : 1));
});

const displayDays = computed(() => {
  const count = Math.max(1, tripDays.value, manualDayCount.value, maxAssignedDay.value);
  return Array.from({ length: count }, (_, index) => index + 1);
});

const routePlaces = computed(() => localPlaces.value);

const hasValidInitialView = () => hasValidView(props.initialView);

const isSameViewAsCurrent = (view) => {
  if (!map || !hasValidView(view)) return false;
  const center = map.getCenter();
  const zoom = map.getZoom();
  if (!center || !Number.isFinite(zoom)) return false;
  const currentLng = center.getLng();
  const currentLat = center.getLat();
  const [targetLng, targetLat] = view.center;
  const lngDiff = Math.abs(currentLng - targetLng);
  const latDiff = Math.abs(currentLat - targetLat);
  const zoomDiff = Math.abs(zoom - view.zoom);
  return lngDiff < 0.000001 && latDiff < 0.000001 && zoomDiff < 0.001;
};

const applyInitialView = () => {
  if (!map || !hasValidInitialView()) return;
  if (isSameViewAsCurrent(props.initialView)) return;
  if (typeof map.setZoomAndCenter === 'function') {
    map.setZoomAndCenter(props.initialView.zoom, props.initialView.center, true);
    return;
  }
  map.setCenter(props.initialView.center, true);
  map.setZoom(props.initialView.zoom, true);
};

const emitCurrentView = () => {
  if (!map) return;
  const center = map.getCenter();
  const zoom = map.getZoom();
  if (!center || !Number.isFinite(zoom)) return;
  _emit('view-change', {
    center: [center.getLng(), center.getLat()],
    zoom
  });
};

onMounted(() => {
  initMap();
  document.addEventListener('click', handleDocumentClick);
});

const initMap = () => {
  preloadAmap()
    .then((loadedAMap) => {
      AMap = loadedAMap;
      const initialCenter = hasValidInitialView()
        ? props.initialView.center
        : [116.397428, 39.90923];
      const initialZoom = hasValidInitialView()
        ? props.initialView.zoom
        : 13;
      map = new AMap.Map("amap", {
        zoom: initialZoom,
        center: initialCenter,
      });
      map.addControl(new AMap.Scale());
      map.on('moveend', emitCurrentView);
      map.on('zoomend', emitCurrentView);
      mapReady.value = true;
      initSearch();
      renderDiaryMarkers();
    })
    .catch(console.error);
};

const initSearch = () => {
  placeSearch = new AMap.PlaceSearch({
    pageSize: 10, city: "全国", citylimit: false, panel: false
  });
  autoComplete = new AMap.AutoComplete({
    city: "", citylimit: false, datatype: 'poi'
  });
};

const handleKeywordInput = () => {
  const keyword = searchKeyword.value.trim();
  if (!keyword) {
    searchResults.value = [];
    return;
  }
  if (autocompleteTimer) clearTimeout(autocompleteTimer);
  autocompleteTimer = setTimeout(() => {
    handleAutocomplete(keyword);
  }, 220);
};

const handleSearchBlur = () => {
  setTimeout(() => {
    if (isSelectingSuggestion) return;
    const section = searchSectionRef.value;
    const activeElement = document.activeElement;
    if (!section || !(activeElement instanceof Node)) {
      clearSearchMarkers();
      return;
    }
    if (!section.contains(activeElement)) {
      clearSearchMarkers();
    }
  }, 100);
};

const handleDocumentClick = (event) => {
  if (isSelectingSuggestion) return;
  const section = searchSectionRef.value;
  if (!section) return;
  const target = event.target;
  if (target instanceof Node && section.contains(target)) return;
  clearSearchMarkers();
};

const beginSuggestionSelection = () => {
  isSelectingSuggestion = true;
  if (suggestionSelectionTimer) clearTimeout(suggestionSelectionTimer);
};

const endSuggestionSelection = () => {
  if (suggestionSelectionTimer) clearTimeout(suggestionSelectionTimer);
  suggestionSelectionTimer = setTimeout(() => {
    isSelectingSuggestion = false;
    suggestionSelectionTimer = null;
  }, 180);
};

const handleAutocomplete = (keyword) => {
  if (!autoComplete || !keyword) return;
  autoComplete.search(keyword, (status, result) => {
    if (status !== 'complete' || !result?.tips?.length) {
      handleSuggestionFallback(keyword);
      return;
    }
    const tips = result.tips
      .filter(tip => tip?.name)
      .map(tip => ({
        id: tip.id || tip.uid || `${tip.name}-${tip.address || ''}`,
        name: tip.name,
        address: [tip.district, tip.address].filter(Boolean).join(' '),
        location: normalizeLocation(tip.location),
        tel: '',
        type: tip.type || '',
        typecode: tip.typecode || '',
        description: getPlaceDescription(tip),
        images: normalizeImages(tip.photos || tip.images),
        isTip: true,
      }));
    if (tips.length === 0) {
      handleSuggestionFallback(keyword);
      return;
    }
    searchResults.value = tips;
  });
};

const handleSuggestionFallback = (keyword) => {
  if (!placeSearch || !keyword) {
    searchResults.value = [];
    return;
  }
  placeSearch.search(keyword, (status, result) => {
    if (status !== 'complete' || !result?.poiList?.pois?.length) {
      searchResults.value = [];
      return;
    }
    searchResults.value = result.poiList.pois.slice(0, 8).map(poi => ({
      id: poi.id,
      name: poi.name,
      address: poi.address || '',
      location: normalizeLocation(poi.location),
      tel: poi.tel || '',
      type: poi.type || '',
      typecode: poi.typecode || '',
      description: getPlaceDescription(poi),
      images: normalizeImages(poi.photos || poi.images)
    }));
  });
};

const normalizeLocation = (location) => {
  if (!location) return null;
  if (typeof location.lng === 'number' && typeof location.lat === 'number') {
    return { lng: location.lng, lat: location.lat };
  }
  if (typeof location.getLng === 'function' && typeof location.getLat === 'function') {
    return { lng: location.getLng(), lat: location.getLat() };
  }
  return null;
};

const normalizeImages = (images) => {
  if (!Array.isArray(images)) return [];
  const urls = images.map((item) => {
    if (typeof item === 'string') return item;
    if (!item || typeof item !== 'object') return '';
    return item.url || item.image || item.img || '';
  }).filter((url) => typeof url === 'string' && /^https?:\/\//i.test(url.trim()));
  return [...new Set(urls.map((url) => url.trim()))].slice(0, 6);
};

const getPlaceDescription = (place) => {
  const candidates = [
    place?.description,
    place?.intro,
    place?.detail,
    place?.businessArea,
    place?.adname,
  ];
  const text = candidates.find((item) => typeof item === 'string' && item.trim());
  return text ? text.trim() : '';
};

const handleSearch = () => {
  if (!searchKeyword.value.trim()) return;
  placeSearch.search(searchKeyword.value, (status, result) => {
    if (status === 'complete') onSearchComplete(result);
  });
};

const onSearchComplete = (result) => {
  clearSearchMarkers();
  searchResults.value = [];
  if (result.poiList?.pois) {
    searchResults.value = result.poiList.pois.map(poi => ({
      id: poi.id, name: poi.name, address: poi.address,
      location: poi.location, tel: poi.tel,
      type: poi.type, typecode: poi.typecode,
      description: getPlaceDescription(poi),
      images: normalizeImages(poi.photos || poi.images)
    }));
    addSearchMarkers(searchResults.value);
  }
};

const selectSearchResult = (result) => {
  beginSuggestionSelection();
  searchKeyword.value = result.name || searchKeyword.value;
  if (result.location) {
    clearSearchMarkers();
    addSearchMarkers([result]);
    map.setCenter([result.location.lng, result.location.lat]);
    map.setZoom(16);
    showMarkerInfo(result);
    searchResults.value = [];
    endSuggestionSelection();
    return;
  }
  handleSearch();
  endSuggestionSelection();
};

const getPlacesByDay = (day) => {
  return routePlaces.value
    .filter((place) => Number(place.routeDay) === Number(day))
    .sort((a, b) => {
      const orderA = Number.isFinite(Number(a.routeOrder)) ? Number(a.routeOrder) : 0;
      const orderB = Number.isFinite(Number(b.routeOrder)) ? Number(b.routeOrder) : 0;
      return orderA - orderB;
    });
};

const buildOrderedRoutePayload = (nextPlaces) => {
  const updates = [];
  displayDays.value.forEach((day) => {
    const dayPlaces = nextPlaces
      .filter((place) => Number(place.routeDay) === day)
      .sort((a, b) => Number(a.routeOrder) - Number(b.routeOrder));
    dayPlaces.forEach((place, orderIndex) => {
      updates.push({ placeId: place.id, routeDay: day, routeOrder: orderIndex });
    });
  });
  return updates;
};

const commitRouteChanges = (nextPlaces) => {
  localPlaces.value = normalizeRoutePlaces(nextPlaces);
  _emit('update-route-plan', { items: buildOrderedRoutePayload(localPlaces.value) });
};

const onPlaceDragStart = (placeId) => {
  draggingPlaceId.value = placeId;
};

const onPlaceDragEnd = () => {
  draggingPlaceId.value = null;
  dragOverDay.value = null;
};

const onDayDragOver = (day) => {
  dragOverDay.value = day;
};

const onDayDrop = (targetDay) => {
  if (!draggingPlaceId.value) return;
  const draggedPlace = localPlaces.value.find((place) => place.id === draggingPlaceId.value);
  if (!draggedPlace) return;

  const sameDayPlaces = getPlacesByDay(targetDay);
  const nextOrder = sameDayPlaces.length;
  const nextPlaces = localPlaces.value.map((place) => {
    if (place.id !== draggedPlace.id) return place;
    return {
      ...place,
      routeDay: targetDay,
      routeOrder: nextOrder
    };
  });
  commitRouteChanges(nextPlaces);
  onPlaceDragEnd();
};

const onPlaceDragOver = (day) => {
  dragOverDay.value = day;
};

const onPlaceDrop = (targetDay, targetPlaceId) => {
  if (!draggingPlaceId.value) return;
  if (draggingPlaceId.value === targetPlaceId) return;

  const draggedPlace = localPlaces.value.find((place) => place.id === draggingPlaceId.value);
  if (!draggedPlace) return;

  const baseList = localPlaces.value.filter((place) => place.id !== draggedPlace.id);
  const targetDayPlaces = baseList
    .filter((place) => Number(place.routeDay) === Number(targetDay))
    .sort((a, b) => Number(a.routeOrder) - Number(b.routeOrder));
  const insertIndex = targetDayPlaces.findIndex((place) => place.id === targetPlaceId);
  const insertAt = insertIndex >= 0 ? insertIndex : targetDayPlaces.length;
  targetDayPlaces.splice(insertAt, 0, { ...draggedPlace, routeDay: targetDay });

  const rebuilt = baseList.map((place) => ({ ...place }));
  targetDayPlaces.forEach((place, index) => {
    const target = rebuilt.find((item) => item.id === place.id);
    if (!target) {
      rebuilt.push({ ...place, routeOrder: index });
      return;
    }
    target.routeDay = targetDay;
    target.routeOrder = index;
  });

  commitRouteChanges(rebuilt);
  onPlaceDragEnd();
};

const addRouteDay = () => {
  manualDayCount.value = Math.max(manualDayCount.value + 1, displayDays.value.length + 1);
};

const addSearchMarkers = (places) => {
  places.forEach(place => {
    if (!place.location) return;
    const marker = new AMap.Marker({
      position: [place.location.lng, place.location.lat],
      title: place.name,
      content: createMarkerContent(place.typecode, false, null),
      offset: new AMap.Pixel(-15, -38)
    });
    marker.setMap(map);
    marker.on('click', () => showMarkerInfo(place));
    searchMarkers.push(marker);
  });
};

// 高德 POI typecode 前两位对应大类，使用 xicons 组件
const iconComponents = {
  '05': RestaurantIcon, // 餐饮
  '06': CartIcon,       // 购物
  '10': BedIcon,        // 住宿
  '11': LeafIcon,       // 风景名胜
  '15': BusIcon,        // 交通
};
const defaultIconComponent = LocationIcon;

// 每个类别对应的颜色
const typeColors = {
  '05': '#f97316', // 餐饮 - 橙色
  '06': '#a855f7', // 购物 - 紫色
  '10': '#3b82f6', // 住宿 - 蓝色
  '11': '#2ecc71', // 风景 - 绿色
  '15': '#64748b', // 交通 - 灰蓝
};
const defaultDiaryColor = '#ef4444'; // 默认 - 红色

const getColorByTypecode = (typecode) => {
  if (!typecode) return defaultDiaryColor;
  const prefix = typecode.substring(0, 2);
  return typeColors[prefix] || defaultDiaryColor;
};

const getIconByTypecode = (typecode) => {
  const prefix = typecode ? typecode.substring(0, 2) : '';
  const comp = iconComponents[prefix] || defaultIconComponent;
  return renderIconSvgContent(comp);
};

const createMarkerContent = (typecode, isDiary, name) => {
  const color = isDiary ? getColorByTypecode(typecode) : '#3b82f6';
  const iconSvg = getIconByTypecode(typecode);

  const wrapper = document.createElement('div');
  wrapper.style.cssText = 'display:flex;flex-direction:column;align-items:center;cursor:pointer;';

  // Pin body
  const pin = document.createElement('div');
  pin.style.cssText = `width:30px;height:30px;border-radius:50% 50% 50% 0;background:${color};transform:rotate(-45deg);display:flex;align-items:center;justify-content:center;box-shadow:0 2px 8px rgba(0,0,0,0.25);border:2px solid #fff;`;

  const iconContainer = document.createElement('div');
  iconContainer.style.cssText = 'transform:rotate(45deg);display:flex;align-items:center;justify-content:center;';
  iconContainer.innerHTML = `<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 512 512" style="color:#fff">${iconSvg}</svg>`;

  pin.appendChild(iconContainer);
  wrapper.appendChild(pin);

  // Pin tail
  const tail = document.createElement('div');
  tail.style.cssText = `width:2px;height:6px;background:${color};margin-top:-1px;`;
  wrapper.appendChild(tail);

  // Name label for diary markers
  if (isDiary && name) {
    const label = document.createElement('div');
    label.style.cssText = 'margin-top:2px;padding:1px 6px;background:rgba(255,255,255,0.92);border-radius:3px;font-size:11px;color:#333;white-space:nowrap;max-width:80px;overflow:hidden;text-overflow:ellipsis;box-shadow:0 1px 3px rgba(0,0,0,0.15);line-height:1.4;';
    label.textContent = name;
    wrapper.appendChild(label);
  }

  return wrapper;
};

const showMarkerInfo = (place) => {
  selectedMarker.value = place;
  isEditingDescription.value = false;
  descriptionDraft.value = place?.description || '';
};

const closeMarkerInfo = () => {
  selectedMarker.value = null;
  isEditingDescription.value = false;
  descriptionDraft.value = '';
};

const startDescriptionEdit = () => {
  descriptionDraft.value = selectedMarker.value?.description || '';
  isEditingDescription.value = true;
};

const cancelDescriptionEdit = () => {
  descriptionDraft.value = selectedMarker.value?.description || '';
  isEditingDescription.value = false;
};

const saveDescriptionEdit = () => {
  const marker = selectedMarker.value;
  const placeId = getPlaceDbId(marker);
  if (!marker || !placeId) return;
  const description = descriptionDraft.value.trim();
  selectedMarker.value = { ...marker, description };
  isEditingDescription.value = false;
  _emit('update-place-description', { placeId, description });
};

const toggleSidebar = () => {
  sidebarOpen.value = !sidebarOpen.value;
};

const clearSearchMarkers = () => {
  searchMarkers.forEach(m => m.setMap(null));
  searchMarkers.length = 0;
};

const clearDiaryMarkers = () => {
  diaryMarkers.forEach(m => m.setMap(null));
  diaryMarkers.length = 0;
};

const renderDiaryMarkers = () => {
  if (!AMap || !map) return;
  clearDiaryMarkers();
  routePlaces.value.forEach(place => {
    if (!Number.isFinite(place.lng) || !Number.isFinite(place.lat)) return;
    const marker = new AMap.Marker({
      position: [place.lng, place.lat],
      title: place.name,
      content: createMarkerContent(place.typecode, true, place.name),
      offset: new AMap.Pixel(-15, -38)
    });
    marker.setMap(map);
    marker.on('click', () => goToPlace(place));
    diaryMarkers.push(marker);
  });
};

const goToPlace = (place) => {
  if (place.lng && place.lat) {
    map.setCenter([place.lng, place.lat]);
    map.setZoom(16);
    showMarkerInfo({
      id: place.poi_id, name: place.name, address: place.address,
      location: { lng: place.lng, lat: place.lat },
      tel: place.tel, type: place.type, typecode: place.typecode,
      description: place.description || '',
      images: Array.isArray(place.images) ? place.images : []
    });
  }
};

const isPlaceInDiary = (marker) => {
  if (!marker) return false;
  return routePlaces.value.some(p => p.poi_id === marker.id);
};

const getPlaceDbId = (marker) => {
  const found = routePlaces.value.find(p => p.poi_id === marker.id);
  return found ? found.id : null;
};

const getPlaceTypecode = (marker) => {
  const found = routePlaces.value.find(p => p.poi_id === marker.id);
  return found ? found.typecode : '';
};

const markerTypeOptions = [
  { code: '', label: '默认', color: defaultDiaryColor, icon: defaultIconComponent },
  { code: '05', label: '餐饮', color: typeColors['05'], icon: iconComponents['05'] },
  { code: '06', label: '购物', color: typeColors['06'], icon: iconComponents['06'] },
  { code: '10', label: '住宿', color: typeColors['10'], icon: iconComponents['10'] },
  { code: '11', label: '风景', color: typeColors['11'], icon: iconComponents['11'] },
  { code: '15', label: '交通', color: typeColors['15'], icon: iconComponents['15'] },
];

watch(() => props.places, (nextPlaces) => {
  localPlaces.value = normalizeRoutePlaces(nextPlaces);
  manualDayCount.value = Math.max(parseDiaryTripDays(props.diaryTripTime), maxAssignedDay.value, 1);
}, { deep: true, immediate: true });

watch(() => props.diaryTripTime, () => {
  manualDayCount.value = Math.max(manualDayCount.value, parseDiaryTripDays(props.diaryTripTime), maxAssignedDay.value, 1);
});

watch([routePlaces, mapReady], () => {
  if (mapReady.value) renderDiaryMarkers();
}, { deep: true });

watch(() => props.initialView, () => {
  if (!mapReady.value) return;
  applyInitialView();
}, { deep: true });

onUnmounted(() => {
  if (autocompleteTimer) clearTimeout(autocompleteTimer);
  if (suggestionSelectionTimer) clearTimeout(suggestionSelectionTimer);
  document.removeEventListener('click', handleDocumentClick);
  if (map) {
    emitCurrentView();
    map.off('moveend', emitCurrentView);
    map.off('zoomend', emitCurrentView);
    map.destroy();
    map = null;
  }
});
</script>

<style scoped>
.map-container {
  width: 100%;
  height: 100%;
  position: relative;
  color: var(--color-text);
}

#amap {
  width: 100%;
  height: 100%;
}

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

.sidebar-content::-webkit-scrollbar { width: 6px; }
.sidebar-content::-webkit-scrollbar-track { background: transparent; }
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

.sidebar-section-title.clickable { cursor: pointer; }

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

.search-box input:focus { border-color: var(--color-primary); }

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

.search-result-item:hover { background: var(--color-light-light); }

.result-name { font-size: 14px; font-weight: 500; color: var(--color-text); }
.result-address { font-size: 12px; color: var(--color-text-sub-sub); margin-top: 2px; }

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

.favorite-name { font-size: 14px; color: var(--color-text); }
.favorite-address { font-size: 12px; color: var(--color-text-sub-sub); margin-top: 2px; }
.no-favorites { text-align: center; color: var(--color-text-sub-sub); padding: 20px 0; font-size: 13px; }

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

.remove-favorite:hover { opacity: 1; }

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

.sidebar-toggle-btn.sidebar-open { opacity: 0; pointer-events: none; }

.marker-info-panel {
  position: absolute;
  top: 70px;
  right: 20px;
  width: 320px;
  background: color-mix(in srgb, var(--color-background-soft) 95%, transparent);
  backdrop-filter: blur(10px);
  border-radius: 12px;
  box-shadow: 0 4px 15px var(--color-shadow);
  border: 1px solid var(--color-border);
  z-index: 100;
  overflow: hidden;
}

.marker-info-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px;
  border-bottom: 1px solid var(--color-border);
}

.marker-info-header h3 { margin: 0; font-size: 16px; color: var(--color-text); }

.close-btn {
  background: none;
  border: none;
  font-size: 20px;
  cursor: pointer;
  color: var(--color-text-sub-sub);
}

.marker-info-content { padding: 16px; }
.marker-info-content p { margin: 6px 0; font-size: 13px; color: var(--color-text-sub); }

.marker-actions { margin-top: 12px; display: flex; gap: 8px; }

.action-btn {
  flex: 1;
  padding: 8px 12px;
  border: 1px solid var(--color-border);
  border-radius: 6px;
  background: var(--color-background-soft);
  color: var(--color-text);
  cursor: pointer;
  font-size: 13px;
  transition: all 0.2s;
}

.action-btn:hover { background: var(--color-light-light); }
.action-btn.active { background: var(--color-primary); color: var(--color-background); border-color: var(--color-primary); }

.marker-type-section { margin-top: 10px; }
.marker-type-label { margin-bottom: 6px !important; }

.marker-type-options {
  display: flex;
  gap: 6px;
  flex-wrap: wrap;
}

.marker-type-btn {
  --hover-color: #888;
  width: 34px;
  height: 34px;
  border-radius: 8px;
  border: 2px solid var(--color-border);
  background: var(--color-background-soft);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--color-text-sub-sub);
  transition: all 0.2s;
}

.marker-type-btn:hover {
  border-color: var(--hover-color);
  color: var(--hover-color);
}

.marker-type-btn.active {
  color: #fff;
}

.marker-type-icon {
  width: 18px;
  height: 18px;
}

.marker-image-section {
  margin-top: 10px;
}

.marker-image-label {
  margin-bottom: 6px !important;
}

.marker-image-list {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 6px;
}

.marker-image-link {
  display: block;
  border-radius: 8px;
  overflow: hidden;
  background: var(--color-background);
  border: 1px solid var(--color-border);
  aspect-ratio: 1 / 1;
}

.marker-image-link img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
}

.marker-description-section {
  margin-top: 10px;
}

.marker-description-empty {
  color: var(--color-text-sub-sub) !important;
}

.marker-description-editable {
  cursor: pointer;
  text-decoration: underline;
  text-decoration-style: dashed;
  text-underline-offset: 3px;
  text-decoration-color: color-mix(in srgb, var(--color-text-sub-sub) 45%, transparent);
  transition: color 0.2s ease, text-decoration-color 0.2s ease;
}

.marker-description-editable:hover {
  text-decoration-color: color-mix(in srgb, var(--color-primary) 90%, transparent);
  color: var(--color-primary) !important;
}

.marker-description-editor {
  margin-top: 8px;
}

.marker-description-input {
  width: 100%;
  resize: vertical;
  min-height: 70px;
  border: 1px solid var(--color-border);
  border-radius: 8px;
  padding: 8px 10px;
  font-size: 13px;
  color: var(--color-text);
  background: var(--color-background-soft);
  outline: none;
  box-sizing: border-box;
}

.marker-description-input:focus {
  border-color: var(--color-primary);
}

.marker-description-count {
  margin-top: 6px;
  font-size: 11px;
  color: var(--color-text-sub-sub);
  text-align: right;
}

.marker-description-actions {
  margin-top: 8px;
  display: flex;
  justify-content: flex-end;
  gap: 8px;
}

.marker-description-btn {
  border: 1px solid var(--color-border);
  background: var(--color-background-soft);
  color: var(--color-text-sub);
  border-radius: 6px;
  padding: 4px 10px;
  font-size: 12px;
  cursor: pointer;
}

.marker-description-btn.primary {
  border-color: var(--color-primary);
  background: var(--color-primary);
  color: var(--color-background);
}

.marker-description-btn.subtle {
  background: var(--color-background);
}

@media (max-width: 768px) {
  .sidebar {
    width: calc(100% - 32px);
    left: 16px;
  }
  .sidebar-toggle-btn { left: 16px; }
  .marker-info-panel {
    width: calc(100% - 40px);
    left: 20px; right: 20px; top: auto; bottom: 20px;
  }
}

.search-results::-webkit-scrollbar,
.favorites-list::-webkit-scrollbar { width: 6px; }
.search-results::-webkit-scrollbar-track,
.favorites-list::-webkit-scrollbar-track { background: var(--color-background); border-radius: 3px; }
.search-results::-webkit-scrollbar-thumb,
.favorites-list::-webkit-scrollbar-thumb { background: color-mix(in srgb, var(--color-text-sub-sub) 80%, transparent); border-radius: 3px; }
.search-results::-webkit-scrollbar-thumb:hover,
.favorites-list::-webkit-scrollbar-thumb:hover { background: color-mix(in srgb, var(--color-text-sub) 80%, transparent); }
</style>

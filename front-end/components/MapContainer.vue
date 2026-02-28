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
          <span class="sidebar-diary-name">{{ diaryName }}</span>
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
          <div v-if="showPlaces" class="favorites-list">
            <div
              v-for="place in places"
              :key="place.id"
              class="favorite-item"
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
import { ref, onMounted, onUnmounted, watch, createVNode, render as vueRender } from "vue";
import AMapLoader from "@amap/amap-jsapi-loader";
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
  diaryName: { type: String, default: '' }
})
const _emit = defineEmits(['add-place', 'remove-place', 'update-place-type', 'back'])

const searchKeyword = ref('');
const searchResults = ref([]);
const selectedMarker = ref(null);
const showPlaces = ref(true);
const sidebarOpen = ref(true);
const searchSectionRef = ref(null);

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

onMounted(() => {
  initMap();
  document.addEventListener('click', handleDocumentClick);
});

const initMap = () => {
  window._AMapSecurityConfig = {
    securityJsCode: "467acecf4320cdce83d519705e1aad3b", // TODO - 生产环境请替换为正式的安全码
  };
  AMapLoader.load({
    key: "3fbe22db53162479e06074420635fba4",
    version: "2.0",
    plugins: ['AMap.Scale', 'AMap.PlaceSearch', 'AMap.AutoComplete'],
  })
    .then((loadedAMap) => {
      AMap = loadedAMap;
      map = new AMap.Map("amap", {
        zoom: 13,
        center: [116.397428, 39.90923],
      });
      map.addControl(new AMap.Scale());
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
      typecode: poi.typecode || ''
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
      type: poi.type, typecode: poi.typecode
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
};

const closeMarkerInfo = () => {
  selectedMarker.value = null;
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
  props.places.forEach(place => {
    if (!place.lng || !place.lat) return;
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
      tel: place.tel, type: place.type, typecode: place.typecode
    });
  }
};

const isPlaceInDiary = (marker) => {
  if (!marker) return false;
  return props.places.some(p => p.poi_id === marker.id);
};

const getPlaceDbId = (marker) => {
  const found = props.places.find(p => p.poi_id === marker.id);
  return found ? found.id : null;
};

const getPlaceTypecode = (marker) => {
  const found = props.places.find(p => p.poi_id === marker.id);
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

watch([() => props.places, mapReady], () => {
  if (mapReady.value) renderDiaryMarkers();
}, { deep: true });

onUnmounted(() => {
  if (autocompleteTimer) clearTimeout(autocompleteTimer);
  if (suggestionSelectionTimer) clearTimeout(suggestionSelectionTimer);
  document.removeEventListener('click', handleDocumentClick);
  if (map) { map.destroy(); map = null; }
});
</script>

<style scoped>
.map-container {
  width: 100%;
  height: 100%;
  position: relative;
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
  background: rgba(255, 255, 255, 0.92);
  backdrop-filter: blur(12px);
  border: 1px solid rgba(255, 255, 255, 0.55);
  box-shadow: 0 10px 28px rgba(0, 0, 0, 0.14);
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
  background: rgba(0, 0, 0, 0.16);
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
  background: rgba(255, 255, 255, 0.92);
  backdrop-filter: blur(8px);
  border-bottom: 1px solid #ececec;
}

.back-btn {
  background: none;
  border: none;
  cursor: pointer;
  display: flex;
  align-items: center;
  color: #666;
  padding: 4px;
  border-radius: 6px;
  transition: background 0.2s, color 0.2s;
  flex-shrink: 0;
}

.back-btn:hover {
  background: #f0f0f0;
  color: #333;
}

.sidebar-diary-name {
  flex: 1;
  font-size: 15px;
  font-weight: 500;
  color: #333;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.sidebar-close-btn {
  background: none;
  border: none;
  font-size: 18px;
  color: #999;
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

.sidebar-close-btn:hover {
  background: #f0f0f0;
  color: #333;
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
  color: #333;
}

.sidebar-section-title.clickable { cursor: pointer; }

.favorites-toggle {
  font-size: 12px;
  color: #999;
}

.sidebar-divider {
  height: 1px;
  background: #efefef;
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
  border: 1px solid #ddd;
  border-radius: 6px;
  font-size: 14px;
  outline: none;
}

.search-box input:focus { border-color: #2ecc71; }

.search-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 8px 12px;
  border: none;
  border-radius: 6px;
  background: #2ecc71;
  color: white;
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
  border-bottom: 1px solid #f0f0f0;
  cursor: pointer;
  transition: background 0.2s;
}

.search-result-item:hover { background: #f9f9f9; }

.result-name { font-size: 14px; font-weight: 500; color: #333; }
.result-address { font-size: 12px; color: #999; margin-top: 2px; }

.favorites-list {
  max-height: 300px;
  overflow-y: auto;
  margin: 0 -16px;
  padding: 0 16px;
}

.favorite-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px;
  border-bottom: 1px solid #f0f0f0;
  cursor: pointer;
  transition: background 0.2s;
}

.favorite-item:hover { background: #f9f9f9; }
.favorite-name { font-size: 14px; color: #333; }
.favorite-address { font-size: 12px; color: #999; margin-top: 2px; }
.no-favorites { text-align: center; color: #999; padding: 20px 0; font-size: 13px; }

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
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
  border: none;
  width: 36px;
  height: 36px;
  border-radius: 10px;
  cursor: pointer;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  font-size: 14px;
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
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
  border-radius: 12px;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
  z-index: 100;
  overflow: hidden;
}

.marker-info-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px;
  border-bottom: 1px solid #eee;
}

.marker-info-header h3 { margin: 0; font-size: 16px; color: #333; }

.close-btn {
  background: none;
  border: none;
  font-size: 20px;
  cursor: pointer;
  color: #999;
}

.marker-info-content { padding: 16px; }
.marker-info-content p { margin: 6px 0; font-size: 13px; color: #666; }

.marker-actions { margin-top: 12px; display: flex; gap: 8px; }

.action-btn {
  flex: 1;
  padding: 8px 12px;
  border: 1px solid #ddd;
  border-radius: 6px;
  background: white;
  cursor: pointer;
  font-size: 13px;
  transition: all 0.2s;
}

.action-btn:hover { background: #f9f9f9; }
.action-btn.active { background: #2ecc71; color: white; border-color: #2ecc71; }

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
  border: 2px solid #e0e0e0;
  background: #fff;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #888;
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
.favorites-list::-webkit-scrollbar-track { background: #f1f1f1; border-radius: 3px; }
.search-results::-webkit-scrollbar-thumb,
.favorites-list::-webkit-scrollbar-thumb { background: #c1c1c1; border-radius: 3px; }
.search-results::-webkit-scrollbar-thumb:hover,
.favorites-list::-webkit-scrollbar-thumb:hover { background: #a8a8a8; }
</style>

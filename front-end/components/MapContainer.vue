<template>
  <div class="map-container">
    <div id="amap"/>
    
    <div class="search-panel">
      <div class="search-box">
        <input
          id="search_input"
          v-model="searchKeyword"
          type="text"
          placeholder="搜索地点、景点、餐厅..."
          @keyup.enter="handleSearch"
        />
        <button class="search-btn" @click="handleSearch">🔍</button>
      </div>
      
      <div v-if="searchResults.length > 0" class="search-results">
        <div 
          v-for="(result, index) in searchResults" 
          :key="index"
          class="search-result-item"
          @click="selectSearchResult(result)"
        >
          <div class="result-name">{{ result.name }}</div>
          <div class="result-address">{{ result.address }}</div>
        </div>
      </div>
    </div>

    <div v-if="selectedMarker" class="marker-info-panel">
      <div class="marker-info-header">
        <h3>{{ selectedMarker.name }}</h3>
        <button class="close-btn" @click="closeMarkerInfo">×</button>
      </div>
      <div class="marker-info-content">
        <p><strong>地址:</strong> {{ selectedMarker.address }}</p>
        <p v-if="selectedMarker.tel"><strong>电话:</strong> {{ selectedMarker.tel }}</p>
        <p v-if="selectedMarker.type"><strong>类型:</strong> {{ selectedMarker.type }}</p>
        <div class="marker-actions">
          <button 
            class="action-btn favorite-btn"
            :class="{ active: selectedMarker.isFavorite }"
            @click="toggleFavorite"
          >
            {{ selectedMarker.isFavorite ? '❤️ 已收藏' : '🤍 收藏' }}
          </button>
          <button class="action-btn note-btn" @click="addNote">
            📝 添加笔记
          </button>
        </div>
        <div v-if="selectedMarker.note" class="marker-note">
          <strong>笔记:</strong>
          <p>{{ selectedMarker.note }}</p>
        </div>
      </div>
    </div>

    <div class="favorites-panel" :class="{ open: showFavorites }">
      <div class="favorites-header" @click="toggleFavorites">
        <h3>我的收藏</h3>
        <button class="toggle-btn">{{ showFavorites ? '收起' : '展开' }}</button>
      </div>
      <div v-if="showFavorites" class="favorites-list">
        <div 
          v-for="favorite in favorites" 
          :key="favorite.id"
          class="favorite-item"
          @click="goToFavorite(favorite)"
        >
          <div class="favorite-name">{{ favorite.name }}</div>
          <div class="favorite-address">{{ favorite.address }}</div>
          <button class="remove-favorite" @click.stop="removeFavorite(favorite.id)">🗑️</button>
        </div>
        <div v-if="favorites.length === 0" class="no-favorites">暂无收藏地点</div>
      </div>
    </div>

    <div v-if="showNoteModal" class="note-modal-overlay" @click="closeNoteModal">
      <div class="note-modal" @click.stop>
        <h3>添加笔记</h3>
        <textarea 
          v-model="noteText" 
          placeholder="在这里记录你的想法..."
          rows="4"
        ></textarea>
        <div class="note-modal-actions">
          <button class="cancel-btn" @click="closeNoteModal">取消</button>
          <button class="save-btn" @click="saveNote">保存</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from "vue";
import AMapLoader from "@amap/amap-jsapi-loader";

const searchKeyword = ref('');
const searchResults = ref([]);
const selectedMarker = ref(null);
const showFavorites = ref(false);
const favorites = ref([]);
const showNoteModal = ref(false);
const noteText = ref('');

let map = null;
let AMap = null;
let placeSearch = null;
let autocomplete = null;
let markers = [];

onMounted(() => {
  initMap();
  loadFavorites();
});

const initMap = () => {
  window._AMapSecurityConfig = {
    securityJsCode: "467acecf4320cdce83d519705e1aad3b",
  };

  AMapLoader.load({
    key: "3fbe22db53162479e06074420635fba4",
    version: "2.0",
    plugins: ['AMap.Scale', 'AMap.PlaceSearch', 'AMap.Autocomplete'],
  })
    .then((loadedAMap) => {
      AMap = loadedAMap;
      
      map = new AMap.Map("amap", {
        zoom: 13,
        center: [116.397428, 39.90923],
      });

      map.addControl(new AMap.Scale());
      initSearch();
      map.on('click', onMapClick);
    })
    .catch(console.error);
};

const initSearch = () => {
  placeSearch = new AMap.PlaceSearch({
    pageSize: 10,
    city: "全国",
    map: map,
    panel: false
  });

  autocomplete = new AMap.Autocomplete({
    input: "search_input",
    city: "全国"
  });

  placeSearch.on('complete', onSearchComplete);
  autocomplete.on('select', (e) => {
    searchKeyword.value = e.poi.name;
    handleSearch();
  });
};

const handleSearch = () => {
  if (!searchKeyword.value.trim()) return;
  placeSearch.search(searchKeyword.value, (status, result) => {
    if (status === 'complete') onSearchComplete(result);
  });
};

const onSearchComplete = (result) => {
  clearMarkers();
  searchResults.value = [];
  
  if (result.poiList?.pois) {
    searchResults.value = result.poiList.pois.map(poi => ({
      id: poi.id,
      name: poi.name,
      address: poi.address,
      location: poi.location,
      tel: poi.tel,
      type: poi.type,
      typecode: poi.typecode
    }));
    addMarkersToMap(searchResults.value);
  }
};

const selectSearchResult = (result) => {
  if (result.location) {
    map.setCenter([result.location.lng, result.location.lat]);
    map.setZoom(16);
    showMarkerInfo(result);
  }
  searchResults.value = [];
};

// 添加标记到地图
const addMarkersToMap = (places) => {
  places.forEach(place => {
    if (place.location) {
      const marker = new AMap.Marker({
        position: [place.location.lng, place.location.lat],
        title: place.name,
        icon: getMarkerIcon(place.typecode)
      });

      marker.setMap(map);
      marker.place = place;
      
      // 标记点击事件
      marker.on('click', () => {
        showMarkerInfo(place);
      });

      markers.push(marker);
    }
  });
};

// 获取标记图标
const getMarkerIcon = (typecode) => {
  // 根据类型码返回不同图标
  const iconMap = {
    '060000': '🏛️', // 景点
    '050000': '🍽️', // 餐饮
    '100000': '🏨', // 住宿
    '060100': '🛍️', // 购物
    '150000': '🚇'  // 交通
  };
  
  const icon = iconMap[typecode] || '📍';
  
  return new AMap.Icon({
    size: new AMap.Size(32, 32),
    image: `data:image/svg+xml;charset=utf-8,${encodeURIComponent(`
      <svg xmlns="http://www.w3.org/2000/svg" width="32" height="32" viewBox="0 0 32 32">
        <circle cx="16" cy="16" r="12" fill="#ff4757" stroke="#fff" stroke-width="2"/>
        <text x="16" y="20" text-anchor="middle" font-size="12">${icon}</text>
      </svg>
    `)}`
  });
};

// 显示标记信息
const showMarkerInfo = (place) => {
  const favorite = favorites.value.find(f => f.id === place.id);
  selectedMarker.value = {
    ...place,
    isFavorite: !!favorite,
    note: favorite?.note || ''
  };
};

// 关闭标记信息
const closeMarkerInfo = () => {
  selectedMarker.value = null;
};

// 切换收藏状态
const toggleFavorite = () => {
  if (!selectedMarker.value) return;
  
  const marker = selectedMarker.value;
  const existingIndex = favorites.value.findIndex(f => f.id === marker.id);
  
  if (existingIndex >= 0) {
    // 取消收藏
    favorites.value.splice(existingIndex, 1);
    marker.isFavorite = false;
  } else {
    // 添加收藏
    const favorite = {
      id: marker.id,
      name: marker.name,
      address: marker.address,
      location: marker.location,
      tel: marker.tel,
      type: marker.type,
      note: marker.note || '',
      createdAt: new Date().toISOString()
    };
    favorites.value.push(favorite);
    marker.isFavorite = true;
  }
  
  saveFavorites();
};

// 添加笔记
const addNote = () => {
  noteText.value = selectedMarker.value?.note || '';
  showNoteModal.value = true;
};

// 保存笔记
const saveNote = () => {
  if (!selectedMarker.value) return;
  
  selectedMarker.value.note = noteText.value;
  
  // 更新收藏中的笔记
  const favoriteIndex = favorites.value.findIndex(f => f.id === selectedMarker.value.id);
  if (favoriteIndex >= 0) {
    favorites.value[favoriteIndex].note = noteText.value;
    saveFavorites();
  }
  
  closeNoteModal();
};

// 关闭笔记模态框
const closeNoteModal = () => {
  showNoteModal.value = false;
  noteText.value = '';
};

// 切换收藏面板
const toggleFavorites = () => {
  showFavorites.value = !showFavorites.value;
};

// 跳转到收藏地点
const goToFavorite = (favorite) => {
  if (favorite.location) {
    map.setCenter([favorite.location.lng, favorite.location.lat]);
    map.setZoom(16);
    showMarkerInfo(favorite);
  }
};

// 删除收藏
const removeFavorite = (id) => {
  const index = favorites.value.findIndex(f => f.id === id);
  if (index >= 0) {
    favorites.value.splice(index, 1);
    saveFavorites();
    
    // 更新当前选中标记的收藏状态
    if (selectedMarker.value && selectedMarker.value.id === id) {
      selectedMarker.value.isFavorite = false;
    }
  }
};


// 地图点击事件
const onMapClick = (e) => {
  // 可以在这里添加自定义标记功能
  console.log('地图点击位置:', e.lnglat);
};

// 清除所有标记
const clearMarkers = () => {
  markers.forEach(marker => {
    marker.setMap(null);
  });
  markers = [];
};

// 保存收藏到本地存储
const saveFavorites = () => {
  localStorage.setItem('travel_favorites', JSON.stringify(favorites.value));
};

// 从本地存储加载收藏
const loadFavorites = () => {
  const saved = localStorage.getItem('travel_favorites');
  if (saved) {
    try {
      favorites.value = JSON.parse(saved);
    } catch (e) {
      console.error('加载收藏失败:', e);
      favorites.value = [];
    }
  }
};

onUnmounted(() => {
  map?.destroy();
});
</script>

<style scoped>
.map-container {
  position: relative;
  width: 100%;
  height: 100vh;
  overflow: hidden;
}

#amap {
  width: 100%;
  height: 100%;
}

/* 搜索面板样式 */
.search-panel {
  position: absolute;
  top: 20px;
  left: 20px;
  width: 400px;
  z-index: 1000;
  background: rgba(255, 255, 255, 0.95);
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
  backdrop-filter: blur(10px);
}

.search-box {
  display: flex;
  padding: 12px;
  gap: 8px;
}

#search_input {
  flex: 1;
  padding: 12px 16px;
  border: 2px solid #e1e5e9;
  border-radius: 8px;
  font-size: 14px;
  outline: none;
  transition: all 0.3s ease;
}

#search_input:focus {
  border-color: #4285f4;
  box-shadow: 0 0 0 3px rgba(66, 133, 244, 0.1);
}

.search-btn {
  padding: 12px 16px;
  background: #4285f4;
  color: white;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s ease;
  font-size: 16px;
}

.search-btn:hover {
  background: #3367d6;
  transform: translateY(-1px);
}

/* 搜索结果样式 */
.search-results {
  max-height: 300px;
  overflow-y: auto;
  border-top: 1px solid #e1e5e9;
}

.search-result-item {
  padding: 12px 16px;
  cursor: pointer;
  border-bottom: 1px solid #f0f0f0;
  transition: background-color 0.2s ease;
}

.search-result-item:hover {
  background-color: #f8f9fa;
}

.search-result-item:last-child {
  border-bottom: none;
}

.result-name {
  font-weight: 600;
  color: #333;
  margin-bottom: 4px;
}

.result-address {
  font-size: 12px;
  color: #666;
}

/* 标记信息面板样式 */
.marker-info-panel {
  position: absolute;
  top: 20px;
  right: 20px;
  width: 320px;
  background: white;
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
  z-index: 1000;
  overflow: hidden;
}

.marker-info-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.marker-info-header h3 {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
}

.close-btn {
  background: none;
  border: none;
  color: white;
  font-size: 24px;
  cursor: pointer;
  padding: 0;
  width: 30px;
  height: 30px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: background-color 0.2s ease;
}

.close-btn:hover {
  background-color: rgba(255, 255, 255, 0.2);
}

.marker-info-content {
  padding: 20px;
}

.marker-info-content p {
  margin: 8px 0;
  color: #333;
  line-height: 1.5;
}

.marker-actions {
  display: flex;
  gap: 10px;
  margin: 16px 0;
}

.action-btn {
  flex: 1;
  padding: 10px 16px;
  border: 2px solid #e1e5e9;
  border-radius: 8px;
  background: white;
  cursor: pointer;
  font-size: 14px;
  transition: all 0.3s ease;
}

.action-btn:hover {
  transform: translateY(-1px);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.favorite-btn.active {
  background: #ff6b6b;
  border-color: #ff6b6b;
  color: white;
}

.note-btn {
  background: #4ecdc4;
  border-color: #4ecdc4;
  color: white;
}

.marker-note {
  margin-top: 16px;
  padding: 12px;
  background: #f8f9fa;
  border-radius: 8px;
  border-left: 4px solid #4285f4;
}

.marker-note p {
  margin: 4px 0 0 0;
  font-style: italic;
  color: #555;
}

/* 收藏面板样式 */
.favorites-panel {
  position: absolute;
  bottom: 20px;
  left: 20px;
  width: 300px;
  background: white;
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
  z-index: 1000;
  transition: all 0.3s ease;
  max-height: 60px;
  overflow: hidden;
}

.favorites-panel.open {
  max-height: 400px;
}

.favorites-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px;
  background: linear-gradient(135deg, #ffecd2 0%, #fcb69f 100%);
  cursor: pointer;
}

.favorites-header h3 {
  margin: 0;
  font-size: 16px;
  font-weight: 600;
  color: #333;
}

.toggle-btn {
  background: none;
  border: none;
  color: #666;
  font-size: 12px;
  cursor: pointer;
  padding: 4px 8px;
  border-radius: 4px;
  transition: background-color 0.2s ease;
}

.toggle-btn:hover {
  background-color: rgba(0, 0, 0, 0.1);
}

.favorites-list {
  max-height: 300px;
  overflow-y: auto;
}

.favorite-item {
  display: flex;
  align-items: center;
  padding: 12px 16px;
  border-bottom: 1px solid #f0f0f0;
  cursor: pointer;
  transition: background-color 0.2s ease;
}

.favorite-item:hover {
  background-color: #f8f9fa;
}

.favorite-item:last-child {
  border-bottom: none;
}

.favorite-name {
  font-weight: 600;
  color: #333;
  margin-bottom: 2px;
}

.favorite-address {
  font-size: 12px;
  color: #666;
  flex: 1;
}

.remove-favorite {
  background: none;
  border: none;
  cursor: pointer;
  padding: 4px;
  border-radius: 4px;
  transition: background-color 0.2s ease;
  margin-left: 8px;
}

.remove-favorite:hover {
  background-color: #ffebee;
}

.no-favorites {
  padding: 20px;
  text-align: center;
  color: #999;
  font-style: italic;
}


/* 笔记模态框样式 */
.note-modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 2000;
}

.note-modal {
  background: white;
  border-radius: 12px;
  padding: 24px;
  width: 90%;
  max-width: 500px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
}

.note-modal h3 {
  margin: 0 0 16px 0;
  font-size: 18px;
  font-weight: 600;
  color: #333;
}

.note-modal textarea {
  width: 100%;
  padding: 12px;
  border: 2px solid #e1e5e9;
  border-radius: 8px;
  font-size: 14px;
  font-family: inherit;
  resize: vertical;
  outline: none;
  transition: border-color 0.3s ease;
}

.note-modal textarea:focus {
  border-color: #4285f4;
}

.note-modal-actions {
  display: flex;
  gap: 12px;
  margin-top: 16px;
  justify-content: flex-end;
}

.cancel-btn, .save-btn {
  padding: 10px 20px;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 500;
  transition: all 0.3s ease;
}

.cancel-btn {
  background: #f5f5f5;
  color: #666;
}

.cancel-btn:hover {
  background: #e0e0e0;
}

.save-btn {
  background: #4285f4;
  color: white;
}

.save-btn:hover {
  background: #3367d6;
  transform: translateY(-1px);
}

/* 响应式设计 */
@media (max-width: 768px) {
  .search-panel {
    width: calc(100% - 40px);
    left: 20px;
    right: 20px;
  }
  
  .marker-info-panel {
    width: calc(100% - 40px);
    left: 20px;
    right: 20px;
    top: auto;
    bottom: 100px;
  }
  
  .favorites-panel {
    width: calc(100% - 40px);
    bottom: 20px;
  }
}

/* 滚动条样式 */
.search-results::-webkit-scrollbar,
.favorites-list::-webkit-scrollbar {
  width: 6px;
}

.search-results::-webkit-scrollbar-track,
.favorites-list::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 3px;
}

.search-results::-webkit-scrollbar-thumb,
.favorites-list::-webkit-scrollbar-thumb {
  background: #c1c1c1;
  border-radius: 3px;
}

.search-results::-webkit-scrollbar-thumb:hover,
.favorites-list::-webkit-scrollbar-thumb:hover {
  background: #a8a8a8;
}
</style>

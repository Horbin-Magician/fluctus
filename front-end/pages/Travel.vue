<!-- 旅行页 Travel -->
<template>
  <div class="travel-page">
    <!-- 地图容器 -->
    <div class="map-section">
      <div class="map-container">
        <!-- Map container -->
        <div id="amap" ref="mapContainer"/>
        
        <!-- 搜索工具栏 -->
        <div class="search-toolbar">
          <div class="search-input-container">
            <input
              v-model="searchQuery"
              type="text"
              placeholder="搜索旅行地点..."
              class="search-input"
              @keyup.enter="handleEnterKey"
              @keyup.up="handleArrowUp"
              @keyup.down="handleArrowDown"
              @keyup.esc="closeSuggestions"
              @input="onSearchInput"
              @blur="handleInputBlur"
            />
            <button @click="searchLocation" class="search-btn">
              <n-icon size="16">
                <Search />
              </n-icon>
            </button>
          </div>
          
          <!-- 搜索建议列表 -->
          <div v-if="searchSuggestions.length > 0" class="suggestions-list">
            <div
              v-for="(suggestion, index) in searchSuggestions"
              :key="index"
              class="suggestion-item"
              :class="{ 'suggestion-selected': index === selectedSuggestionIndex }"
              @click="selectSuggestion(suggestion)"
              @mouseenter="selectedSuggestionIndex = index"
            >
              <div class="suggestion-icon">
                <n-icon size="14">
                  <LocationOutline />
                </n-icon>
              </div>
              <div class="suggestion-content">
                <div class="suggestion-name">{{ suggestion.name }}</div>
                <div v-if="suggestion.district" class="suggestion-address">
                  {{ suggestion.district }}{{ suggestion.adcode ? ` · ${suggestion.adcode}` : '' }}
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- 地图控制按钮 -->
        <div class="map-controls">
          <button @click="getCurrentLocation" class="control-btn" title="定位到当前位置">
            <n-icon size="18">
              <LocationOutline />
            </n-icon>
          </button>
          <button @click="clearAllMarkers" class="control-btn" title="清除所有标记">
            <n-icon size="18">
              <TrashOutline />
            </n-icon>
          </button>
        </div>
      </div>
    </div>

    <!-- 侧边栏 -->
    <div class="sidebar" :class="{ 'sidebar-collapsed': sidebarCollapsed }">
      <div class="sidebar-header">
        <h3 v-if="!sidebarCollapsed">我的旅行地点</h3>
        <button @click="toggleSidebar" class="toggle-btn">
          <n-icon size="16">
            <ChevronForwardOutline v-if="sidebarCollapsed" />
            <ChevronBackOutline v-else />
          </n-icon>
        </button>
      </div>

      <div v-if="!sidebarCollapsed" class="sidebar-content">
        <!-- 统计信息 -->
        <div class="stats">
          <div class="stat-item">
            <span class="stat-label">已标记地点:</span>
            <span class="stat-value">{{ markedLocations.length }}</span>
          </div>
        </div>

        <!-- 地点列表 -->
        <div class="locations-list">
          <div
            v-for="location in markedLocations"
            :key="location.id"
            class="location-item"
            @click="focusLocation(location)"
          >
            <div class="location-info">
              <h4 class="location-name">{{ location.name }}</h4>
              <p class="location-address">{{ location.address }}</p>
              <p class="location-date">{{ formatDate(location.createdAt) }}</p>
            </div>
            <div class="location-actions">
              <button @click.stop="editLocation(location)" class="action-btn edit-btn">
                <n-icon size="14">
                  <CreateOutline />
                </n-icon>
              </button>
              <button @click.stop="removeLocation(location.id)" class="action-btn delete-btn">
                <n-icon size="14">
                  <TrashOutline />
                </n-icon>
              </button>
            </div>
          </div>
          
          <div v-if="markedLocations.length === 0" class="empty-state">
            <n-icon size="48">
              <LocationOutline />
            </n-icon>
            <p>还没有标记任何地点</p>
            <p>点击地图上的位置来添加标记</p>
          </div>
        </div>
      </div>
    </div>

    <!-- 地点详情弹窗 -->
    <div v-if="showLocationModal" class="modal-overlay" @click="closeLocationModal">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h3>{{ isEditingLocation ? '编辑地点' : '添加地点' }}</h3>
          <button @click="closeLocationModal" class="close-btn">
            <n-icon size="16">
              <CloseOutline />
            </n-icon>
          </button>
        </div>
        <div class="modal-body">
          <div class="form-group">
            <label>地点名称:</label>
            <input v-model="currentLocation.name" type="text" placeholder="请输入地点名称" />
          </div>
          <div class="form-group">
            <label>地址:</label>
            <input v-model="currentLocation.address" type="text" placeholder="请输入地址" />
          </div>
          <div class="form-group">
            <label>备注:</label>
            <textarea v-model="currentLocation.notes" placeholder="添加一些备注..."></textarea>
          </div>
        </div>
        <div class="modal-footer">
          <button @click="closeLocationModal" class="btn btn-cancel">取消</button>
          <button @click="saveLocation" class="btn btn-primary">保存</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, nextTick } from 'vue'
import { NIcon } from 'naive-ui'
import AMapLoader from '@amap/amap-jsapi-loader'
import storageUtils from '@/utils/storageUtils'
import { 
  Search, 
  LocationOutline, 
  TrashOutline, 
  ChevronForwardOutline, 
  ChevronBackOutline,
  CreateOutline,
  CloseOutline
} from '@vicons/ionicons5'

// 地图相关
let map: any = null
let placeSearch: any = null
let autocomplete: any = null
const mapContainer = ref<HTMLElement>()

// 搜索相关
const searchQuery = ref('')
const searchSuggestions = ref<any[]>([])
const selectedSuggestionIndex = ref(-1)
let searchTimeout: NodeJS.Timeout | null = null

// 侧边栏
const sidebarCollapsed = ref(false)

// 标记地点相关
interface MarkedLocation {
  id: string
  name: string
  address: string
  notes: string
  lng: number
  lat: number
  createdAt: Date
}

const markedLocations = ref<MarkedLocation[]>([])
const showLocationModal = ref(false)
const isEditingLocation = ref(false)
const currentLocation = ref<Partial<MarkedLocation>>({})
const currentMarker = ref<any>(null)

// 存储键
const TRAVEL_LOCATIONS_KEY = 'travel_locations'

// 初始化地图
const initMap = async () => {
  ;(window as any)._AMapSecurityConfig = {
    securityJsCode: "467acecf4320cdce83d519705e1aad3b",
  }

  try {
    const AMap = await AMapLoader.load({
      key: "3fbe22db53162479e06074420635fba4",
      version: "2.0",
      plugins: ['AMap.Scale', 'AMap.PlaceSearch', 'AMap.Autocomplete', 'AMap.Geolocation', 'AMap.Geocoder'],
    })

    map = new AMap.Map("amap", {
      viewMode: "3D",
      zoom: 11,
      center: [116.397428, 39.90923],
    })

    // 添加地图控件
    map.addControl(new AMap.Scale())

    // 初始化搜索功能
    placeSearch = new AMap.PlaceSearch({
      map: map,
      panel: false
    })

    // 初始化AutoComplete - 使用正确的配置
    autocomplete = new AMap.AutoComplete({
      city: '全国', // 搜索范围
      citylimit: false, // 不限制城市
      datatype: 'all', // 返回所有数据类型
      extensions: 'all' // 返回扩展信息
    })
    
    console.log('AutoComplete initialized:', autocomplete)
    
    // 测试AutoComplete是否工作
    setTimeout(() => {
      if (autocomplete) {
        console.log('Testing AutoComplete with "北京"...')
        autocomplete.search('北京', (status: string, result: any) => {
          console.log('Test AutoComplete status:', status)
          console.log('Test AutoComplete result:', result)
        })
      }
    }, 1000)

    // 地图点击事件
    map.on('click', onMapClick)

    // 加载已保存的地点
    loadSavedLocations()

  } catch (error) {
    console.error('地图初始化失败:', error)
  }
}

// 地图点击事件处理
const onMapClick = (e: any) => {
  const { lng, lat } = e.lnglat
  
  // 逆地理编码获取地址信息
  const geocoder = new (window as any).AMap.Geocoder()
  geocoder.getAddress([lng, lat], (status: string, result: any) => {
    if (status === 'complete' && result.regeocode) {
      const address = result.regeocode.formattedAddress
      const poi = result.regeocode.pois[0]
      
      currentLocation.value = {
        name: poi?.name || '未知地点',
        address: address,
        notes: '',
        lng,
        lat,
        createdAt: new Date()
      }
      
      showLocationModal.value = true
      isEditingLocation.value = false
    }
  })
}

// 搜索输入处理
const onSearchInput = () => {
  if (searchTimeout) {
    clearTimeout(searchTimeout)
  }
  
  // 重置选中索引
  selectedSuggestionIndex.value = -1
  
  searchTimeout = setTimeout(() => {
    if (searchQuery.value.trim()) {
      console.log('Search query:', searchQuery.value)
      console.log('AutoComplete object:', autocomplete)
      
      if (autocomplete) {
        autocomplete.search(searchQuery.value, (status: string, result: any) => {
          console.log('AutoComplete status:', status)
          console.log('AutoComplete result:', result)
          
          if (status === 'complete' && result.tips && result.tips.length > 0) {
            // 过滤并处理建议项
            const validTips = result.tips.filter((tip: any) => 
              tip.name && tip.name.trim()
            ).map((tip: any) => ({
              name: tip.name,
              district: tip.district || tip.adname || '',
              adcode: tip.adcode || '',
              location: tip.location
            }))
            
            console.log('Valid tips:', validTips)
            searchSuggestions.value = validTips.slice(0, 8)
          } else {
            console.log('No tips found or status not complete, status:', status)
            searchSuggestions.value = []
          }
        })
      } else {
        console.error('AutoComplete not initialized')
        searchSuggestions.value = []
      }
    } else {
      searchSuggestions.value = []
    }
  }, 200)
}

// 搜索地点
const searchLocation = () => {
  if (!searchQuery.value.trim()) return
  
  placeSearch.search(searchQuery.value, (status: string, result: any) => {
    if (status === 'complete' && result.poiList.pois.length > 0) {
      const poi = result.poiList.pois[0]
      map.setCenter([poi.location.lng, poi.location.lat])
      map.setZoom(15)
    }
  })
  
  searchSuggestions.value = []
}

// 选择搜索建议
const selectSuggestion = (suggestion: any) => {
  searchQuery.value = suggestion.name
  searchLocation()
  selectedSuggestionIndex.value = -1
}

// 键盘导航处理
const handleEnterKey = () => {
  if (selectedSuggestionIndex.value >= 0 && searchSuggestions.value[selectedSuggestionIndex.value]) {
    selectSuggestion(searchSuggestions.value[selectedSuggestionIndex.value])
  } else {
    searchLocation()
  }
}

const handleArrowUp = () => {
  if (searchSuggestions.value.length > 0) {
    selectedSuggestionIndex.value = selectedSuggestionIndex.value <= 0 
      ? searchSuggestions.value.length - 1 
      : selectedSuggestionIndex.value - 1
  }
}

const handleArrowDown = () => {
  if (searchSuggestions.value.length > 0) {
    selectedSuggestionIndex.value = selectedSuggestionIndex.value >= searchSuggestions.value.length - 1 
      ? 0 
      : selectedSuggestionIndex.value + 1
  }
}

const closeSuggestions = () => {
  searchSuggestions.value = []
  selectedSuggestionIndex.value = -1
}

const handleInputBlur = () => {
  // 延迟关闭建议列表，以便点击建议项能正常工作
  setTimeout(() => {
    closeSuggestions()
  }, 200)
}

// 获取当前位置
const getCurrentLocation = () => {
  const geolocation = new (window as any).AMap.Geolocation({
    enableHighAccuracy: true,
    timeout: 10000,
  })
  
  geolocation.getCurrentPosition((status: string, result: any) => {
    if (status === 'complete') {
      map.setCenter([result.position.lng, result.position.lat])
      map.setZoom(15)
    } else {
      console.error('定位失败:', result.message)
    }
  })
}

// 清除所有标记
const clearAllMarkers = () => {
  if (confirm('确定要清除所有地点标记吗？')) {
    map.clearMap()
    markedLocations.value = []
    saveLocationsToStorage()
  }
}

// 切换侧边栏
const toggleSidebar = () => {
  sidebarCollapsed.value = !sidebarCollapsed.value
}

// 聚焦到地点
const focusLocation = (location: MarkedLocation) => {
  map.setCenter([location.lng, location.lat])
  map.setZoom(15)
}

// 编辑地点
const editLocation = (location: MarkedLocation) => {
  currentLocation.value = { ...location }
  isEditingLocation.value = true
  showLocationModal.value = true
}

// 删除地点
const removeLocation = (id: string) => {
  if (confirm('确定要删除这个地点吗？')) {
    markedLocations.value = markedLocations.value.filter(loc => loc.id !== id)
    saveLocationsToStorage()
    
    // 从地图上移除对应的标记
    map.getAllOverlays('marker').forEach((marker: any) => {
      if (marker.getExtData()?.id === id) {
        map.remove(marker)
      }
    })
  }
}

// 保存地点
const saveLocation = () => {
  if (!currentLocation.value.name?.trim()) {
    alert('请输入地点名称')
    return
  }

  if (isEditingLocation.value) {
    // 更新现有地点
    const index = markedLocations.value.findIndex(loc => loc.id === currentLocation.value.id)
    if (index !== -1) {
      markedLocations.value[index] = currentLocation.value as MarkedLocation
    }
  } else {
    // 添加新地点
    const newLocation: MarkedLocation = {
      ...currentLocation.value as MarkedLocation,
      id: Date.now().toString()
    }
    markedLocations.value.push(newLocation)
    
    // 在地图上添加标记
    addMarkerToMap(newLocation)
  }
  
  saveLocationsToStorage()
  closeLocationModal()
}

// 在地图上添加标记
const addMarkerToMap = (location: MarkedLocation) => {
  const marker = new (window as any).AMap.Marker({
    position: [location.lng, location.lat],
    title: location.name,
    extData: { id: location.id }
  })
  
  // 添加信息窗口
  const infoWindow = new (window as any).AMap.InfoWindow({
    content: `
      <div style="padding: 10px;">
        <h4>${location.name}</h4>
        <p>${location.address}</p>
        ${location.notes ? `<p><strong>备注:</strong> ${location.notes}</p>` : ''}
      </div>
    `
  })
  
  marker.on('click', () => {
    infoWindow.open(map, marker.getPosition())
  })
  
  map.add(marker)
}

// 关闭地点弹窗
const closeLocationModal = () => {
  showLocationModal.value = false
  currentLocation.value = {}
  currentMarker.value = null
}

// 保存地点到本地存储
const saveLocationsToStorage = () => {
  localStorage.setItem(TRAVEL_LOCATIONS_KEY, JSON.stringify(markedLocations.value))
}

// 从本地存储加载地点
const loadSavedLocations = () => {
  const saved = localStorage.getItem(TRAVEL_LOCATIONS_KEY)
  if (saved) {
    try {
      markedLocations.value = JSON.parse(saved)
      // 在地图上添加所有保存的标记
      markedLocations.value.forEach(location => {
        addMarkerToMap(location)
      })
    } catch (error) {
      console.error('加载保存的地点失败:', error)
    }
  }
}

// 格式化日期
const formatDate = (date: Date | string) => {
  const d = new Date(date)
  return d.toLocaleDateString('zh-CN')
}

onMounted(() => {
  nextTick(() => {
    initMap()
  })
})

onUnmounted(() => {
  if (searchTimeout) {
    clearTimeout(searchTimeout)
  }
  map?.destroy()
})
</script>

<style scoped>
.travel-page {
  display: flex;
  height: 100vh;
  background: #f5f5f5;
}

.map-section {
  flex: 1;
  position: relative;
}

.map-container {
  width: 100%;
  height: 100%;
  position: relative;
}

#amap {
  width: 100%;
  height: 100%;
}

/* 搜索工具栏 */
.search-toolbar {
  position: absolute;
  top: 20px;
  left: 20px;
  z-index: 1000;
  width: 400px;
}

.search-input-container {
  display: flex;
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  overflow: hidden;
}

.search-input {
  flex: 1;
  padding: 12px 16px;
  border: none;
  outline: none;
  font-size: 14px;
}

.search-btn {
  padding: 12px 16px;
  background: #1890ff;
  color: white;
  border: none;
  cursor: pointer;
  transition: background-color 0.3s;
}

.search-btn:hover {
  background: #40a9ff;
}

.suggestions-list {
  background: white;
  border-radius: 0 0 8px 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  max-height: 200px;
  overflow-y: auto;
}

.suggestion-item {
  padding: 12px 16px;
  cursor: pointer;
  border-bottom: 1px solid #f0f0f0;
  display: flex;
  align-items: flex-start;
  gap: 12px;
  transition: all 0.2s ease;
}

.suggestion-item:hover,
.suggestion-selected {
  background: #e6f7ff;
  border-left: 3px solid #1890ff;
  padding-left: 13px;
}

.suggestion-item:last-child {
  border-bottom: none;
}

.suggestion-icon {
  margin-top: 2px;
  color: #1890ff;
  flex-shrink: 0;
}

.suggestion-content {
  flex: 1;
  min-width: 0;
}

.suggestion-name {
  font-size: 14px;
  font-weight: 500;
  color: #333;
  margin-bottom: 2px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.suggestion-address {
  font-size: 12px;
  color: #666;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.suggestion-selected .suggestion-name {
  color: #1890ff;
}

.suggestion-selected .suggestion-address {
  color: #40a9ff;
}

/* 地图控制按钮 */
.map-controls {
  position: absolute;
  top: 20px;
  right: 20px;
  display: flex;
  flex-direction: column;
  gap: 10px;
  z-index: 1000;
}

.control-btn {
  width: 40px;
  height: 40px;
  background: white;
  border: none;
  border-radius: 6px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s;
}

.control-btn:hover {
  background: #f5f5f5;
  transform: translateY(-1px);
}

/* 侧边栏 */
.sidebar {
  width: 350px;
  background: white;
  border-left: 1px solid #e8e8e8;
  display: flex;
  flex-direction: column;
  transition: width 0.3s ease;
}

.sidebar-collapsed {
  width: 60px;
}

.sidebar-header {
  padding: 20px;
  border-bottom: 1px solid #e8e8e8;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.sidebar-header h3 {
  margin: 0;
  font-size: 18px;
  color: #333;
}

.toggle-btn {
  width: 32px;
  height: 32px;
  border: none;
  background: #f5f5f5;
  border-radius: 4px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
}

.sidebar-content {
  flex: 1;
  overflow-y: auto;
}

/* 统计信息 */
.stats {
  padding: 20px;
  border-bottom: 1px solid #e8e8e8;
}

.stat-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.stat-label {
  color: #666;
  font-size: 14px;
}

.stat-value {
  font-size: 18px;
  font-weight: bold;
  color: #1890ff;
}

/* 地点列表 */
.locations-list {
  padding: 20px;
}

.location-item {
  padding: 16px;
  border: 1px solid #e8e8e8;
  border-radius: 8px;
  margin-bottom: 12px;
  cursor: pointer;
  transition: all 0.3s;
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
}

.location-item:hover {
  border-color: #1890ff;
  box-shadow: 0 2px 8px rgba(24, 144, 255, 0.1);
}

.location-info {
  flex: 1;
}

.location-name {
  margin: 0 0 8px 0;
  font-size: 16px;
  color: #333;
}

.location-address {
  margin: 0 0 4px 0;
  font-size: 14px;
  color: #666;
}

.location-date {
  margin: 0;
  font-size: 12px;
  color: #999;
}

.location-actions {
  display: flex;
  gap: 8px;
}

.action-btn {
  width: 28px;
  height: 28px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s;
}

.edit-btn {
  background: #f0f9ff;
  color: #1890ff;
}

.edit-btn:hover {
  background: #e6f7ff;
}

.delete-btn {
  background: #fff2f0;
  color: #ff4d4f;
}

.delete-btn:hover {
  background: #ffece8;
}

.empty-state {
  text-align: center;
  padding: 40px 20px;
  color: #999;
}

.empty-state svg {
  font-size: 48px;
  margin-bottom: 16px;
  display: block;
  width: 48px;
  height: 48px;
  margin: 0 auto 16px auto;
}

/* 弹窗样式 */
.modal-overlay {
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

.modal-content {
  background: white;
  border-radius: 8px;
  width: 500px;
  max-width: 90vw;
  max-height: 90vh;
  overflow: hidden;
}

.modal-header {
  padding: 20px;
  border-bottom: 1px solid #e8e8e8;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.modal-header h3 {
  margin: 0;
  font-size: 18px;
}

.close-btn {
  width: 32px;
  height: 32px;
  border: none;
  background: none;
  cursor: pointer;
  border-radius: 4px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.close-btn:hover {
  background: #f5f5f5;
}

.modal-body {
  padding: 20px;
}

.form-group {
  margin-bottom: 20px;
}

.form-group label {
  display: block;
  margin-bottom: 8px;
  font-weight: 500;
  color: #333;
}

.form-group input,
.form-group textarea {
  width: 100%;
  padding: 8px 12px;
  border: 1px solid #d9d9d9;
  border-radius: 4px;
  font-size: 14px;
  transition: border-color 0.3s;
}

.form-group input:focus,
.form-group textarea:focus {
  outline: none;
  border-color: #1890ff;
}

.form-group textarea {
  height: 80px;
  resize: vertical;
}

.modal-footer {
  padding: 20px;
  border-top: 1px solid #e8e8e8;
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}

.btn {
  padding: 8px 16px;
  border: 1px solid #d9d9d9;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  transition: all 0.3s;
}

.btn-cancel {
  background: white;
  color: #666;
}

.btn-cancel:hover {
  border-color: #1890ff;
  color: #1890ff;
}

.btn-primary {
  background: #1890ff;
  color: white;
  border-color: #1890ff;
}

.btn-primary:hover {
  background: #40a9ff;
  border-color: #40a9ff;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .travel-page {
    flex-direction: column;
  }
  
  .sidebar {
    width: 100%;
    height: 300px;
  }
  
  .sidebar-collapsed {
    height: 60px;
  }
  
  .search-toolbar {
    width: calc(100% - 40px);
  }
}
</style>

<!-- 旅行页 Travel -->
<template>
  <div class="travel-page">
    <!-- 日记列表视图 -->
    <div v-if="!currentDiary" class="diary-list-view">
      <div class="diary-list-panel">
        <div class="diary-header">
          <div class="diary-header-left">
            <n-icon class="diary-header-icon" size="24"> <BookmarksIcon/> </n-icon>
            <h2>旅行日记</h2>
          </div>
          <button class="create-btn" @click="showCreateModal = true">
            <svg xmlns="http://www.w3.org/2000/svg" width="15" height="15" viewBox="0 0 24 24"
              fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
              <line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/>
            </svg>
            新建日记
          </button>
        </div>
        <div v-if="diaries.length === 0" class="empty-state">
          <svg class="empty-icon" xmlns="http://www.w3.org/2000/svg" width="48" height="48" viewBox="0 0 24 24"
            fill="none" stroke="currentColor" stroke-width="1.2" stroke-linecap="round" stroke-linejoin="round">
            <path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"/>
            <circle cx="12" cy="10" r="3"/>
          </svg>
          <p>还没有旅行日记</p>
          <span class="empty-hint">点击上方按钮，创建一个开始记录吧</span>
        </div>
        <div v-else class="diary-items">
          <div
            v-for="(diary, index) in diaries"
            :key="diary.id"
            class="diary-item"
            :style="{ animationDelay: `${index * 0.05}s` }"
            @click="openDiary(diary)"
          >
            <div class="diary-info">
              <div class="diary-name">{{ diary.name }}</div>
              <div class="diary-meta">
                <span class="diary-time">{{ diary.updated_at }}</span>
              </div>
            </div>
            <div class="diary-actions">
              <button class="delete-btn" title="删除日记" @click.stop="confirmDelete(diary)">
                <svg xmlns="http://www.w3.org/2000/svg" width="15" height="15" viewBox="0 0 24 24"
                  fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"
                  stroke-linejoin="round">
                  <polyline points="3 6 5 6 21 6"/>
                  <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/>
                </svg>
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 地图视图 -->
    <div v-else class="map-view">
      <MapContainer
        :places="diaryPlaces"
        :diary-name="currentDiary.name"
        :initial-view="currentDiaryView"
        @add-place="addPlaceToDiary"
        @remove-place="removePlaceFromDiary"
        @update-place-type="updatePlaceType"
        @update-place-description="updatePlaceDescription"
        @view-change="handleMapViewChange"
        @back="closeDiary"
      />
    </div>

    <!-- 新建日记弹窗 -->
    <n-modal v-model:show="showCreateModal" preset="dialog" :closable="false"
      title="新建旅行日记" positive-text="创建" negative-text="取消"
      @positive-click="handleCreate" @negative-click="showCreateModal = false">
      <n-input v-model:value="newDiaryName" placeholder="输入日记名称"
        @keyup.enter="handleCreate" />
    </n-modal>

    <!-- 删除确认弹窗 -->
    <n-modal v-model:show="showDeleteModal" preset="dialog" :closable="false"
      type="warning" title="删除日记"
      :content="`确定要删除「${deletingDiary?.name}」吗？所有地点数据将被清除。`"
      positive-text="确认删除" negative-text="取消"
      @positive-click="handleDelete" />
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { NModal, NInput, useMessage, NIcon } from 'naive-ui'
import { checkLoginPromise } from '@/utils/userUtils'
import { Bookmarks as BookmarksIcon } from "@vicons/ionicons5"
import ajax from '@/api/ajax'
import { preloadAmap } from '@/utils/amapLoader'

const message = useMessage()

const currentDiary = ref(null)
const diaries = ref([])
const diaryPlaces = ref([])
const showCreateModal = ref(false)
const showDeleteModal = ref(false)
const newDiaryName = ref('')
const deletingDiary = ref(null)
const currentDiaryView = ref(null)
let mapViewSyncTimer = null
let lastSyncedDiaryView = null

const VIEW_SYNC_DISTANCE_THRESHOLD_METERS = 50
const VIEW_SYNC_ZOOM_THRESHOLD = 0.2

function toRadians(degree) {
  return degree * Math.PI / 180
}

function getDistanceMeters(centerA, centerB) {
  if (!Array.isArray(centerA) || !Array.isArray(centerB)) return Number.POSITIVE_INFINITY
  const [lng1, lat1] = centerA.map(Number)
  const [lng2, lat2] = centerB.map(Number)
  if (![lng1, lat1, lng2, lat2].every(Number.isFinite)) return Number.POSITIVE_INFINITY
  const earthRadius = 6371000
  const dLat = toRadians(lat2 - lat1)
  const dLng = toRadians(lng2 - lng1)
  const a = Math.sin(dLat / 2) ** 2
    + Math.cos(toRadians(lat1)) * Math.cos(toRadians(lat2)) * Math.sin(dLng / 2) ** 2
  const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a))
  return earthRadius * c
}

function shouldSyncDiaryView(nextView, prevView) {
  if (!nextView?.center || !Number.isFinite(Number(nextView.zoom))) return false
  if (!prevView?.center || !Number.isFinite(Number(prevView.zoom))) return true
  const zoomDiff = Math.abs(Number(nextView.zoom) - Number(prevView.zoom))
  if (zoomDiff >= VIEW_SYNC_ZOOM_THRESHOLD) return true
  const distance = getDistanceMeters(nextView.center, prevView.center)
  return distance >= VIEW_SYNC_DISTANCE_THRESHOLD_METERS
}

function normalizeDiaryView(diary) {
  const lng = Number(diary?.view_lng)
  const lat = Number(diary?.view_lat)
  const zoom = Number(diary?.view_zoom)
  if (!Number.isFinite(lng) || !Number.isFinite(lat) || !Number.isFinite(zoom)) {
    return null
  }
  return { center: [lng, lat], zoom }
}

function normalizeImageUrls(images) {
  if (!Array.isArray(images)) return []
  const urls = images
    .filter((item) => typeof item === 'string')
    .map((item) => item.trim())
    .filter((item) => /^https?:\/\//i.test(item))
  return [...new Set(urls)].slice(0, 6)
}

function parsePlaceNote(note) {
  if (typeof note !== 'string' || !note.trim()) {
    return { description: '', images: [] }
  }
  try {
    const parsed = JSON.parse(note)
    return {
      description: typeof parsed?.description === 'string' ? parsed.description.trim() : '',
      images: normalizeImageUrls(parsed?.images)
    }
  } catch {
    return { description: note.trim(), images: [] }
  }
}

function normalizePlaces(rawPlaces) {
  if (!Array.isArray(rawPlaces)) return []
  return rawPlaces.map((place) => {
    const extra = parsePlaceNote(place?.note)
    return {
      ...place,
      description: extra.description,
      images: extra.images
    }
  })
}

function buildPlaceNote(markerData) {
  const description = typeof markerData?.description === 'string'
    ? markerData.description.trim()
    : ''
  const images = normalizeImageUrls(markerData?.images)
  if (!description && images.length === 0) return ''
  return JSON.stringify({ description, images })
}

async function apiCall(data) {
  return ajax('/api/travel', data, 'POST')
}

async function fetchDiaries() {
  const loggedIn = await checkLoginPromise()
  if (!loggedIn) return
  const res = await apiCall({ type: 'get_diaries' })
  if (res.status === '0') diaries.value = res.data
}

async function handleCreate() {
  const name = newDiaryName.value.trim()
  if (!name) { message.warning('请输入日记名称'); return false }
  const res = await apiCall({ type: 'create_diary', name })
  if (res.status === '0') {
    await fetchDiaries()
    newDiaryName.value = ''
    showCreateModal.value = false
    message.success('创建成功')
  }
}

function confirmDelete(diary) {
  deletingDiary.value = diary
  showDeleteModal.value = true
}

async function handleDelete() {
  if (!deletingDiary.value) return
  const res = await apiCall({ type: 'delete_diary', diary_id: deletingDiary.value.id })
  if (res.status === '0') {
    await fetchDiaries()
    deletingDiary.value = null
    message.success('已删除')
  }
}

async function openDiary(diary) {
  currentDiaryView.value = normalizeDiaryView(diary)
  lastSyncedDiaryView = currentDiaryView.value
  currentDiary.value = diary
  const res = await apiCall({ type: 'get_places', diary_id: diary.id })
  if (res.status !== '0') return
  diaryPlaces.value = normalizePlaces(res.data)
  currentDiaryView.value = res.view || currentDiaryView.value
  lastSyncedDiaryView = currentDiaryView.value
}

function closeDiary() {
  if (mapViewSyncTimer) {
    clearTimeout(mapViewSyncTimer)
    mapViewSyncTimer = null
  }
  currentDiary.value = null
  currentDiaryView.value = null
  lastSyncedDiaryView = null
  diaryPlaces.value = []
}

function handleMapViewChange(view) {
  const diaryId = currentDiary.value?.id
  if (!diaryId || !view) return
  currentDiaryView.value = view
  if (!shouldSyncDiaryView(view, lastSyncedDiaryView)) return
  if (mapViewSyncTimer) clearTimeout(mapViewSyncTimer)
  mapViewSyncTimer = setTimeout(() => {
    apiCall({
      type: 'update_diary_view',
      diary_id: diaryId,
      center: view.center,
      zoom: view.zoom
    }).then((res) => {
      if (res?.status === '0') {
        lastSyncedDiaryView = view
      }
    }).catch(() => undefined)
    mapViewSyncTimer = null
  }, 220)
}

async function addPlaceToDiary(markerData) {
  if (!currentDiary.value) return
  const place = {
    poi_id: markerData.id || '',
    name: markerData.name || '',
    address: markerData.address || '',
    lng: markerData.location?.lng || 0,
    lat: markerData.location?.lat || 0,
    tel: markerData.tel || '',
    type: markerData.type || '',
    typecode: markerData.typecode || '',
    note: buildPlaceNote(markerData)
  }
  const res = await apiCall({ type: 'add_place', diary_id: currentDiary.value.id, place })
  if (res.status === '0') {
    const placesRes = await apiCall({ type: 'get_places', diary_id: currentDiary.value.id })
    if (placesRes.status === '0') diaryPlaces.value = normalizePlaces(placesRes.data)
    message.success('已添加到日记')
  }
}

async function removePlaceFromDiary(placeId) {
  if (!currentDiary.value) return
  const res = await apiCall({ type: 'delete_place', diary_id: currentDiary.value.id, place_id: placeId })
  if (res.status === '0') {
    diaryPlaces.value = diaryPlaces.value.filter(p => p.id !== placeId)
    message.success('已移除')
  }
}

async function updatePlaceType(placeId, typecode) {
  if (!currentDiary.value) return
  const res = await apiCall({
    type: 'update_place_typecode',
    diary_id: currentDiary.value.id,
    place_id: placeId,
    typecode
  })
  if (res.status === '0') {
    const place = diaryPlaces.value.find(p => p.id === placeId)
    if (place) place.typecode = typecode
  }
}

async function updatePlaceDescription(payload) {
  if (!currentDiary.value) return
  const placeId = Number(payload?.placeId)
  if (!Number.isFinite(placeId)) return
  const place = diaryPlaces.value.find((item) => item.id === placeId)
  if (!place) return
  const description = typeof payload?.description === 'string'
    ? payload.description.trim()
    : ''
  const note = buildPlaceNote({ description, images: place.images })
  const res = await apiCall({
    type: 'update_place_note',
    diary_id: currentDiary.value.id,
    place_id: placeId,
    note
  })
  if (res.status === '0') {
    place.description = description
    place.note = note
    message.success('简介已保存')
  }
}

onMounted(() => {
  fetchDiaries()
  preloadAmap().catch(() => undefined)
})

onUnmounted(() => {
  if (mapViewSyncTimer) {
    clearTimeout(mapViewSyncTimer)
    mapViewSyncTimer = null
  }
})
</script>

<style scoped>
/* 日记列表视图 */
.diary-list-view {
  display: flex;
  justify-content: center;
  align-items: flex-start;
  padding: 80px 20px;
}

.diary-list-panel {
  width: 100%;
  max-width: 640px;
  background: var(--color-background);
  border-radius: 16px;
  box-shadow: 0 4px 24px rgba(0, 0, 0, 0.06);
  border: 1px solid var(--color-border);
  padding: 32px;
}

/* 头部 */
.diary-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 28px;
  padding-bottom: 20px;
  border-bottom: 1px solid var(--color-border);
}

.diary-header-left {
  display: flex;
  align-items: center;
  gap: 10px;
}

.diary-header-icon {
  color: var(--color-light);
}

.diary-header h2 {
  margin: 0;
  font-size: 20px;
  font-weight: 600;
  color: var(--color-text);
  letter-spacing: -0.3px;
}

.create-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 16px;
  border: none;
  border-radius: 20px;
  background: var(--color-light);
  color: var(--color-background);
  cursor: pointer;
  font-size: 13px;
  font-weight: 500;
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.create-btn:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(var(--color-primary-rgb), 0.3);
}

.create-btn:active {
  transform: translateY(0);
}

/* 空状态 */
.empty-state {
  text-align: center;
  padding: 48px 20px;
}

.empty-icon {
  color: var(--color-text-sub-sub);
  margin-bottom: 16px;
}

.empty-state p {
  font-size: 15px;
  color: var(--color-text-sub);
  margin-bottom: 6px;
}

.empty-hint {
  font-size: 13px;
  color: var(--color-text-sub-sub);
}

/* 日记列表 */
.diary-items {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

@keyframes fadeSlideIn {
  from {
    opacity: 0;
    transform: translateY(8px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.diary-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 14px 16px;
  border-radius: 10px;
  background: var(--color-background-soft);
  cursor: pointer;
  transition: transform 0.2s ease, box-shadow 0.2s ease, background 0.2s ease;
  animation: fadeSlideIn 0.3s ease both;
}

.diary-item:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.06);
}

.diary-info {
  flex: 1;
  min-width: 0;
}

.diary-name {
  font-size: 15px;
  font-weight: 500;
  color: var(--color-text);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.diary-meta {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-top: 4px;
}

.diary-time {
  font-size: 12px;
  color: var(--color-text-sub-sub);
}

/* 操作区 */
.diary-actions {
  display: flex;
  align-items: center;
  gap: 4px;
  margin-left: 12px;
  flex-shrink: 0;
}

.delete-btn {
  background: none;
  border: none;
  color: var(--color-text-sub-sub);
  cursor: pointer;
  padding: 6px;
  border-radius: 6px;
  transition: color 0.2s ease, background 0.2s ease;
  opacity: 0;
}

.diary-item:hover .delete-btn {
  opacity: 1;
}

.delete-btn:hover {
  color: #e74c3c;
  background: rgba(231, 76, 60, 0.08);
}

/* 地图视图 */
.map-view {
  position: relative;
  width: 100%;
  height: 100vh;
}
</style>

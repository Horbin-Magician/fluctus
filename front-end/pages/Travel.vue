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
          <button class="create-btn" :disabled="creatingDiary || loadingDiaries" @click="showCreateModal = true">
            <svg xmlns="http://www.w3.org/2000/svg" width="15" height="15" viewBox="0 0 24 24"
              fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
              <line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/>
            </svg>
            新建日记
          </button>
        </div>
        <n-spin :show="loadingDiaries || openingDiary">
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
                  <div v-if="diary.trip_time" class="diary-meta-row diary-trip-time">出行时间：{{ diary.trip_time }}</div>
                  <div class="diary-meta-row">
                    <span class="diary-access">创建者：{{ diary.username }}</span>
                    <span class="diary-access">共享者：{{ formatSharersText(diary.sharers) }}</span>
                    <div class="diary-meta-row diary-time">{{ diary.updated_at }}</div>
                  </div>
                </div>
                <div v-if="diary.summary" class="diary-summary">{{ diary.summary }}</div>
              </div>
              <div class="diary-actions">
                <button class="edit-btn" title="编辑日记" @click.stop="startEdit(diary)">
                  <svg xmlns="http://www.w3.org/2000/svg" width="15" height="15" viewBox="0 0 24 24"
                    fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"
                    stroke-linejoin="round">
                    <path d="M12 20h9"/>
                    <path d="M16.5 3.5a2.12 2.12 0 0 1 3 3L7 19l-4 1 1-4 12.5-12.5z"/>
                  </svg>
                </button>
                <button v-if="diary.can_delete" class="delete-btn" title="删除日记" @click.stop="confirmDelete(diary)">
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
        </n-spin>
      </div>
    </div>

    <!-- 地图视图 -->
    <div v-else class="map-view">
      <n-spin class="map-view-spin" :show="loadingDiaryPlaces || placeActionLoading">
        <LazyMapContainer
          :places="diaryPlaces"
          :diary-name="currentDiary.name"
          :diary-owner="currentDiary.username || ''"
          :diary-sharers="currentDiary.sharers || []"
          :diary-trip-time="currentDiary.trip_time || ''"
          :diary-summary="currentDiary.summary || ''"
          :initial-view="currentDiaryView"
          @add-place="addPlaceToDiary"
          @remove-place="removePlaceFromDiary"
          @update-place-type="updatePlaceType"
          @update-place-description="updatePlaceDescription"
          @update-route-plan="updateRoutePlan"
          @view-change="handleMapViewChange"
          @edit-diary="startEdit(currentDiary)"
          @back="closeDiary"
        />
      </n-spin>
    </div>

    <!-- 新建日记弹窗 -->
    <n-modal v-model:show="showCreateModal" preset="dialog" :closable="false"
      title="新建旅行日记" positive-text="创建" negative-text="取消"
      :positive-button-props="{ loading: creatingDiary, disabled: creatingDiary }"
      :negative-button-props="{ disabled: creatingDiary }"
      @positive-click="handleCreate" @negative-click="handleCancelCreate">
      <div class="create-form">
        <n-input v-model:value="newDiaryName" placeholder="输入日记名称"
          @keyup.enter="handleCreate" />
        <n-date-picker
          v-model:value="newDiaryStartDate"
          type="date"
          clearable
          :first-day-of-week="1"
          placeholder="开始日期"
        />
        <n-input
          v-model:value="newDiarySummary"
          type="textarea"
          :maxlength="300"
          :autosize="{ minRows: 2, maxRows: 4 }"
          placeholder="旅行简介（可选）"
        />
      </div>
    </n-modal>

    <!-- 编辑日记弹窗 -->
    <n-modal v-model:show="showEditModal" preset="dialog" :closable="false"
      title="编辑旅行日记" positive-text="保存" negative-text="取消"
      :positive-button-props="{ loading: editingDiaryLoading, disabled: editingDiaryLoading }"
      :negative-button-props="{ disabled: editingDiaryLoading }"
      @positive-click="handleEdit" @negative-click="handleCancelEdit">
      <div class="create-form">
        <n-input v-model:value="editingDiaryName" placeholder="输入日记名称"
          @keyup.enter="handleEdit" />
        <n-date-picker
          v-model:value="editingDiaryStartDate"
          type="date"
          clearable
          :first-day-of-week="1"
          placeholder="开始日期"
        />
        <n-input
          v-model:value="editingDiarySummary"
          type="textarea"
          :maxlength="300"
          :autosize="{ minRows: 2, maxRows: 4 }"
          placeholder="旅行简介（可选）"
        />
        <n-select
          v-if="editingDiary?.can_manage_share"
          v-model:value="editingDiarySharers"
          multiple
          filterable
          clearable
          tag
          :options="diaryShareCandidates"
          placeholder="添加共享者（输入用户名后回车）"
        />
      </div>
    </n-modal>

    <!-- 删除确认弹窗 -->
    <n-modal v-model:show="showDeleteModal" preset="dialog" :closable="false"
      type="warning" title="删除日记"
      :content="`确定要删除「${deletingDiary?.name}」吗？所有地点数据将被清除。`"
      positive-text="确认删除" negative-text="取消"
      :positive-button-props="{ loading: deletingDiaryLoading, disabled: deletingDiaryLoading }"
      :negative-button-props="{ disabled: deletingDiaryLoading }"
      @positive-click="handleDelete" />
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { NModal, NInput, NDatePicker, NSelect, useMessage, NIcon, NSpin } from 'naive-ui'
import { Bookmarks as BookmarksIcon } from "@vicons/ionicons5"
import ajax from '@/api/ajax'

definePageMeta({
  middleware: 'auth'
})

const message = useMessage()

const currentDiary = ref(null)
const diaries = ref([])
const diaryPlaces = ref([])
const showCreateModal = ref(false)
const showEditModal = ref(false)
const showDeleteModal = ref(false)
const newDiaryName = ref('')
const newDiaryStartDate = ref(null)
const newDiarySummary = ref('')
const editingDiary = ref(null)
const editingDiaryName = ref('')
const editingDiaryStartDate = ref(null)
const editingDiarySummary = ref('')
const editingDiarySharers = ref([])
const diaryShareCandidates = ref([])
const deletingDiary = ref(null)
const currentDiaryView = ref(null)
const loadingDiaries = ref(false)
const creatingDiary = ref(false)
const editingDiaryLoading = ref(false)
const deletingDiaryLoading = ref(false)
const openingDiary = ref(false)
const loadingDiaryPlaces = ref(false)
const placeActionLoading = ref(false)
let mapViewSyncTimer = null
let lastSyncedDiaryView = null
let pendingDiaryView = null
let viewSyncInFlight = false
let lastViewSyncAt = 0

const VIEW_SYNC_DISTANCE_THRESHOLD_METERS = 50
const VIEW_SYNC_ZOOM_THRESHOLD = 0.2
const VIEW_SYNC_MIN_INTERVAL_MS = 1200

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

function formatDateValue(value) {
  const date = new Date(Number(value))
  if (Number.isNaN(date.getTime())) return ''
  const year = date.getFullYear()
  const month = String(date.getMonth() + 1).padStart(2, '0')
  const day = String(date.getDate()).padStart(2, '0')
  return `${year}-${month}-${day}`
}

function formatSharersText(sharers) {
  if (!Array.isArray(sharers) || sharers.length === 0) return '无'
  return sharers.join('、')
}

function formatTripTimeByStartDate(startValue, dayCount = 1) {
  const start = formatDateValue(startValue)
  if (!start) return ''
  const normalizedDayCount = Number.isFinite(Number(dayCount)) && Number(dayCount) >= 1
    ? Math.floor(Number(dayCount))
    : 1
  if (normalizedDayCount <= 1) return start
  const startTimestamp = Date.parse(`${start}T00:00:00`)
  if (Number.isNaN(startTimestamp)) return start
  const dayMs = 24 * 60 * 60 * 1000
  const endTimestamp = startTimestamp + (normalizedDayCount - 1) * dayMs
  const end = formatDateValue(endTimestamp)
  return end && end !== start ? `${start} 至 ${end}` : start
}

function parseStartDateFromTripTime(tripTime) {
  if (typeof tripTime !== 'string' || !tripTime.trim()) return null
  const matched = tripTime.trim().match(/^(\d{4}-\d{2}-\d{2})(?:\s*(?:至|~|-)\s*(\d{4}-\d{2}-\d{2}))?$/)
  if (!matched) return null
  const start = Date.parse(`${matched[1]}T00:00:00`)
  if (Number.isNaN(start)) return null
  return start
}

function getTripDayCountByPlaces(places = diaryPlaces.value) {
  if (!Array.isArray(places) || places.length === 0) return 1
  return places.reduce((maxDay, place) => {
    const routeDay = Number(place?.routeDay)
    if (!Number.isFinite(routeDay) || routeDay < 1) return maxDay
    return Math.max(maxDay, Math.floor(routeDay))
  }, 1)
}

function updateDiaryTripTimeInList(diaryId, tripTime) {
  const index = diaries.value.findIndex((item) => item.id === diaryId)
  if (index === -1) return
  diaries.value[index] = {
    ...diaries.value[index],
    trip_time: tripTime
  }
}

async function syncCurrentDiaryTripTimeByPlaces() {
  if (!currentDiary.value?.id) return
  const startDate = parseStartDateFromTripTime(currentDiary.value.trip_time)
  if (!Number.isFinite(Number(startDate))) return
  const nextTripTime = formatTripTimeByStartDate(startDate, getTripDayCountByPlaces())
  if (!nextTripTime || nextTripTime === currentDiary.value.trip_time) return

  const res = await apiCall({
    type: 'update_diary',
    diary_id: currentDiary.value.id,
    name: currentDiary.value.name,
    trip_time: nextTripTime,
    summary: currentDiary.value.summary || ''
  })
  if (res?.status !== '0') {
    message.error('同步出行时间失败，请稍后重试')
    return
  }

  currentDiary.value = {
    ...currentDiary.value,
    trip_time: nextTripTime
  }
  updateDiaryTripTimeInList(currentDiary.value.id, nextTripTime)
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
    return { description: '', images: [], routeDay: null, routeOrder: null }
  }
  try {
    const parsed = JSON.parse(note)
    const routeDayRaw = Number(parsed?.routeDay)
    const routeOrderRaw = Number(parsed?.routeOrder)
    return {
      description: typeof parsed?.description === 'string' ? parsed.description.trim() : '',
      images: normalizeImageUrls(parsed?.images),
      routeDay: Number.isFinite(routeDayRaw) && routeDayRaw >= 1 ? Math.floor(routeDayRaw) : null,
      routeOrder: Number.isFinite(routeOrderRaw) ? routeOrderRaw : null
    }
  } catch {
    return { description: note.trim(), images: [], routeDay: null, routeOrder: null }
  }
}

function normalizePlaces(rawPlaces) {
  if (!Array.isArray(rawPlaces)) return []
  const withMeta = rawPlaces.map((place, index) => {
    const extra = parsePlaceNote(place?.note)
    return {
      ...place,
      description: extra.description,
      images: extra.images,
      routeDay: extra.routeDay,
      routeOrder: extra.routeOrder ?? index
    }
  })
  return withMeta.map((place, index) => ({
    ...place,
    routeDay: Number.isFinite(place.routeDay) && place.routeDay >= 1 ? place.routeDay : 1,
    routeOrder: Number.isFinite(place.routeOrder) ? place.routeOrder : index
  }))
}

function buildPlaceNote(markerData) {
  const description = typeof markerData?.description === 'string'
    ? markerData.description.trim()
    : ''
  const images = normalizeImageUrls(markerData?.images)
  const routeDayRaw = Number(markerData?.routeDay)
  const routeOrderRaw = Number(markerData?.routeOrder)
  const routeDay = Number.isFinite(routeDayRaw) && routeDayRaw >= 1 ? Math.floor(routeDayRaw) : null
  const routeOrder = Number.isFinite(routeOrderRaw) ? routeOrderRaw : null
  if (!description && images.length === 0 && routeDay === null && routeOrder === null) return ''
  return JSON.stringify({
    description,
    images,
    routeDay,
    routeOrder
  })
}

function getNextRouteOrder(routeDay) {
  const targetDay = Number(routeDay)
  if (!Number.isFinite(targetDay) || targetDay < 1) return diaryPlaces.value.length
  const dayPlaces = diaryPlaces.value.filter((item) => Number(item.routeDay) === targetDay)
  if (dayPlaces.length === 0) return 0
  const maxOrder = Math.max(...dayPlaces.map((item, index) => Number.isFinite(Number(item.routeOrder)) ? Number(item.routeOrder) : index))
  return maxOrder + 1
}

async function apiCall(data) {
  try {
    return await ajax('/api/travel', data, 'POST')
  } catch (error) {
    const text = error?.message ? String(error.message) : '请求失败，请稍后重试'
    message.error(text)
    return null
  }
}

async function fetchDiaries() {
  if (loadingDiaries.value) return
  loadingDiaries.value = true
  const res = await apiCall({ type: 'get_diaries' })
  if (res?.status === '0') {
    diaries.value = Array.isArray(res.data) ? res.data : []
  } else {
    message.error('加载日记列表失败')
  }
  loadingDiaries.value = false
}

async function handleCreate() {
  if (creatingDiary.value) return false
  const name = newDiaryName.value.trim()
  const tripTime = formatTripTimeByStartDate(newDiaryStartDate.value)
  const summary = newDiarySummary.value.trim()
  if (!name) { message.warning('请输入日记名称'); return false }
  if (!tripTime) { message.warning('请选择开始日期'); return false }
  creatingDiary.value = true
  const res = await apiCall({ type: 'create_diary', name, trip_time: tripTime, summary })
  if (res?.status === '0') {
    await fetchDiaries()
    resetCreateForm()
    message.success('创建成功')
  } else {
    message.error('创建失败，请稍后重试')
  }
  creatingDiary.value = false
}

function resetCreateForm() {
  newDiaryName.value = ''
  newDiaryStartDate.value = null
  newDiarySummary.value = ''
  showCreateModal.value = false
}

function handleCancelCreate() {
  if (creatingDiary.value) return
  resetCreateForm()
}

function confirmDelete(diary) {
  if (!diary?.can_delete) {
    message.warning('仅创建者可删除日记')
    return
  }
  deletingDiary.value = diary
  showDeleteModal.value = true
}

async function startEdit(diary) {
  if (!diary) return
  const parsedStartDate = parseStartDateFromTripTime(diary?.trip_time)
  editingDiary.value = diary
  editingDiaryName.value = diary?.name || ''
  editingDiaryStartDate.value = parsedStartDate
  editingDiarySummary.value = diary?.summary || ''
  editingDiarySharers.value = []
  diaryShareCandidates.value = []
  if (diary?.can_manage_share) {
    const shareRes = await apiCall({ type: 'get_diary_sharers', diary_id: diary.id })
    if (shareRes?.status === '0') {
      const sharers = Array.isArray(shareRes?.data?.sharers) ? shareRes.data.sharers : []
      const candidates = Array.isArray(shareRes?.data?.candidates) ? shareRes.data.candidates : []
      editingDiarySharers.value = sharers
      diaryShareCandidates.value = candidates.map((username) => ({
        label: username,
        value: username
      }))
    } else {
      message.error('加载共享者失败，请稍后重试')
    }
  }
  showEditModal.value = true
}

function resetEditForm() {
  editingDiary.value = null
  editingDiaryName.value = ''
  editingDiaryStartDate.value = null
  editingDiarySummary.value = ''
  editingDiarySharers.value = []
  diaryShareCandidates.value = []
  showEditModal.value = false
}

function handleCancelEdit() {
  if (editingDiaryLoading.value) return
  resetEditForm()
}

async function handleEdit() {
  if (!editingDiary.value || editingDiaryLoading.value) return false
  const diaryId = editingDiary.value.id
  const name = editingDiaryName.value.trim()
  const tripTime = formatTripTimeByStartDate(editingDiaryStartDate.value)
  const summary = editingDiarySummary.value.trim()
  if (!name) {
    message.warning('请输入日记名称')
    return false
  }
  if (!tripTime) {
    message.warning('请选择开始日期')
    return false
  }
  editingDiaryLoading.value = true
  const res = await apiCall({
    type: 'update_diary',
    diary_id: editingDiary.value.id,
    name,
    trip_time: tripTime,
    summary
  })
  if (res?.status === '0') {
    if (editingDiary.value?.can_manage_share) {
      const shareRes = await apiCall({
        type: 'update_diary_sharers',
        diary_id: editingDiary.value.id,
        sharers: editingDiarySharers.value
      })
      if (shareRes?.status !== '0') {
        if (Array.isArray(shareRes?.invalid_users) && shareRes.invalid_users.length > 0) {
          message.error(`共享者不存在：${shareRes.invalid_users.join('、')}`)
        } else {
          message.error(shareRes?.message || '更新共享者失败，请稍后重试')
        }
        editingDiaryLoading.value = false
        return false
      }
    }
    if (currentDiary.value?.id === diaryId) {
      currentDiary.value = {
        ...currentDiary.value,
        name,
        trip_time: tripTime,
        summary
      }
    }
    await fetchDiaries()
    resetEditForm()
    message.success('已保存')
  } else {
    message.error('保存失败，请稍后重试')
  }
  editingDiaryLoading.value = false
}

async function handleDelete() {
  if (!deletingDiary.value || deletingDiaryLoading.value) return
  deletingDiaryLoading.value = true
  const res = await apiCall({ type: 'delete_diary', diary_id: deletingDiary.value.id })
  if (res?.status === '0') {
    await fetchDiaries()
    deletingDiary.value = null
    showDeleteModal.value = false
    message.success('已删除')
  } else {
    message.error('删除失败，请稍后重试')
  }
  deletingDiaryLoading.value = false
}

async function openDiary(diary) {
  if (openingDiary.value || loadingDiaryPlaces.value) return
  openingDiary.value = true
  loadingDiaryPlaces.value = true
  currentDiaryView.value = normalizeDiaryView(diary)
  lastSyncedDiaryView = currentDiaryView.value
  currentDiary.value = diary
  const res = await apiCall({ type: 'get_places', diary_id: diary.id })
  if (res?.status !== '0') {
    message.error('加载日记地点失败')
    closeDiary()
    loadingDiaryPlaces.value = false
    openingDiary.value = false
    return
  }
  diaryPlaces.value = normalizePlaces(res.data)
  currentDiaryView.value = res.view || currentDiaryView.value
  lastSyncedDiaryView = currentDiaryView.value
  await syncCurrentDiaryTripTimeByPlaces()
  loadingDiaryPlaces.value = false
  openingDiary.value = false
}

function closeDiary() {
  if (mapViewSyncTimer) {
    clearTimeout(mapViewSyncTimer)
    mapViewSyncTimer = null
  }
  pendingDiaryView = null
  viewSyncInFlight = false
  lastViewSyncAt = 0
  currentDiary.value = null
  currentDiaryView.value = null
  lastSyncedDiaryView = null
  loadingDiaryPlaces.value = false
  openingDiary.value = false
  placeActionLoading.value = false
  diaryPlaces.value = []
}

function handleMapViewChange(view) {
  const diaryId = currentDiary.value?.id
  if (!diaryId || !view) return
  if (!shouldSyncDiaryView(view, lastSyncedDiaryView)) return
  pendingDiaryView = view
  if (mapViewSyncTimer) clearTimeout(mapViewSyncTimer)
  mapViewSyncTimer = setTimeout(syncPendingDiaryView, 260)
}

async function syncPendingDiaryView() {
  mapViewSyncTimer = null
  const diaryId = currentDiary.value?.id
  const view = pendingDiaryView
  if (!diaryId || !view) return
  if (viewSyncInFlight) {
    mapViewSyncTimer = setTimeout(syncPendingDiaryView, 300)
    return
  }

  const now = Date.now()
  const remain = VIEW_SYNC_MIN_INTERVAL_MS - (now - lastViewSyncAt)
  if (remain > 0) {
    mapViewSyncTimer = setTimeout(syncPendingDiaryView, remain)
    return
  }

  pendingDiaryView = null
  viewSyncInFlight = true
  const res = await apiCall({
    type: 'update_diary_view',
    diary_id: diaryId,
    center: view.center,
    zoom: view.zoom
  })
  viewSyncInFlight = false

  if (res?.status === '0') {
    lastSyncedDiaryView = view
    lastViewSyncAt = Date.now()
  }

  if (pendingDiaryView) {
    mapViewSyncTimer = setTimeout(syncPendingDiaryView, 320)
  }
}

async function addPlaceToDiary(markerData) {
  if (!currentDiary.value || placeActionLoading.value) return
  placeActionLoading.value = true
  const routeDay = 1
  const routeOrder = getNextRouteOrder(routeDay)
  const place = {
    poi_id: markerData.id || '',
    name: markerData.name || '',
    address: markerData.address || '',
    lng: markerData.location?.lng || 0,
    lat: markerData.location?.lat || 0,
    tel: markerData.tel || '',
    type: markerData.type || '',
    typecode: markerData.typecode || '',
    note: buildPlaceNote({ ...markerData, routeDay, routeOrder })
  }
  const res = await apiCall({ type: 'add_place', diary_id: currentDiary.value.id, place })
  if (res?.status === '0') {
    const placesRes = await apiCall({ type: 'get_places', diary_id: currentDiary.value.id })
    if (placesRes?.status === '0') {
      diaryPlaces.value = normalizePlaces(placesRes.data)
      await syncCurrentDiaryTripTimeByPlaces()
    }
    message.success('已添加到日记')
  } else {
    message.error('添加地点失败')
  }
  placeActionLoading.value = false
}

async function removePlaceFromDiary(placeId) {
  if (!currentDiary.value || placeActionLoading.value) return
  placeActionLoading.value = true
  const res = await apiCall({ type: 'delete_place', diary_id: currentDiary.value.id, place_id: placeId })
  if (res?.status === '0') {
    diaryPlaces.value = diaryPlaces.value.filter(p => p.id !== placeId)
    await syncCurrentDiaryTripTimeByPlaces()
    message.success('已移除')
  } else {
    message.error('移除地点失败')
  }
  placeActionLoading.value = false
}

async function updatePlaceType(placeId, typecode) {
  if (!currentDiary.value || placeActionLoading.value) return
  placeActionLoading.value = true
  const res = await apiCall({
    type: 'update_place_typecode',
    diary_id: currentDiary.value.id,
    place_id: placeId,
    typecode
  })
  if (res?.status === '0') {
    const place = diaryPlaces.value.find(p => p.id === placeId)
    if (place) place.typecode = typecode
  } else {
    message.error('更新地点图标失败')
  }
  placeActionLoading.value = false
}

async function updatePlaceDescription(payload) {
  if (!currentDiary.value || placeActionLoading.value) return
  const placeId = Number(payload?.placeId)
  if (!Number.isFinite(placeId)) return
  const place = diaryPlaces.value.find((item) => item.id === placeId)
  if (!place) return
  placeActionLoading.value = true
  const description = typeof payload?.description === 'string'
    ? payload.description.trim()
    : ''
  const note = buildPlaceNote({
    description,
    images: place.images,
    routeDay: place.routeDay,
    routeOrder: place.routeOrder
  })
  const res = await apiCall({
    type: 'update_place_note',
    diary_id: currentDiary.value.id,
    place_id: placeId,
    note
  })
  if (res?.status === '0') {
    place.description = description
    place.note = note
    message.success('简介已保存')
  } else {
    message.error('保存简介失败')
  }
  placeActionLoading.value = false
}

async function updateRoutePlan(payload) {
  if (!currentDiary.value || placeActionLoading.value) return
  const items = Array.isArray(payload?.items) ? payload.items : []
  if (items.length === 0) return

  const updates = items
    .map((item) => {
      const placeId = Number(item?.placeId)
      const routeDay = Number(item?.routeDay)
      const routeOrder = Number(item?.routeOrder)
      if (!Number.isFinite(placeId) || !Number.isFinite(routeDay) || routeDay < 1 || !Number.isFinite(routeOrder)) {
        return null
      }
      const place = diaryPlaces.value.find((entry) => entry.id === placeId)
      if (!place) return null
      if (Number(place.routeDay) === Math.floor(routeDay) && Number(place.routeOrder) === routeOrder) {
        return null
      }
      const nextRouteDay = Math.floor(routeDay)
      const nextRouteOrder = Number(routeOrder)
      const note = buildPlaceNote({
        description: place.description,
        images: place.images,
        routeDay: nextRouteDay,
        routeOrder: nextRouteOrder
      })
      return {
        place,
        placeId,
        routeDay: nextRouteDay,
        routeOrder: nextRouteOrder,
        note
      }
    })
    .filter(Boolean)

  if (updates.length === 0) return
  placeActionLoading.value = true

  let hasFailed = false
  for (const update of updates) {
    const res = await apiCall({
      type: 'update_place_note',
      diary_id: currentDiary.value.id,
      place_id: update.placeId,
      note: update.note
    })
    if (res?.status !== '0') {
      hasFailed = true
      break
    }
  }

  if (hasFailed) {
    message.error('保存路线失败，请稍后重试')
    const placesRes = await apiCall({ type: 'get_places', diary_id: currentDiary.value.id })
    if (placesRes?.status === '0') {
      diaryPlaces.value = normalizePlaces(placesRes.data)
    }
  } else {
    updates.forEach((update) => {
      update.place.routeDay = update.routeDay
      update.place.routeOrder = update.routeOrder
      update.place.note = update.note
    })
    await syncCurrentDiaryTripTimeByPlaces()
  }

  placeActionLoading.value = false
}

onMounted(() => {
  fetchDiaries()
})

onUnmounted(() => {
  if (mapViewSyncTimer) {
    clearTimeout(mapViewSyncTimer)
    mapViewSyncTimer = null
  }
  pendingDiaryView = null
  viewSyncInFlight = false
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

.create-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  transform: none;
  box-shadow: none;
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
  flex-direction: column;
  align-items: flex-start;
  gap: 2px;
  margin-top: 4px;
}

.diary-meta-row {
  display: flex;
  align-items: center;
  gap: 10px;
}

.diary-time {
  font-size: 12px;
  color: var(--color-text-sub-sub);
}

.diary-trip-time {
  font-size: 12px;
  color: var(--color-text-sub);
}

.diary-access {
  font-size: 12px;
  color: var(--color-text-sub-sub);
}

.diary-summary {
  margin-top: 8px;
  font-size: 13px;
  color: var(--color-text-sub);
  display: -webkit-box;
  line-clamp: 2;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
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

.edit-btn {
  background: none;
  border: none;
  color: var(--color-text-sub-sub);
  cursor: pointer;
  padding: 6px;
  border-radius: 6px;
  transition: color 0.2s ease, background 0.2s ease;
  opacity: 0;
}

.diary-item:hover .delete-btn,
.diary-item:hover .edit-btn {
  opacity: 1;
}

.edit-btn:hover {
  color: var(--color-text);
  background: var(--color-light-light);
}

.delete-btn:hover {
  color: #e74c3c;
  background: rgba(231, 76, 60, 0.08);
}

/* 地图视图 */
.map-view {
  position: relative;
  width: 100%;
  height: 100dvh;
}

.map-view-spin {
  display: block;
  width: 100%;
  height: 100%;
}

.map-view-spin :deep(.n-spin-container),
.map-view-spin :deep(.n-spin-content) {
  width: 100%;
  height: 100%;
}

.create-form {
  display: flex;
  flex-direction: column;
  gap: 12px;
}
</style>

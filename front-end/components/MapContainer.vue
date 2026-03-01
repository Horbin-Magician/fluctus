<template>
  <div class="map-container">
    <div id="amap"/>

    <MapSidebar
      ref="sidebarRef"
      :sidebar-open="sidebarOpen"
      :diary-name="diaryName"
      :diary-trip-time="diaryTripTime"
      :diary-summary="diarySummary"
      :search-keyword="searchKeyword"
      :search-results="searchResults"
      :show-places="showPlaces"
      :places="places"
      :display-days="displayDays"
      :get-places-by-day="getPlacesByDay"
      :drag-over-day="dragOverDay"
      :dragging-place-id="draggingPlaceId"
      :is-drop-indicator="isDropIndicator"
      :get-adjacent-driving-text="getAdjacentDrivingText"
      :get-place-subtitle="getPlaceSubtitle"
      @back="_emit('back')"
      @edit-diary="_emit('edit-diary')"
      @toggle-sidebar="toggleSidebar"
      @update:search-keyword="onSearchKeywordUpdate"
      @keyword-input="handleKeywordInput"
      @search-blur="handleSearchBlur"
      @search="handleSearch"
      @suggestion-mousedown="beginSuggestionSelection"
      @select-search-result="selectSearchResult"
      @toggle-places="showPlaces = !showPlaces"
      @day-dragover="onDayDragOver"
      @day-drop="onDayDrop"
      @place-dragstart="onPlaceDragStart"
      @place-dragend="onPlaceDragEnd"
      @place-dragover="onPlaceDragOver"
      @place-drop="onPlaceDrop"
      @route-leg-dragover="onRouteLegDragOver"
      @route-leg-drop="onRouteLegDrop"
      @add-route-day="addRouteDay"
      @remove-place="_emit('remove-place', $event)"
      @go-to-place="goToPlace"
    />

    <MapSidebarToggleButton
      :sidebar-open="sidebarOpen"
      @toggle-sidebar="toggleSidebar"
    />

    <MapMarkerInfoPanel
      :selected-marker="selectedMarker"
      :is-editing-description="isEditingDescription"
      :description-draft="descriptionDraft"
      :marker-type-options="markerTypeOptions"
      :is-place-in-diary="isPlaceInDiary"
      :get-place-typecode="getPlaceTypecode"
      :get-place-db-id="getPlaceDbId"
      @close="closeMarkerInfo"
      @start-description-edit="startDescriptionEdit"
      @cancel-description-edit="cancelDescriptionEdit"
      @save-description-edit="saveDescriptionEdit"
      @update:description-draft="descriptionDraft = $event"
      @update-place-type="(placeId, typecode) => _emit('update-place-type', placeId, typecode)"
      @add-place="_emit('add-place', $event)"
      @remove-place="_emit('remove-place', $event)"
    />
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
  Location as LocationIcon
} from "@vicons/ionicons5";
import { preloadAmap } from '@/utils/amapLoader';
import MapSidebar from '@/components/map/MapSidebar.vue';
import MapMarkerInfoPanel from '@/components/map/MapMarkerInfoPanel.vue';
import MapSidebarToggleButton from '@/components/map/MapSidebarToggleButton.vue';

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
const sidebarRef = ref(null);
const localPlaces = ref([]);
const draggingPlaceId = ref(null);
const dragOverDay = ref(null);
const dropIndicator = ref({ day: null, placeId: null, position: '' });
const manualDayCount = ref(1);
const DROP_INDICATOR_DEADZONE_PX = 14;
const DROP_DAY_APPEND_TRIGGER_PX = 18;

let map = null;
let AMap = null;
let placeSearchGlobal = null;
let placeSearchNearby = null;
let autoComplete = null;
let autocompleteTimer = null;
let autocompleteRequestVersion = 0;
let searchRequestVersion = 0;
let suggestionSelectionTimer = null;
let isSelectingSuggestion = false;
let drivingService = null;
let drivingRouteRequestVersion = 0;
const mapReady = ref(false);
const searchMarkers = [];
const diaryMarkers = [];
const adjacentDrivingInfo = ref({});
const adjacentDrivingLoading = ref({});

const hasValidView = (view) => {
  const center = view?.center;
  const zoom = view?.zoom;
  return Array.isArray(center)
    && center.length === 2
    && Number.isFinite(center[0])
    && Number.isFinite(center[1])
    && Number.isFinite(zoom);
};

const getPlaceSubtitle = (place) => {
  const description = typeof place?.description === 'string' ? place.description.trim() : '';
  if (description) return description;
  return place?.address || '';
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

const getPlaceTimestamp = (place) => {
  if (!place) return Number.NEGATIVE_INFINITY;
  const createdAt = typeof place.created_at === 'string' ? Date.parse(place.created_at.replace(' ', 'T')) : Number.NaN;
  if (Number.isFinite(createdAt)) return createdAt;
  const id = Number(place.id);
  return Number.isFinite(id) ? id : Number.NEGATIVE_INFINITY;
};

const getLastAddedPlaceAnchor = () => {
  if (!Array.isArray(routePlaces.value) || routePlaces.value.length === 0) return null;
  const latestPlace = routePlaces.value.reduce((latest, place) => {
    if (!latest) return place;
    return getPlaceTimestamp(place) > getPlaceTimestamp(latest) ? place : latest;
  }, null);
  if (!latestPlace) return null;
  const lng = Number(latestPlace.lng);
  const lat = Number(latestPlace.lat);
  if (!Number.isFinite(lng) || !Number.isFinite(lat)) return null;
  return { lng, lat };
};

const toRadians = (value) => value * Math.PI / 180;

const getDistanceMeters = (locationA, locationB) => {
  if (!locationA || !locationB) return Number.POSITIVE_INFINITY;

  const parsePoint = (location) => {
    if (!location) return null;
    if (typeof location.lng === 'number' && typeof location.lat === 'number') {
      return { lng: location.lng, lat: location.lat };
    }
    if (typeof location.getLng === 'function' && typeof location.getLat === 'function') {
      return { lng: location.getLng(), lat: location.getLat() };
    }
    return null;
  };

  const pointA = parsePoint(locationA);
  const pointB = parsePoint(locationB);
  if (!pointA || !pointB) return Number.POSITIVE_INFINITY;

  const lng1 = Number(pointA.lng);
  const lat1 = Number(pointA.lat);
  const lng2 = Number(pointB.lng);
  const lat2 = Number(pointB.lat);
  if (![lng1, lat1, lng2, lat2].every(Number.isFinite)) return Number.POSITIVE_INFINITY;
  const earthRadius = 6371000;
  const dLat = toRadians(lat2 - lat1);
  const dLng = toRadians(lng2 - lng1);
  const a = Math.sin(dLat / 2) ** 2
    + Math.cos(toRadians(lat1)) * Math.cos(toRadians(lat2)) * Math.sin(dLng / 2) ** 2;
  const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
  return earthRadius * c;
};

const prioritizeResultsByLastAddedPlace = (results) => {
  if (!Array.isArray(results) || results.length <= 1) return Array.isArray(results) ? results : [];
  const anchor = getLastAddedPlaceAnchor();
  if (!anchor) return [...results];
  return [...results].sort((a, b) => {
    const distanceA = getDistanceMeters(a?.location, anchor);
    const distanceB = getDistanceMeters(b?.location, anchor);
    if (distanceA === distanceB) return 0;
    if (!Number.isFinite(distanceA)) return 1;
    if (!Number.isFinite(distanceB)) return -1;
    return distanceA - distanceB;
  });
};

const mapPoiToSearchResult = (poi) => ({
  id: poi.id,
  name: poi.name,
  address: poi.address || '',
  location: normalizeLocation(poi.location),
  tel: poi.tel || '',
  type: poi.type || '',
  typecode: poi.typecode || '',
  description: getPlaceDescription(poi),
  images: normalizeImages(poi.photos || poi.images)
});

const getPoiMergeKey = (poi) => {
  if (!poi) return '';
  if (poi.id) return `id:${poi.id}`;
  return `na:${poi.name || ''}:${poi.address || ''}`;
};

const mergeNearbyFirstPois = (nearbyPois, globalPois) => {
  const merged = [];
  const exists = new Set();
  [...nearbyPois, ...globalPois].forEach((poi) => {
    const key = getPoiMergeKey(poi);
    if (!key || exists.has(key)) return;
    exists.add(key);
    merged.push(poi);
  });
  return merged;
};

const applyPoiResults = (pois) => {
  clearSearchMarkers();
  searchResults.value = [];
  if (!Array.isArray(pois) || pois.length === 0) return;
  const mapped = pois.map(mapPoiToSearchResult);
  searchResults.value = prioritizeResultsByLastAddedPlace(mapped);
  addSearchMarkers(searchResults.value);
};

const searchPoisByKeyword = (keyword) => {
  return new Promise((resolve) => {
    if (!placeSearchGlobal || !keyword) {
      resolve([]);
      return;
    }
    placeSearchGlobal.search(keyword, (status, result) => {
      if (status !== 'complete' || !result?.poiList?.pois?.length) {
        resolve([]);
        return;
      }
      resolve(result.poiList.pois);
    });
  });
};

const searchNearbyPois = (keyword, anchor, radius = 30000) => {
  return new Promise((resolve) => {
    if (!placeSearchNearby || !keyword || !anchor || typeof placeSearchNearby.searchNearBy !== 'function') {
      resolve([]);
      return;
    }
    placeSearchNearby.searchNearBy(keyword, [anchor.lng, anchor.lat], radius, (status, result) => {
      if (status !== 'complete' || !result?.poiList?.pois?.length) {
        resolve([]);
        return;
      }
      resolve(result.poiList.pois);
    });
  });
};

const searchTipsByKeyword = (keyword) => {
  return new Promise((resolve) => {
    if (!autoComplete || !keyword) {
      resolve([]);
      return;
    }
    autoComplete.search(keyword, (status, result) => {
      if (status !== 'complete' || !result?.tips?.length) {
        resolve([]);
        return;
      }
      const tips = result.tips
        .filter((tip) => tip?.name)
        .map((tip) => ({
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
      resolve(tips);
    });
  });
};

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
  placeSearchGlobal = new AMap.PlaceSearch({
    pageSize: 10, city: "全国", citylimit: false, panel: false
  });
  placeSearchNearby = new AMap.PlaceSearch({
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
    const section = sidebarRef.value?.getSearchSectionElement?.() || null;
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
  const section = sidebarRef.value?.getSearchSectionElement?.() || null;
  if (!section) return;
  const target = event.target;
  if (target instanceof Node && section.contains(target)) return;
  clearSearchMarkers();
};

const onSearchKeywordUpdate = (keyword) => {
  searchKeyword.value = keyword;
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

const handleAutocomplete = async (keyword) => {
  const requestVersion = autocompleteRequestVersion + 1;
  autocompleteRequestVersion = requestVersion;
  if (!keyword) return;

  const globalTips = await searchTipsByKeyword(keyword);
  if (requestVersion !== autocompleteRequestVersion) return;

  const anchor = getLastAddedPlaceAnchor();
  if (anchor) {
    const nearbyPois = await searchNearbyPois(keyword, anchor, 30000);
    if (requestVersion !== autocompleteRequestVersion) return;
    const nearbySuggestions = Array.isArray(nearbyPois)
      ? nearbyPois.slice(0, 8).map(mapPoiToSearchResult)
      : [];
    const mergedSuggestions = mergeNearbyFirstPois(nearbySuggestions, globalTips);
    if (mergedSuggestions.length > 0) {
      searchResults.value = prioritizeResultsByLastAddedPlace(mergedSuggestions);
      return;
    }
    handleSuggestionFallback(keyword);
    return;
  }

  if (globalTips.length > 0) {
    searchResults.value = prioritizeResultsByLastAddedPlace(globalTips);
    return;
  }
  handleSuggestionFallback(keyword);
};

const handleSuggestionFallback = (keyword) => {
  if (!placeSearchGlobal || !keyword) {
    searchResults.value = [];
    return;
  }
  placeSearchGlobal.search(keyword, (status, result) => {
    if (status !== 'complete' || !result?.poiList?.pois?.length) {
      searchResults.value = [];
      return;
    }
    const fallbackResults = result.poiList.pois.slice(0, 8).map(mapPoiToSearchResult);
    searchResults.value = prioritizeResultsByLastAddedPlace(fallbackResults);
  });
};

const normalizeLocation = (location) => {
  if (!location) return null;
  if (Array.isArray(location) && location.length >= 2) {
    const lng = Number(location[0]);
    const lat = Number(location[1]);
    if (Number.isFinite(lng) && Number.isFinite(lat)) {
      return { lng, lat };
    }
  }
  if (typeof location === 'string') {
    const parts = location.split(',').map((item) => Number(item.trim()));
    if (parts.length >= 2 && Number.isFinite(parts[0]) && Number.isFinite(parts[1])) {
      return { lng: parts[0], lat: parts[1] };
    }
  }
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

const handleSearch = async () => {
  if (!searchKeyword.value.trim()) return;
  const requestVersion = searchRequestVersion + 1;
  searchRequestVersion = requestVersion;
  const keyword = searchKeyword.value.trim();
  const anchor = getLastAddedPlaceAnchor();
  const nearbyPois = anchor ? await searchNearbyPois(keyword, anchor) : [];
  if (requestVersion !== searchRequestVersion) return;
  const globalPois = await searchPoisByKeyword(keyword);
  if (requestVersion !== searchRequestVersion) return;
  const mergedPois = mergeNearbyFirstPois(nearbyPois, globalPois);
  applyPoiResults(mergedPois);
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

const getPlaceCoordinate = (place) => {
  const lng = Number(place?.lng);
  const lat = Number(place?.lat);
  if (!Number.isFinite(lng) || !Number.isFinite(lat)) return null;
  return [lng, lat];
};

const buildAdjacentDrivingKey = (day, fromPlace, toPlace) => {
  const fromId = Number.isFinite(Number(fromPlace?.id)) ? Number(fromPlace.id) : String(fromPlace?.poi_id || fromPlace?.name || 'from');
  const toId = Number.isFinite(Number(toPlace?.id)) ? Number(toPlace.id) : String(toPlace?.poi_id || toPlace?.name || 'to');
  return `${Number(day)}:${fromId}->${toId}`;
};

const formatDrivingDuration = (seconds) => {
  const totalSeconds = Number(seconds);
  if (!Number.isFinite(totalSeconds) || totalSeconds <= 0) return '未知';
  const minutes = Math.max(1, Math.round(totalSeconds / 60));
  if (minutes < 60) return `${minutes} 分钟`;
  const hours = Math.floor(minutes / 60);
  const remainMinutes = minutes % 60;
  if (remainMinutes === 0) return `${hours} 小时`;
  return `${hours} 小时 ${remainMinutes} 分钟`;
};

const formatDrivingDistance = (meters) => {
  const totalMeters = Number(meters);
  if (!Number.isFinite(totalMeters) || totalMeters <= 0) return '';
  if (totalMeters < 1000) return `${Math.round(totalMeters)} 米`;
  const kilometers = totalMeters / 1000;
  const text = kilometers >= 100 ? kilometers.toFixed(0) : kilometers.toFixed(1);
  return `${text} 公里`;
};

const getAdjacentDrivingText = (day, index) => {
  const dayPlaces = getPlacesByDay(day);
  const fromPlace = dayPlaces[index];
  const toPlace = dayPlaces[index + 1];
  if (!fromPlace || !toPlace) return '';
  const key = buildAdjacentDrivingKey(day, fromPlace, toPlace);
  if (adjacentDrivingLoading.value[key]) return '车程计算中...';
  const detail = adjacentDrivingInfo.value[key];
  if (!detail) return '车程暂无数据';
  const durationText = formatDrivingDuration(detail.duration);
  const distanceText = formatDrivingDistance(detail.distance);
  return distanceText ? `车程约 ${durationText} · ${distanceText}` : `车程约 ${durationText}`;
};

const ensureDrivingService = () => {
  if (drivingService || !AMap) return Promise.resolve(drivingService);
  return new Promise((resolve) => {
    AMap.plugin('AMap.Driving', () => {
      drivingService = new AMap.Driving({
        policy: AMap.DrivingPolicy?.LEAST_TIME,
      });
      resolve(drivingService);
    });
  });
};

const queryAdjacentDrivingDetail = async (fromPlace, toPlace) => {
  const service = await ensureDrivingService();
  const fromCoordinate = getPlaceCoordinate(fromPlace);
  const toCoordinate = getPlaceCoordinate(toPlace);
  if (!service || !fromCoordinate || !toCoordinate) return null;
  return new Promise((resolve) => {
    service.search(fromCoordinate, toCoordinate, (status, result) => {
      if (status !== 'complete') {
        resolve(null);
        return;
      }
      const route = result?.routes?.[0];
      const duration = Number(route?.time);
      const distance = Number(route?.distance);
      if (!Number.isFinite(duration)) {
        resolve(null);
        return;
      }
      resolve({ duration, distance: Number.isFinite(distance) ? distance : 0 });
    });
  });
};

const refreshAdjacentDrivingInfo = async () => {
  const routePairs = [];
  const currentKeys = new Set();

  displayDays.value.forEach((day) => {
    const dayPlaces = getPlacesByDay(day);
    for (let index = 0; index < dayPlaces.length - 1; index += 1) {
      const fromPlace = dayPlaces[index];
      const toPlace = dayPlaces[index + 1];
      const key = buildAdjacentDrivingKey(day, fromPlace, toPlace);
      currentKeys.add(key);
      routePairs.push({ key, fromPlace, toPlace });
    }
  });

  if (routePairs.length === 0) {
    adjacentDrivingInfo.value = {};
    adjacentDrivingLoading.value = {};
    return;
  }

  adjacentDrivingInfo.value = Object.fromEntries(
    Object.entries(adjacentDrivingInfo.value).filter(([key]) => currentKeys.has(key))
  );
  adjacentDrivingLoading.value = Object.fromEntries(
    Object.entries(adjacentDrivingLoading.value).filter(([key]) => currentKeys.has(key))
  );

  const requestVersion = drivingRouteRequestVersion + 1;
  drivingRouteRequestVersion = requestVersion;

  for (const pair of routePairs) {
    if (adjacentDrivingInfo.value[pair.key]) continue;
    adjacentDrivingLoading.value = {
      ...adjacentDrivingLoading.value,
      [pair.key]: true,
    };
    const detail = await queryAdjacentDrivingDetail(pair.fromPlace, pair.toPlace);
    if (requestVersion !== drivingRouteRequestVersion) return;
    const { [pair.key]: _removed, ...nextLoading } = adjacentDrivingLoading.value;
    adjacentDrivingLoading.value = nextLoading;
    if (detail) {
      adjacentDrivingInfo.value = {
        ...adjacentDrivingInfo.value,
        [pair.key]: detail,
      };
    }
  }
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
  dropIndicator.value = { day: null, placeId: null, position: '' };
};

const onDayDragOver = (day, event) => {
  if (!draggingPlaceId.value) return;
  dragOverDay.value = day;

  const dayPlaces = getPlacesByDay(day);
  if (dayPlaces.length === 0) {
    dropIndicator.value = { day, placeId: null, position: 'end' };
    return;
  }

  const container = event?.currentTarget;
  if (!(container instanceof HTMLElement)) {
    dropIndicator.value = { day, placeId: dayPlaces[dayPlaces.length - 1].id, position: 'after' };
    return;
  }

  const itemElements = Array.from(container.querySelectorAll('.favorite-item'));
  if (itemElements.length === 0) {
    dropIndicator.value = { day, placeId: null, position: 'end' };
    return;
  }

  const y = event.clientY;
  const firstRect = itemElements[0].getBoundingClientRect();
  const lastRect = itemElements[itemElements.length - 1].getBoundingClientRect();

  if (y < firstRect.top) {
    dropIndicator.value = { day, placeId: dayPlaces[0].id, position: 'before' };
    return;
  }

  if (y > lastRect.bottom + DROP_DAY_APPEND_TRIGGER_PX) {
    dropIndicator.value = { day, placeId: null, position: 'end' };
    return;
  }

  for (let index = 0; index < itemElements.length; index += 1) {
    const rect = itemElements[index].getBoundingClientRect();
    const midpoint = rect.top + rect.height / 2;
    if (y <= midpoint) {
      dropIndicator.value = { day, placeId: dayPlaces[index].id, position: 'before' };
      return;
    }
  }

  dropIndicator.value = { day, placeId: dayPlaces[dayPlaces.length - 1].id, position: 'after' };
};

const onDayDrop = (targetDay) => {
  if (!draggingPlaceId.value) return;
  const preview = dropIndicator.value;
  if (preview.day === targetDay && preview.placeId) {
    onPlaceDrop(targetDay, preview.placeId);
    return;
  }

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

const onPlaceDragOver = (day, targetPlaceId, event) => {
  if (!draggingPlaceId.value) return;
  dragOverDay.value = day;
  const target = event?.currentTarget;
  if (!(target instanceof HTMLElement)) {
    dropIndicator.value = { day, placeId: targetPlaceId, position: 'before' };
    return;
  }
  const rect = target.getBoundingClientRect();
  const middleY = rect.top + rect.height / 2;
  const distanceToMiddle = event.clientY - middleY;
  const absDistance = Math.abs(distanceToMiddle);
  const lastIndicator = dropIndicator.value;

  let position = distanceToMiddle > 0 ? 'after' : 'before';
  const isSameTarget = lastIndicator.day === day && lastIndicator.placeId === targetPlaceId;
  if (isSameTarget && absDistance <= DROP_INDICATOR_DEADZONE_PX && (lastIndicator.position === 'before' || lastIndicator.position === 'after')) {
    position = lastIndicator.position;
  }
  dropIndicator.value = { day, placeId: targetPlaceId, position };
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
  let insertAt = insertIndex >= 0 ? insertIndex : targetDayPlaces.length;
  const preview = dropIndicator.value;
  if (
    preview.day === targetDay
    && preview.placeId === targetPlaceId
    && preview.position === 'after'
    && insertAt < targetDayPlaces.length
  ) {
    insertAt += 1;
  }
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

const onRouteLegDragOver = (day, index) => {
  if (!draggingPlaceId.value) return;
  dragOverDay.value = day;
  const dayPlaces = getPlacesByDay(day);
  const previousPlace = dayPlaces[index];
  if (!previousPlace?.id) {
    dropIndicator.value = { day, placeId: null, position: 'end' };
    return;
  }
  dropIndicator.value = { day, placeId: previousPlace.id, position: 'after' };
};

const onRouteLegDrop = (day, index) => {
  if (!draggingPlaceId.value) return;
  const dayPlaces = getPlacesByDay(day);
  const previousPlace = dayPlaces[index];
  if (!previousPlace?.id) {
    onDayDrop(day);
    return;
  }
  dropIndicator.value = { day, placeId: previousPlace.id, position: 'after' };
  onPlaceDrop(day, previousPlace.id);
};

const isDropIndicator = (day, placeId, position) => {
  if (!draggingPlaceId.value) return false;
  return dropIndicator.value.day === day
    && dropIndicator.value.placeId === placeId
    && dropIndicator.value.position === position;
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

watch([routePlaces, mapReady], () => {
  if (!mapReady.value) return;
  refreshAdjacentDrivingInfo();
}, { deep: true, immediate: true });

watch(() => props.initialView, () => {
  if (!mapReady.value) return;
  applyInitialView();
}, { deep: true });

onUnmounted(() => {
  drivingRouteRequestVersion += 1;
  autocompleteRequestVersion += 1;
  searchRequestVersion += 1;
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
</style>

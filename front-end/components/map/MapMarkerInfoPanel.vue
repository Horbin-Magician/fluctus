<template>
  <div v-if="selectedMarker" class="marker-info-panel">
    <div class="marker-info-header">
      <h3>{{ selectedMarker.name }}</h3>
      <button class="close-btn" @click="$emit('close')">×</button>
    </div>
    <div class="marker-info-content">
      <p><strong>地址:</strong> {{ selectedMarker.address }}</p>
      <p v-if="selectedMarker.tel"><strong>电话:</strong> {{ selectedMarker.tel }}</p>
      <p v-if="selectedMarker.type"><strong>类型:</strong> {{ selectedMarker.type }}</p>
      <p
        v-if="!isEditingDescription"
        :class="isPlaceInDiary(selectedMarker) ? 'marker-description-editable' : (selectedMarker.description ? '' : 'marker-description-empty')"
        @click="isPlaceInDiary(selectedMarker) ? $emit('start-description-edit') : null"
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
            :value="descriptionDraft"
            class="marker-description-input"
            rows="3"
            maxlength="500"
            placeholder="输入你对这个地点的简介或备注"
            @input="$emit('update:description-draft', $event.target.value)"
          />
          <div class="marker-description-count">{{ descriptionDraft.length }}/500</div>
          <div class="marker-description-actions">
            <button class="marker-description-btn subtle" @click="$emit('cancel-description-edit')">取消</button>
            <button class="marker-description-btn primary" @click="$emit('save-description-edit')">保存</button>
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
</template>

<script setup>
defineProps({
  selectedMarker: { type: Object, default: null },
  isEditingDescription: { type: Boolean, default: false },
  descriptionDraft: { type: String, default: '' },
  markerTypeOptions: { type: Array, default: () => [] },
  isPlaceInDiary: { type: Function, required: true },
  getPlaceTypecode: { type: Function, required: true },
  getPlaceDbId: { type: Function, required: true },
})

defineEmits([
  'close',
  'start-description-edit',
  'cancel-description-edit',
  'save-description-edit',
  'update:description-draft',
  'update-place-type',
  'add-place',
  'remove-place',
])
</script>

<style scoped>
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

.marker-info-header h3 {
  margin: 0;
  font-size: 16px;
  color: var(--color-text);
}

.close-btn {
  background: none;
  border: none;
  font-size: 20px;
  cursor: pointer;
  color: var(--color-text-sub-sub);
}

.marker-info-content {
  padding: 16px;
}

.marker-info-content p {
  margin: 6px 0;
  font-size: 13px;
  color: var(--color-text-sub);
}

.marker-actions {
  margin-top: 12px;
  display: flex;
  gap: 8px;
}

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

.action-btn:hover {
  background: var(--color-light-light);
}

.action-btn.active {
  background: var(--color-primary);
  color: var(--color-background);
  border-color: var(--color-primary);
}

.marker-type-section {
  margin-top: 10px;
}

.marker-type-label {
  margin-bottom: 6px !important;
}

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
  .marker-info-panel {
    width: calc(100% - 40px);
    left: 20px;
    right: 20px;
    top: auto;
    bottom: 20px;
  }
}
</style>

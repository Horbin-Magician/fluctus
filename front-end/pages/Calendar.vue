<!-- 日历页 Calendar -->
<template>
  <div class="container">
    <div class="calendar-card">
      <!-- 头部 -->
      <header class="header">
        <div class="header-left">
          <div class="date-btn" title="选择年份" @click="openYearPicker">
            <span class="data-text">{{ show_date.getFullYear() }}</span>
            <svg class="edit-icon" viewBox="0 0 24 24"><path d="M7 10l5 5 5-5z"/></svg>
          </div>
          <div class="date-btn" title="选择月份" @click="openMonthPicker">
            <span class="data-text">{{ show_date.getMonth() + 1 }}月</span>
            <svg class="edit-icon" viewBox="0 0 24 24"><path d="M7 10l5 5 5-5z"/></svg>
          </div>
        </div>
        
        <div class="header-controls">
          <button class="icon-btn" title="上个月" @click="navigateMonth(-1)">
            <svg viewBox="0 0 24 24"><path d="M15.41 7.41L14 6l-6 6 6 6 1.41-1.41L10.83 12z"/></svg>
          </button>
          <button class="icon-btn" title="今天" @click="show_date = new Date()">
            <svg viewBox="0 0 24 24"><path d="M19 3h-1V1h-2v2H8V1H6v2H5c-1.11 0-2.9.9-2 2v14c0 1.1.89 2 2 2h14c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2zm0 16H5V8h14v11z"/></svg>
          </button>
          <button class="icon-btn" title="下个月" @click="navigateMonth(1)">
            <svg viewBox="0 0 24 24"><path d="M10 6L8.59 7.41 13.17 12l-4.58 4.59L10 18l6-6z"/></svg>
          </button>
        </div>
      </header>

      <!-- 星期 -->
      <div class="weekdays-row">
        <span v-for="week in weeks" :key="week" class="weekday-cell">{{ week }}</span>
      </div>

      <!-- 日期网格 -->
      <div class="days-grid">
        <div 
          v-for="(week, i) in monthData" 
          :key="i"
          class="week-row"
        >
          <div 
            v-for="dayInfo in week" 
            :key="`${dayInfo.fullYear}-${dayInfo.month}-${dayInfo.day}`"
            :class="getCellClass(dayInfo)"
            @click="onDateClick(dayInfo)"
          >
            <div class="day-content">
              <div class="day-top">
                <span class="day-num">{{ dayInfo.day }}</span>
                <div class="moon-phase" title="月相">
                   <div class="moon_mask" :style="getMoonPhaseOffset(dayInfo)" />
                </div>
              </div>
              
              <div class="day-bottom">
                <span 
                  class="lunar-text"
                  :class="`type-${getDayDisplayInfo(dayInfo).type}`"
                >
                  {{ getDayDisplayInfo(dayInfo).text }}
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Date Picker Modal -->
      <div v-if="isDatePickerOpen" class="date-picker-modal" @click.self="closeDatePicker">
        <div class="date-picker-content">
          <div class="picker-header">{{ pickerMode === 'year' ? '选择年份' : '选择月份' }}</div>
          
          <div class="picker-body">
            <!-- Year Picker -->
            <div v-if="pickerMode === 'year'" class="year-picker-container">
              <div class="year-nav">
                <button class="icon-btn small" @click="changeYearRange(-1)">
                   <svg viewBox="0 0 24 24"><path d="M15.41 7.41L14 6l-6 6 6 6 1.41-1.41L10.83 12z"/></svg>
                </button>
                <span class="range-text">{{ yearRangeStart }} - {{ yearRangeStart + 11 }}</span>
                <button class="icon-btn small" @click="changeYearRange(1)">
                   <svg viewBox="0 0 24 24"><path d="M10 6L8.59 7.41 13.17 12l-4.58 4.59L10 18l6-6z"/></svg>
                </button>
              </div>
              <div class="year-grid">
                <div
                  v-for="offset in 12"
                  :key="offset"
                  class="year-item"
                  :class="{ active: (yearRangeStart + offset - 1) === tempYear }"
                  @click="selectYear(yearRangeStart + offset - 1)"
                >
                  {{ yearRangeStart + offset - 1 }}
                </div>
              </div>
            </div>

            <!-- Month Picker -->
            <div v-else class="month-selector">
              <div
                v-for="m in 12"
                :key="m"
                class="month-item"
                :class="{ active: tempMonth === m - 1 }"
                @click="selectMonth(m - 1)"
              >
                {{ m }}月
              </div>
            </div>
          </div>
          
          <div class="picker-footer">
            <button class="btn btn-cancel" @click="closeDatePicker">取消</button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue';

import calendar from '@/utils/calendarUtils'

definePageMeta({
  middleware: 'auth'
})

// 响应式数据
const now_date = ref(new Date())
const show_date = ref(new Date())
const monthData = ref([])
const selectedDate = ref(null)

// 日期选择器状态
const isDatePickerOpen = ref(false)
const pickerMode = ref('year') // 'year' | 'month'
const tempYear = ref(new Date().getFullYear())
const tempMonth = ref(new Date().getMonth())
const yearRangeStart = ref(new Date().getFullYear() - 4) // 年份选择器的起始年份

// 星期标题
const weeks = ["一", "二", "三", "四", "五", "六", "日"]

// 导航函数
function openYearPicker() {
  pickerMode.value = 'year'
  tempYear.value = show_date.value.getFullYear()
  yearRangeStart.value = tempYear.value - 4
  isDatePickerOpen.value = true
}

function openMonthPicker() {
  pickerMode.value = 'month'
  tempMonth.value = show_date.value.getMonth()
  isDatePickerOpen.value = true
}

function closeDatePicker() {
  isDatePickerOpen.value = false
}

function selectYear(year) {
  const newDate = new Date(show_date.value)
  newDate.setFullYear(year)
  show_date.value = newDate
  closeDatePicker()
}

function selectMonth(month) {
  const newDate = new Date(show_date.value)
  newDate.setMonth(month)
  show_date.value = newDate
  closeDatePicker()
}

function changeYearRange(delta) {
  yearRangeStart.value += delta * 12
}

function navigateMonth(direction) {
  const newDate = new Date(show_date.value)
  newDate.setMonth(newDate.getMonth() + direction)
  show_date.value = newDate
}

function generateMonth(date) {
  const year = date.getFullYear()
  const month = date.getMonth()

  // 获取当月第一天和最后一天
  const firstDay = new Date(year, month, 1)
  const lastDay = new Date(year, month + 1, 0)

  // 获取第一天是星期几（0=周日，转换为1=周一）
  let firstWeekday = firstDay.getDay()
  if (firstWeekday === 0) firstWeekday = 7

  // 获取上个月需要显示的天数
  const prevMonthDays = firstWeekday - 1
  const prevMonth = new Date(year, month - 1, 0)

  // 获取下个月需要显示的天数
  const totalCells = 42 // 6行 × 7列
  const currentMonthDays = lastDay.getDate()
  const nextMonthDays = totalCells - prevMonthDays - currentMonthDays

  const days = []

  // 载入上个月的日期
  for (let i = prevMonthDays; i > 0; i--) {
    const day = prevMonth.getDate() - i + 1
    days.push({
      type: -1,
      date: new Date(prevMonth.getFullYear(), prevMonth.getMonth(), day),
      fullYear: prevMonth.getFullYear(),
      month: prevMonth.getMonth() + 1,
      day: day
    })
  }

  // 载入当前月的日期
  for (let day = 1; day <= currentMonthDays; day++) {
    days.push({
      type: 0,
      date: new Date(year, month, day),
      fullYear: year,
      month: month + 1,
      day: day
    })
  }

  // 载入下个月的日期
  for (let day = 1; day <= nextMonthDays; day++) {
    days.push({
      type: 1,
      date: new Date(year, month + 1, day),
      fullYear: year,
      month: month + 2,
      day: day
    })
  }

  // 转换为二维数组（6行7列）
  const weeks = []
  for (let i = 0; i < 6; i++) {
    weeks.push(days.slice(i * 7, (i + 1) * 7))
  }
  
  return weeks
}

// 获取日期样式类
function getCellClass(dayInfo) {
  const classes = ['day-cell']
  const today = now_date.value
  
  if (dayInfo.type !== 0) {
    classes.push('day-cell--other-month')
  }
  
  if (dayInfo.fullYear === today.getFullYear() && 
      dayInfo.month === today.getMonth() + 1 && 
      dayInfo.day === today.getDate()) {
    classes.push('day-cell--today')
  }
  
  if (selectedDate.value && 
      dayInfo.fullYear === selectedDate.value.fullYear &&
      dayInfo.month === selectedDate.value.month &&
      dayInfo.day === selectedDate.value.day) {
    classes.push('day-cell--selected')
  }
  
  return classes
}

// 计算月相偏移
function getMoonPhaseOffset(d) {
  const offsetList = [1.5, 2.2, 3, 3.5, 4, 5, 6, 6.5, 7, 7.5, 8, 8.5, 9, 9.5]
  let offset = 0
  const lDay = calendar.solar2lunar(d.fullYear, d.month, d.day)["lDay"]
  if (lDay < 15) offset = -offsetList[lDay - 1]
  else if (lDay > 16) offset = offsetList[(31 - lDay) - 1]
  else offset = 10
  return { left: offset + "px", bottom: Math.abs(offset) + "px" }
}

// 获取日历显示信息（合并农历、节日、节气）
function getDayDisplayInfo(dayInfo) {
  const lunarInfo = calendar.solar2lunar(dayInfo.fullYear, dayInfo.month, dayInfo.day)
  
  // 个人节日
  const personalFestivals_solar = {
    '1-20': '槟·生',
    '4-15': '语·生',
    '9-24': '相恋',
  }
  const personalFestivals_lunar = {
    '2-29': '语·农生',
    '12-14': '槟·农生'
  }
  
  const solarKey = `${dayInfo.month}-${dayInfo.day}`
  const lunarKey = `${lunarInfo.lMonth}-${lunarInfo.lDay}`
  
  // 优先级：个人节日 > 农历节日 > 阳历节日 > 节气 > 农历日
  if (personalFestivals_solar[solarKey]) {
    return { text: personalFestivals_solar[solarKey], type: 'personal' }
  }
  if (personalFestivals_lunar[lunarKey]) {
    return { text: personalFestivals_lunar[lunarKey], type: 'personal' }
  }
  
  if (lunarInfo.lunarFestival) {
    return { text: lunarInfo.lunarFestival, type: 'lunar-festival' }
  }
  
  if (lunarInfo.festival) {
    return { text: lunarInfo.festival, type: 'solar-festival' }
  }
  
  if (lunarInfo.isTerm && lunarInfo.Term) {
    return { text: lunarInfo.Term, type: 'term' }
  }
  
  return { text: lunarInfo.IDayCn, type: 'lunar' }
}

// 点击日期
function onDateClick(dayInfo) {
  if (dayInfo.type !== 0) {
    // 点击其他月份的日期，跳转到对应月份
    const targetDate = new Date(dayInfo.date)
    targetDate.setDate(1)
    show_date.value = targetDate
  }
  selectedDate.value = dayInfo
}

// 监听显示日期变化
watch(show_date, () => {
  monthData.value = generateMonth(show_date.value)
}, { immediate: true })

onMounted(() => {
});
</script>

<style scoped>
.container {
  min-height: calc(100vh - 30px);
  display: flex;
  justify-content: center;
  align-items: flex-start;
  padding-top: 80px;
}

.calendar-card {
  width: 100%;
  max-width: 650px;
  background: var(--color-background);
  border-radius: 20px;
  box-shadow: 0 12px 40px rgba(0, 0, 0, 0.06);
  padding: 24px;
  transition: all 0.3s ease;
  position: relative;
}

/* Header */
.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
  padding: 0 4px;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 4px;
}

.date-btn {
  display: flex;
  align-items: center;
  gap: 4px;
  cursor: pointer;
  padding: 4px 8px;
  border-radius: 12px;
  transition: all 0.2s;
}

.date-btn:hover {
  background: var(--color-background-soft);
}

.edit-icon {
  width: 16px;
  height: 16px;
  fill: var(--color-text-sub);
  opacity: 0;
  transform: translateY(1px);
  transition: all 0.2s;
}

.date-btn:hover .edit-icon {
  opacity: 0.5;
}

.data-text {
  font-size: 24px;
  font-weight: 700;
  color: var(--color-text);
}

.header-controls {
  display: flex;
  gap: 8px;
}

.icon-btn {
  width: 32px;
  height: 32px;
  border-radius: 10px;
  border: none;
  background: var(--color-background-soft);
  color: var(--color-text);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
}

.icon-btn:hover {
  background: var(--color-light-light);
  transform: translateY(-1px);
  color: var(--color-primary);
}

.icon-btn svg {
  width: 20px;
  height: 20px;
  fill: currentColor;
}

/* Weekdays */
.weekdays-row {
  display: grid;
  grid-template-columns: repeat(7, 1fr);
  margin-bottom: 16px;
}

.weekday-cell {
  text-align: center;
  font-size: 14px;
  font-weight: 600;
  color: var(--color-text-sub);
  opacity: 0.8;
  padding: 8px 0;
}

/* Grid */
.days-grid {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.week-row {
  display: grid;
  grid-template-columns: repeat(7, 1fr);
  gap: 4px;
}

.day-cell {
  aspect-ratio: 1;
  border-radius: 12px;
  padding: 6px;
  cursor: pointer;
  transition: all 0.2s;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  border: 1px solid var(--color-border);
  background: var(--color-background-soft);
}

.day-cell:hover {
  background: var(--color-background);
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.04);
  border-color: var(--color-primary);
}

.day-cell--other-month {
  opacity: 0.3;
  pointer-events: none; /* Optional: disable interaction */
}

.day-cell--selected {
  border-color: var(--color-primary);
  background: var(--color-background-soft);
}

.day-cell--today {
  background: var(--color-light-light) !important;
  box-shadow: 0 4px 16px rgba(var(--color-primary-rgb), 0.2);
}

.day-cell--today .day-num {
  color: var(--color-primary);
  font-weight: 700;
}

.day-content {
  height: 100%;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
}

.day-top {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
}

.day-num {
  font-size: 16px;
  font-weight: 500;
  color: var(--color-text);
  line-height: 1;
}

/* Moon Phase */
.moon-phase {
  width: 12px;
  height: 12px;
  background: linear-gradient(135deg, #fff6c8 10%, #ffd54f 60%, #ffb300 100%);
  border-radius: 50%;
  overflow: hidden;
  position: relative;
  opacity: 0.8;
}

.moon_mask {
  position: relative;
  width: 12px;
  height: 12px;
  background-color: var(--color-background); /* Needs to match card background */
  border-radius: 50%;
}

/* Lunar Text Types */
.day-bottom {
  text-align: center; /* Optional: align left or center */
}

.lunar-text {
  font-size: 10px;
  color: var(--color-text-sub);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  display: block;
  padding: 1px 4px;
  border-radius: 4px;
}

.type-personal {
  color: #ff6b6b;
  background: rgba(255, 107, 107, 0.1);
  font-weight: 600;
}

.type-solar-festival {
  color: #4dabf7;
  background: rgba(77, 171, 247, 0.1);
}

.type-lunar-festival {
  color: #ff922b;
  background: rgba(255, 146, 43, 0.1);
}

.type-term {
  color: #20c997;
}

/* Responsive */
@media (max-width: 768px) {
  .container {
    padding: 20px 10px;
  }
  
  .calendar-card {
    padding: 20px 12px;
  }
  
  .day-num {
    font-size: 16px;
  }
  
  .lunar-text {
    font-size: 10px;
    transform: scale(0.9);
    transform-origin: left bottom;
  }
  
  .year-text, .month-text {
    font-size: 24px;
  }
}

/* Date Picker Modal */
.date-picker-modal {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(255, 255, 255, 0.8);
  backdrop-filter: blur(4px);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 100;
  border-radius: 20px;
  animation: fadeIn 0.2s ease;
}

.dark-mode .date-picker-modal {
  background: rgba(0, 0, 0, 0.6);
}

.date-picker-content {
  background: var(--color-background);
  padding: 24px;
  border-radius: 20px;
  box-shadow: 0 8px 40px rgba(0,0,0,0.15);
  width: 320px;
  animation: popIn 0.25s cubic-bezier(0.34, 1.56, 0.64, 1);
  border: 1px solid var(--color-border);
}

.picker-header {
  font-size: 16px;
  font-weight: 600;
  color: var(--color-text-sub);
  margin-bottom: 16px;
  text-align: center;
}

/* Year Picker Styles */
.year-nav {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
  background: var(--color-background-soft);
  padding: 4px 12px;
  border-radius: 12px;
}

.range-text {
  font-weight: 600;
  color: var(--color-text);
}

.year-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 8px;
  margin-bottom: 24px;
}

.year-item {
  padding: 10px 0;
  text-align: center;
  border-radius: 10px;
  cursor: pointer;
  font-size: 15px;
  font-weight: 500;
  color: var(--color-text-sub);
  transition: all 0.2s;
  background: var(--color-background-soft);
}

.year-item:hover {
  background: var(--color-light-light);
  color: var(--color-primary);
}

.year-item.active {
  background: var(--color-primary);
  color: white;
  box-shadow: 0 4px 12px rgba(var(--color-primary-rgb), 0.3);
}

.month-selector {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 8px;
  margin-bottom: 24px;
}

.month-item {
  padding: 10px 0;
  text-align: center;
  border-radius: 10px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 500;
  color: var(--color-text-sub);
  transition: all 0.2s;
  background: var(--color-background-soft);
}

.month-item:hover {
  background: var(--color-light-light);
  color: var(--color-primary);
}

.month-item.active {
  background: var(--color-primary);
  color: white;
  box-shadow: 0 4px 12px rgba(var(--color-primary-rgb), 0.3);
}

.picker-footer {
  display: flex;
  justify-content: center;
}

.btn {
  padding: 8px 20px;
  border-radius: 10px;
  border: none;
  cursor: pointer;
  font-size: 14px;
  font-weight: 600;
  transition: all 0.2s;
}

.btn-cancel {
  background: transparent;
  color: var(--color-text-sub);
}

.btn-cancel:hover {
  background: var(--color-background-soft);
  color: var(--color-text);
}


@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

@keyframes popIn {
  from { opacity: 0; transform: scale(0.9); }
  to { opacity: 1; transform: scale(1); }
}
</style>

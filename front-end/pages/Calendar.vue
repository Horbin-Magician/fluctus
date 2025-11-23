<!-- 日历页 Calendar -->
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

// 星期标题
const weeks = ["一", "二", "三", "四", "五", "六", "日"]

// 导航函数
function navigateYear(direction) {
  const newDate = new Date(show_date.value)
  newDate.setFullYear(newDate.getFullYear() + direction)
  show_date.value = newDate
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

<template>
  <div class="container">
    <div class="calendar-card">
      <!-- 头部 -->
      <header class="header">
        <div class="header-left">
          <span class="year-text">{{ show_date.getFullYear() }}</span>
          <span class="month-text">{{ show_date.getMonth() + 1 }}月</span>
        </div>
        
        <div class="header-controls">
          <button class="icon-btn" @click="navigateMonth(-1)" title="上个月">
            <svg viewBox="0 0 24 24"><path d="M15.41 7.41L14 6l-6 6 6 6 1.41-1.41L10.83 12z"/></svg>
          </button>
          <button class="icon-btn" @click="show_date = new Date()" title="今天">
            <svg viewBox="0 0 24 24"><path d="M19 3h-1V1h-2v2H8V1H6v2H5c-1.11 0-2.9.9-2 2v14c0 1.1.89 2 2 2h14c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2zm0 16H5V8h14v11z"/></svg>
          </button>
          <button class="icon-btn" @click="navigateMonth(1)" title="下个月">
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
    </div>
  </div>
</template>

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
  align-items: baseline;
  gap: 8px;
}

.year-text {
  font-size: 24px;
  font-weight: 700;
  color: var(--color-text-sub);
  font-family: 'Helvetica Neue', sans-serif;
}

.month-text {
  font-size: 24px;
  font-weight: 800;
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
  border: 1px solid transparent;
}

.day-cell:hover {
  background: var(--color-background-soft);
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.04);
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
</style>

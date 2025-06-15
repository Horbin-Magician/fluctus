<!-- 日历页 Calendar -->
<script setup>
import { ref, onMounted, watch } from 'vue';
import { useRouter } from 'vue-router'
import { useMessage } from 'naive-ui'

import calendar from '@/utils/calendarUtils'
import { checkLoginPromise } from '@/utils/userUtils';

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

// 获取节日信息
function getFestivalInfo(dayInfo) {
  const lunarInfo = calendar.solar2lunar(dayInfo.fullYear, dayInfo.month, dayInfo.day)
  const festivals = []
  
  // 阳历节日
  // 重点节日：'1-1': '元旦节', '2-14': '情人节', '3-8': '妇女节', '5-1': '劳动节', '10-1': '国庆节', '12-25': '圣诞节', '12-24': '平安夜',
  if (lunarInfo.festival) {
    festivals.push({ name: lunarInfo.festival, type: 'solar' })
  }
  
  // 农历节日
  // 重点节日：'1-1': '春节', '1-15': '元宵节', '5-5': '端午节', '7-7': '七夕节', '8-15': '中秋节', '12-30': '除夕',
  if (lunarInfo.lunarFestival) {
    festivals.push({ name: lunarInfo.lunarFestival, type: 'lunar' })
  }
  
  // 24节气
  if (lunarInfo.isTerm && lunarInfo.Term) {
    festivals.push({ name: lunarInfo.Term, type: 'term' })
  }
  
  // 个人节日（从原代码中提取）
  const personalFestivals_solar = {
    '1-20': '小小槟阳历生日',
    '4-15': '小小语阳历生日',
    '9-24': '相恋纪念日',
  }

  const personalFestivals_lunar = {
    '2-29': '小小语农历生日',
    '12-14': '小小槟农历生日'
  }
  
  const solarKey = `${dayInfo.month}-${dayInfo.day}`
  const lunarKey = `${lunarInfo.lMonth}-${lunarInfo.lDay}`

  if (personalFestivals_solar[solarKey]) {
    festivals.push({ name: personalFestivals_solar[solarKey], type: 'personal' })
  }
  
  if (personalFestivals_lunar[lunarKey]) {
    festivals.push({ name: personalFestivals_lunar[lunarKey], type: 'personal' })
  }

  return festivals
}

// 获取农历信息
function getLunarInfo(dayInfo) {
  const lunarInfo = calendar.solar2lunar(dayInfo.fullYear, dayInfo.month, dayInfo.day)
  return {
    day: lunarInfo.IDayCn,
    month: lunarInfo.IMonthCn
  }
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
  const message = useMessage()
  const router = useRouter()

  checkLoginPromise().then((result) => {
    if (!result) {
      router.push('/')
      message.error("请先登录！")
    }
  });
});
</script>

<template>
  <div class="container">
    <!-- 日历主体 -->
    <div class="calendar">
      <!-- 日历头部 -->
      <div class="calendar-header">
        <div class="nav-buttons">
          <button class="nav-btn" title="上一年" @click="navigateYear(-1)">
            <svg viewBox="0 0 24 24" width="16" height="16">
              <path d="M15.41 7.41L14 6l-6 6 6 6 1.41-1.41L10.83 12z"/>
              <path d="M15.41 7.41L14 6l-6 6 6 6 1.41-1.41L10.83 12z" transform="translate(4,0)"/>
            </svg>
          </button>
          <button class="nav-btn" title="上个月" @click="navigateMonth(-1)">
            <svg viewBox="0 0 24 24" width="16" height="16">
              <path d="M15.41 7.41L14 6l-6 6 6 6 1.41-1.41L10.83 12z"/>
            </svg>
          </button>
        </div>

        <div>
          <span class="cal_h_time">{{ show_date.getFullYear() }} 年 </span>
          <span class="cal_h_time">{{ show_date.getMonth() + 1 }} 月</span>
        </div>

        <div class="nav-buttons">
          <button class="nav-btn" title="下个月" @click="navigateMonth(1)">
            <svg viewBox="0 0 24 24" width="16" height="16">
              <path d="M8.59 16.59L10 18l6-6-6-6-1.41 1.41L13.17 12z"/>
            </svg>
          </button>
          <button class="nav-btn" title="下一年" @click="navigateYear(1)">
            <svg viewBox="0 0 24 24" width="16" height="16">
              <path d="M8.59 16.59L10 18l6-6-6-6-1.41 1.41L13.17 12z"/>
              <path d="M8.59 16.59L10 18l6-6-6-6-1.41 1.41L13.17 12z" transform="translate(-4,0)"/>
            </svg>
          </button>
        </div>
      </div>

      <!-- 星期标题 -->
      <div class="weekdays">
        <div v-for="week in weeks" :key="week" class="weekday"> {{ week }} </div>
      </div>

      <!-- 日期网格 -->
      <div class="calendar-grid">
        <div v-for="(week, weekIndex) in monthData" :key="weekIndex" class="calendar-week">
          <div 
            v-for="dayInfo in week" 
            :key="`${dayInfo.fullYear}-${dayInfo.month}-${dayInfo.day}`"
            :class="getCellClass(dayInfo)"
            @click="onDateClick(dayInfo)"
          >
            <div class="day-info">
              <div class="day-number">{{ dayInfo.day }}</div>
              <div class="lunar-info">{{ getLunarInfo(dayInfo).day }}</div> <!-- 农历信息 -->
            </div>
            
            <!-- 月相 -->
            <div class="moon">
              <div class="moon_mask" :style="getMoonPhaseOffset(dayInfo)" />
            </div>
            
            <!-- 节日信息 -->
            <div class="festivals">
              <div 
                v-for="festival in getFestivalInfo(dayInfo)" 
                :key="festival.name"
                :class="['festival', `festival--${festival.type}`]"
              >
                {{ festival.name }}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
/* 主容器 */
.container {
  height: calc(100vh - 80px);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
}

/* 日历主体 */
.calendar {
  background: var(--color-background);
  border: 2px solid var(--color-text-sub-sub);
  border-radius: 16px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
  overflow: hidden;
  width: 100%;
  max-width: 800px;
  transition: all 0.3s ease;
}

/* 日历头部 */
.calendar-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 14px;
  background: linear-gradient(180deg, var(--color-light-light) 0%, transparent 100%);
  border-bottom: 1px solid var(--color-text-sub-sub);
}

.nav-buttons {
  display: flex;
  gap: 8px;
}

.nav-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 36px;
  height: 36px;
  background: transparent;
  border: 1px solid var(--color-text-sub-sub);
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s ease;
  color: var(--color-text);
}

.nav-btn:hover {
  background: var(--color-light);
  border-color: var(--color-light);
  color: white;
  transform: scale(1.1);
}

.nav-btn svg {
  fill: currentColor;
}

.cal_h_time {
  cursor: pointer;
  height: 34px;
  line-height: 34px;
}

.cal_h_time:hover {
  color: var(--color-light);
}

/* 星期标题 */
.weekdays {
  display: grid;
  grid-template-columns: repeat(7, 1fr);
  background: var(--color-background);
  border-bottom: 1px solid var(--color-text-sub-sub);
}

.weekday {
  padding: 12px;
  text-align: center;
  font-weight: 600;
  color: var(--color-text-sub);
  font-size: 14px;
}

/* 日期网格 */
.calendar-grid {
  display: flex;
  flex-direction: column;
  /* 防止与外边框重叠 */
  margin: -1px;
}

.calendar-week {
  display: grid;
  grid-template-columns: repeat(7, 1fr);
}

/* 日期单元格 */
.day-cell {
  position: relative;
  min-height: 80px;
  padding: 8px;
  border: 1px solid var(--color-text-sub-sub);
  cursor: pointer;
  transition: all 0.3s ease;
  background: var(--color-background);
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  justify-content: flex-start;
  /* 消除边框重叠 */
  margin-right: -1px;
  margin-bottom: -1px;
}

.day-cell:hover {
  background: var(--color-light-light);
}

.day-cell--other-month {
  color: var(--color-text-sub-sub);
  background: rgba(var(--color-text-sub-sub), 0.05);
}

.day-cell--other-month:hover {
  background: rgba(var(--color-text-sub-sub), 0.1);
}

.day-cell--today {
  background: linear-gradient(135deg, var(--color-light) 0%, var(--color-light-light) 100%);
  color: white;
  font-weight: 600;
}

.day-cell--today .lunar-info,
.day-cell--today .festival {
  color: rgba(255, 255, 255, 0.9);
}

.day-cell--selected {
  background: var(--color-light-light);
}

.day-info {
  display: flex;
  flex-direction: column;
}

/* 日期数字 */
.day-number {
  font-size: 16px;
  font-weight: 600;
  margin-bottom: 4px;
}

/* 农历信息 */
.lunar-info {
  font-size: 10px;
  color: var(--color-text-sub);
  margin-bottom: 4px;
}

/* 月相 */
.moon {
  position: absolute;
  right: 8px;
  top: 11px;
  width: 15px;
  height: 15px;
  background-color: #e9e946;
  border-radius: 50%;
  overflow: clip;
}

.moon_mask {
  position: relative;
  width: 15px;
  height: 15px;
  background-color: var(--color-background);
  border-radius: 50%;
}

/* 节日信息 */
.festivals {
  display: flex;
  flex-direction: column;
  gap: 2px;
  margin-top: auto;
  width: 100%;
}

.festival {
  font-size: 10px;
  padding: 1px 4px;
  border-radius: 4px;
  text-align: center;
  font-weight: 500;
  line-height: 1.2;
  max-width: 100%;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.festival--solar {
  background: rgba(255, 206, 86, 0.2);
  color: #c09015;
  border: 1px solid rgba(255, 206, 86, 0.3);
}

.festival--lunar {
  background: rgba(54, 162, 235, 0.2);
  color: #1787d2;
  border: 1px solid rgba(54, 162, 235, 0.3);
}

.festival--term {
  background: rgba(75, 192, 192, 0.2);
  color: #4bc0c0;
  border: 1px solid rgba(75, 192, 192, 0.3);
}

.festival--personal {
  background: rgba(255, 99, 132, 0.2);
  color: #ff6384;
  border: 1px solid rgba(255, 99, 132, 0.3);
}

/* 响应式设计 */
@media (max-width: 768px) {
  .calendar-container {
    padding: 10px;
    gap: 15px;
  }
  
  .today-panel {
    flex-direction: column;
    gap: 12px;
    text-align: center;
  }
  
  .calendar-header {
    padding: 15px;
  }

  
  .day-cell {
    min-height: 60px;
    padding: 4px;
  }
  
  .day-number {
    font-size: 14px;
  }
  
  .lunar-info {
    font-size: 9px;
  }
  
  .festival {
    font-size: 8px;
  }
}

@media (max-width: 480px) {
  .nav-btn {
    width: 32px;
    height: 32px;
  }
  
  .day-cell {
    min-height: 50px;
    padding: 2px;
  }
  
  .day-number {
    font-size: 12px;
  }
  
  .lunar-info {
    font-size: 8px;
  }
  
  .moon-phase {
    width: 10px;
    height: 10px;
  }
}

/* 动画效果 */
@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.calendar {
  animation: fadeIn 0.5s ease-out;
}

.day-cell {
  animation: fadeIn 0.3s ease-out;
}
</style>

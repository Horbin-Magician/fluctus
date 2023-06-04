<!-- 日历页 Calendar -->
<script setup>
    import { ref } from 'vue';
    import { RouterLink, useRouter, useRoute } from 'vue-router'

    import calendar from '@/utils/calendarUtils'
    import { checkLogin } from '@/utils/userUtils';

    const router = useRouter()
    if(!checkLogin()) router.push('/')

    function preYear () {
        let n = show_date.value
        n.setFullYear(n.getFullYear() - 1)
        setYearMonthInfos(n)
    }

    function preMonth () {
        let n = show_date.value
        n.setMonth(n.getMonth() - 1)
        setYearMonthInfos(n)
    }

    function nextYear () {
        let n = show_date.value
        n.setFullYear(n.getFullYear() + 1)
        setYearMonthInfos(n)
    }

    function nextMonth(){
        let n = show_date.value
        n.setMonth(n.getMonth() + 1)
        setYearMonthInfos(n)
    }

    function setYearMonthInfos(date){
        monthData.value = generateMonth(date)
    }

    function generateMonth(date){
        let weekStart = date.getDay() // 星期 0 - 6， 星期天 - 星期6
        if(weekStart == 0) weekStart += 7 // 星期 1 - 7， 星期一 - 星期日

        let endDate = new Date(date.getFullYear(), date.getMonth() + 1, 0)
        let dayEnd = endDate.getDate()
        let weeEnd = endDate.getDay()
        if(weeEnd == 0) weeEnd += 7 // 星期 1 - 7， 星期一 - 星期日

        let milsStart = date.getTime()
        let dayMils = 24 * 60 * 60 * 1000
        let milsEnd = endDate.getTime() + dayMils

        let monthDatas = []
        let current;
        // 载入初始周属于上月日子
        for (let i = 1; i < weekStart; i++) {
            current = new Date(milsStart - (weekStart - i) * dayMils)
            monthDatas.push({
            type: -1,
            date: current,
            fullYear: current.getFullYear(),
            month: current.getMonth() + 1,
            day: current.getDate()
            })
        }
        // 载入当前月日子
        for (let i = 0; i < dayEnd; i++) {
            current = new Date(milsStart + i * dayMils)
            monthDatas.push({
            type: 0,
            date: current,
            fullYear: current.getFullYear(),
            month: current.getMonth() + 1,
            day: current.getDate()
            })
        }
        // 载入最后一周属于下一月的日子
        for (let i = 0; i < (7 - weeEnd); i++) {
            current = new Date(milsEnd + i * dayMils)
            monthDatas.push({
            type: 1,
            date: current,
            fullYear: current.getFullYear(),
            month: current.getMonth() + 1,
            day: current.getDate()
            })
        }

        let monthData = []
        for (let i = 0; i < monthDatas.length; i++) {
            let mi = i % 7;
            if (mi == 0) {
                monthData.push([])
            }
            monthData[Math.floor(i / 7)].push(monthDatas[i])
        }

        // // 少于6行，补足6行
        // if (monthData.length <= 5) {
        //     milsStart = current.getTime()
        //     let lastLine = []
        //     for (let i = 1; i <= 7; i++) {
        //     current = new Date(milsStart + i * dayMils)
        //     lastLine.push({
        //         type: 1,
        //         date: current,
        //         fullYear: current.getFullYear(),
        //         month: current.getMonth() + 1,
        //         day: current.getDate()
        //     })
        //     }
        //     monthData.push(lastLine)
        // }

        return monthData
    }

    function getCellClass(d){
        let return_data = {'day_cell':true}
        const now_year = now_date.value.getFullYear()
        const now_month = now_date.value.getMonth() + 1
        const now_day = now_date.value.getDate()

        if(d.type != 0) return_data['day_cell_invalid'] = true
        if(d.fullYear == now_year && d.month == now_month && d.day == now_day) return_data['day_cell_today'] = true
        return return_data;
    }

    function calOffset(d){
        const offsetList = [1.5, 2.2, 3, 3.5, 4, 5, 6, 6.5, 7, 7.5, 8, 8.5, 9, 9.5]
        let offset = 0
        const lDay = calendar.solar2lunar(d.fullYear, d.month, d.day)["lDay"]
        if(lDay < 15) offset = -offsetList[lDay - 1]
        else if(lDay > 16)  offset = offsetList[(31 - lDay) - 1]
        else offset = 10
        return {left: offset + "px", bottom: Math.abs(offset) + "px"}
    }

    function getFestival(d){
        /**
         * 阳历节日
         */
        const festivalList = {
        '1-1':   {title: '元旦节'},
        '1-20':   {title: '小小槟阳历生日'},
        '2-14':  {title: '情人节'},
        '3-7':   {title: '女生节'},
        '3-8':   {title: '妇女节'},
        '4-15':   {title: '小小语阳历生日'},
        '5-1':   {title: '劳动节'},
        '9-24':  {title: '相恋纪念日'},
        '10-1':  {title: '国庆节'},
        '12-25': {title: '圣诞节'},
        '12-24': {title: '平安夜'},
        }
    
        /**
         * 农历节日
         */
        const lfestivalList = {
        '1-1':   {title: '春节'},
        '1-15':  {title: '元宵节'},
        '2-29': {title: '小小语农历生日'},
        '5-5':   {title: '端午节'},
        '7-7':   {title: '七夕节'},
        '8-15':  {title: '中秋节'},
        '12-14': {title: '小小槟农历生日'},
        '12-30': {title: '除夕'},
        }

        const date = calendar.solar2lunar(d.fullYear, d.month, d.day)
        const festivalDate = date.cMonth + '-' + date.cDay
        const lFestivalDate = date.lMonth + '-' + date.lDay
        const festival = festivalList[festivalDate] ? festivalList[festivalDate].title : null
        const lunarFestival = lfestivalList[lFestivalDate] ? lfestivalList[lFestivalDate].title : null
        let return_festival = ""
        if(festival) return_festival += festival
        if(lunarFestival){
            if(return_festival != "") return_festival = return_festival + ' '
            return_festival += lunarFestival
        }
        return return_festival
    }

    const now_date = ref(new Date())
    let tempDate = new Date()
    tempDate.setDate(1)
    const show_date = ref(tempDate)

    const weeks = ["一", "二", "三", "四", "五", "六", "日"]
    const monthData = ref(generateMonth(show_date.value))
</script>

<template>
    <div class="container">
        <div class="calendar">
            <div class="cal_header">
                <div class="cal_h_left">
                    <div class="cal_h_btn" @click="preYear">
                        <svg>
                            <polyline points="6,0 2,4 6,8" style="fill:none;stroke:#909399;stroke-width:1"/>
                            <polyline points="10,0 6,4 10,8" style="fill:none;stroke:#909399;stroke-width:1"/>
                        </svg>
                    </div>
                    <div class="cal_h_btn" @click="preMonth">
                        <svg>
                            <polyline points="6,0 2,4 6,8" style="fill:none;stroke:#909399;stroke-width:1"/>
                        </svg>
                    </div>
                </div>

                <div>
                    <span class="cal_h_time">{{ show_date.getFullYear() }} 年 </span>
                    <span class="cal_h_time">{{ show_date.getMonth() + 1 }} 月</span>
                </div>

                <div class="cal_h_left">
                    <div class="cal_h_btn" @click="nextMonth">
                        <svg>
                            <polyline points="2,0 8,4 2,8" style="fill:none;stroke:#909399;stroke-width:1"/>
                        </svg>
                    </div>
                    <div class="cal_h_btn" @click="nextYear">
                        <svg>
                            <polyline points="2,0 8,4 2,8" style="fill:none;stroke:#909399;stroke-width:1"/>
                            <polyline points="6,0 12,4 6,8" style="fill:none;stroke:#909399;stroke-width:1"/>
                        </svg>
                    </div>
                </div>
            </div>

            <div class="cal_month">
                <div class="cal_m_weeks">
                    <span v-for="w in weeks" :key="w" class="cal_m_weeks_cell">{{w}}</span>
                </div>

                <div class="cal_m_days">
                    <div v-for="(ds, index) in monthData" :key="index" class="cal_m_day_line">
                        <div v-for="d in ds" :key="d.day" :class="getCellClass(d)">
                            <div class="days_num">
                                {{ d.day }}
                            </div>
                            <div class="moon">
                                <div class="moon_mask" v-bind:style="calOffset(d)"></div>
                            </div>
                            <div class="festival">
                                {{getFestival(d)}}
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>

<style scoped>
    .container{
        height: calc(100vh - 80px);
        display: grid;
        place-items: center;
        align-content: center;
    }

    .calendar{
        width: 740px;
        box-shadow: 0 0 2px var(--color-text);
        background: var(--color-background);
        border-radius: 4px;
        align-self: end;
    }

    .calendar .cal_header{
        padding: 3px;
        display: flex;
        justify-content: space-between;
    }

    .calendar .cal_header .cal_h_time{
        cursor: pointer;
        height: 34px;
        line-height: 34px;
    }

    .calendar .cal_header .cal_h_time:hover{
        color: var(--color-light);
    }

    .calendar .cal_header .cal_h_left{
        height: 100%;
        display: flex;
    }

    .calendar .cal_header .cal_h_left .cal_h_btn{
        width: 24px;
        line-height: 34px;
        cursor: pointer;
    }

    .calendar .cal_header .cal_h_left .cal_h_btn svg{
        height: 8px;
        width: 14px;
        margin: 0 5px;
    }

    .calendar .cal_month{
        font-size: 12px;
        text-align: center;
    }

    .calendar .cal_month .cal_m_weeks{
        display: flex;
        justify-content: space-around;
        justify-items: center;
        border-bottom: 1px solid var(--color-text);
        margin: 0px 10px;
    }

    .calendar .cal_month .cal_m_weeks_cell{
        width: 100px;
        height: 40px;
        line-height: 40px;
        position: relative;
    }

    .calendar .cal_month .cal_m_days{
        display: flex;
        justify-content: space-around;
        justify-items: center;
        flex-wrap: wrap;
        margin: 10px;
    }

    .calendar .cal_month .cal_m_days .cal_m_day_line{
        display: flex;
        justify-content: space-around;
        justify-items: center;
    }

    .day_cell{
        width: 100px;
        height: 70px;
        cursor: pointer;
        transition: box-shadow 0.2s;
        border-radius: 2px;
        margin: 2px;
    }
    
    .day_cell:hover{
        box-shadow: 0 0 0 1px var(--color-light);
    }

    .day_cell_today{
        font-weight: 700;
        color: var(--color-light);
    }

    .day_cell_invalid{
        color: var(--color-text-sub-sub);
    }

    .day_cell_invalid .festival{
        color: var(--color-text-sub-sub);
    }

    .day_cell_invalid:hover{
        box-shadow: 0 0 0 0 var(--color-light);
        cursor: default;
    }

    .days_num{
        text-align: center;
        font-size: 14px;
        font-weight:500;
    }

    .moon{
        position:absolute;
        right: 23px;
        top: 4px;

        width:15px;
        height:15px;
        background-color:#d5c300;
        border-radius:50%;
        overflow: hidden;
        opacity: 0.3;
    }

    .moon_mask{
        position: relative;
        width:15px;
        height:15px;
        background-color:var(--color-background);
        border-radius:50%;
    }

    .festival{
        margin-top: 5px;
    }
</style>

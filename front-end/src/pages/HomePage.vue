<!-- 主页 Home -->
<script setup>
    import { ref, watch } from 'vue';

    import '@/assets/icons/iconfont'
    import { reqSugList } from '@/api/searchAPI'
    import storageUtils from '@/utils/storageUtils';

    const searchValue = ref('')
    const sugList = ref([])
    const searchDivHeight = ref('40px')
    const selectedSugIndex = ref(null)

    const changingSearchSource = ref(false)

    const logoOffsetX = ref('0px')
    const logoOffsetY = ref('0px')

    const defaultSearchSource = storageUtils.getDefaultSearchSource()
    const nowSearchSource = ref(defaultSearchSource ? defaultSearchSource : 'baidu')

    const searchSources = {'baidu':'https://www.baidu.com/s?wd=', 'bing':'https://cn.bing.com/search?q=', 'google':'https://www.google.com/search?q='}

    let search = () => {
        if(selectedSugIndex.value == null) openURL(searchSources[nowSearchSource.value] + searchValue.value);
        else openURL(searchSources[nowSearchSource.value] + sugList.value[selectedSugIndex.value]['q']);
    }

    let openURL = (url) => {
        window.location.href=url;
    }

    let selectPre = (event) => {
        if(selectedSugIndex.value == null){
            selectedSugIndex.value = 0
            return
        }
        event.stopPropagation()
        if(selectedSugIndex.value == 0) return
        selectedSugIndex.value = selectedSugIndex.value - 1
    }

    let selectNext = (event) => {
        if(selectedSugIndex.value == null){
            selectedSugIndex.value = 0
            return
        }
        event.stopPropagation()
        if(selectedSugIndex.value == sugList.value.length - 1) return
        selectedSugIndex.value = selectedSugIndex.value + 1
    }

    let filterUpDownKey = (event)=>{
        var key_num = event.keyCode
        if (38 == key_num || 40 == key_num) event.preventDefault()
    }

    let changeSearchSource = (sourse, flag = undefined)=>{
        console.log(flag)
        if(flag == 'out'){
            changingSearchSource.value = false;
            return
        }

        if(changingSearchSource.value == false){
            changingSearchSource.value = true;
            return;
        }

        if(sourse){
            nowSearchSource.value = sourse;
            storageUtils.setDefaultSearchSource(sourse);
        }
        changingSearchSource.value = false;
    }

    watch(searchValue, async(newValue, oldValue) => {
        if(newValue != oldValue && newValue != ''){
            reqSugList(newValue).then(data => {
                if(searchValue.value != ''){
                    sugList.value = data['data']
                    searchDivHeight.value = sugList.value.length * 34 + 45 + 'px'
                }
            })
        }else{
            sugList.value = []
            searchDivHeight.value = '40px'
        }
        selectedSugIndex.value = null
    })
</script>

<template>
    <div class="container" @mousemove="watchMouseMove">
        <svg id="homelogo">
            <use xlink:href="#icon-homelogo"></use>
        </svg>
        <div class="search-div" tabIndex="0" @keyup.up.prevent="selectPre" @keyup.down.prevent="selectNext">
            <div class="search-input-container">
                <div class="search-icon-source-container"
                :style="{width:changingSearchSource ? '100px' : '28px'}"
                tabindex = "-1"
                @focusout="()=>changeSearchSource(undefined, 'out')">
                    <svg class="search-icon" @click="()=>changeSearchSource()">
                        <use :xlink:href="'#icon-' + nowSearchSource"></use>
                    </svg>
                    <svg v-for="(searchSource, index) in Object.keys(searchSources)" :key="searchSource"
                    :class="{'search-icon':true, 'select-source': true}"
                    @click="()=>changeSearchSource(searchSource)"
                    :display="searchSource == nowSearchSource ? 'none' : 'inline'">
                        <use :xlink:href="'#icon-' + searchSource"></use>
                    </svg>
                </div>
                <input class="search-input" @keydown="filterUpDownKey" @keyup.enter="search" v-model="searchValue"/>
                <svg class="search-icon" @mousedown="search">
                    <use xlink:href="#icon-search"></use>
                </svg>
            </div>
            <div>
                <div v-for="(sug, index) in sugList" :key="index"
                :class="{'sug-item':true, 'selected-sug': selectedSugIndex == index}"
                @mouseenter="()=>{selectedSugIndex = index}" @click="search">
                    {{ sug['q'] }}
                </div>
            </div>
        </div>
        <div class="overlay"></div>
    </div>
</template>

<style scoped>
    .container{
        height: calc(100vh - 80px);
        display: grid;
        grid-template-rows: 24vh 100px 60px;
        place-items: center;
    }

    #homelogo{
        grid-row-start: 2;
        margin-left: v-bind('logoOffsetX');
        margin-bottom: v-bind('logoOffsetY');
        height: 100px;
        width: 200px;
        fill: var(--color-light);
        animation: floatImage 4s ease-in-out infinite;
    }
    .search-div{
        height: v-bind('searchDivHeight');
        margin-top: 10px;
        padding: 0px 4px;
        grid-row-start: 3;
        align-self:flex-start;
        border: 2px solid var(--color-light);
        border-radius: 20px;
        transition: all 0.2s ease-out;
        overflow: hidden;
        background-color: var(--color-background);
        z-index: 200;
    }

    .search-div:hover{
        box-shadow: 0 0 5px var(--color-light);
    }

    .search-div:focus-within{
        box-shadow: 0 0 5px var(--color-light);
    }

    .search-div:focus-within~.overlay{
        z-index: 100;
        background: rgba(0, 0, 0, 0.3);
    }

    .search-input-container{
        display: flex;
        height: 36px;
        align-items: center;
        width: 400px;
        justify-content: space-between;
        transition: all 0.2s ease-out;
    }

    .search-input{
        background-color: transparent;
        border: none;
        outline: none;
        text-align: center;
        height: 100%;
        margin: 0px 4px;
        font-size: 16px;
        color: var(--color-text);
        flex-grow: 5;
    }

    .search-input-container:focus-within{
        width: 500px;
    }

    .search-icon-source-container{
        width: 28px;
        height: 28px;
        border-radius: 14px;
        overflow: hidden;
    }

    .search-icon{
        width: 28px;
        height: 28px;
        border-radius: 14px;
        fill: var(--color-light);
        cursor: pointer;
    }

    .select-source{
        margin-left: 4px;
    }

    .search-icon:hover{
        filter: drop-shadow( 0px 0px 1px var(--color-light) );
    }

    .sug-item:first-child{
        border-top: 2px solid var(--grey);
    }

    .sug-item:last-child{
        border-radius: 0px 0px 16px 16px;
    }

    .sug-item{
        width: 100%;
        height: 34px;
        line-height: 34px;
        text-align: center;
        font-size: 16px;
        color: var(--color-text-sub);
        cursor: pointer;
    }

    .selected-sug{
        background-color: var(--color-light-light);
    }

    .overlay{
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        transition: 0.3s ease-out;
        z-index: -1;
    }

    @keyframes floatImage {
        0% {transform: translateY(0);}
        50% {transform: translateY(-4px);}
        100% {transform: translateY(0);}
    }
</style>
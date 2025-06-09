import { ref, watch } from 'vue'
import type { ApiResponse, SugListResponse } from '@/api'
import { reqSugList } from '@/api'
import storageUtils from '@/utils/storageUtils'

export interface SearchSource {
  key: string
  name: string
  url: string
  icon: string
}

export const searchSources: Record<string, SearchSource> = {
  baidu: {
    key: 'baidu',
    name: '百度',
    url: 'https://www.baidu.com/s?wd=',
    icon: 'icon-baidu'
  },
  bing: {
    key: 'bing',
    name: '必应',
    url: 'https://cn.bing.com/search?q=',
    icon: 'icon-bing'
  },
  google: {
    key: 'google',
    name: '谷歌',
    url: 'https://www.google.com/search?q=',
    icon: 'icon-google'
  }
}

export function useSearch() {
  const searchValue = ref('')
  const sugList = ref<SugListResponse>([])
  const selectedSugIndex = ref<number | null>(null)
  const error = ref<string | null>(null)

  // 获取默认搜索源
  const getDefaultSearchSource = (): string => {
    const defaultSource = storageUtils.getDefaultSearchSource()
    return defaultSource && Object.keys(searchSources).includes(defaultSource) 
      ? defaultSource 
      : 'baidu'
  }

  const currentSearchSource = ref(getDefaultSearchSource())

  // 获取搜索建议
  const fetchSuggestions = async (query: string) => {
    if (!query.trim()) {
      sugList.value = []
      return
    }

    error.value = null

    try {
      const response: ApiResponse<SugListResponse> = await reqSugList(query)
      if (searchValue.value === query) { // 确保结果对应当前搜索值
        sugList.value = response.data as SugListResponse
      }
    } catch (err) {
      error.value = '获取搜索建议失败'
      console.error('搜索建议获取失败:', err)
    }
  }

  // 防抖搜索建议
  let debounceTimer: NodeJS.Timeout | null = null
  const debouncedFetchSuggestions = (query: string) => {
    if (debounceTimer) clearTimeout(debounceTimer)
    debounceTimer = setTimeout(() => fetchSuggestions(query), 300)
  }

  // 监听搜索值变化
  watch(searchValue, (newValue, oldValue) => {
    if (newValue !== oldValue) {
      selectedSugIndex.value = null
      if (newValue.trim()) {
        debouncedFetchSuggestions(newValue)
      } else {
        sugList.value = []
      }
    }
  })

  // 执行搜索
  const performSearch = () => {
    const query = selectedSugIndex.value !== null 
      ? sugList.value[selectedSugIndex.value]?.q 
      : searchValue.value

    if (query?.trim()) {
      const searchUrl = searchSources[currentSearchSource.value].url + encodeURIComponent(query)
      window.location.href = searchUrl
    }
  }

  // 键盘导航
  const navigateUp = (event: KeyboardEvent) => {
    event.preventDefault()
    if (sugList.value.length === 0) return

    if (selectedSugIndex.value === null || selectedSugIndex.value === 0) {
      selectedSugIndex.value = sugList.value.length - 1
    } else {
      selectedSugIndex.value--
    }
  }

  const navigateDown = (event: KeyboardEvent) => {
    event.preventDefault()
    if (sugList.value.length === 0) return

    if (selectedSugIndex.value === null || selectedSugIndex.value === sugList.value.length - 1) {
      selectedSugIndex.value = 0
    } else {
      selectedSugIndex.value++
    }
  }

  // 切换搜索源
  const changeSearchSource = (sourceKey: string) => {
    if (Object.keys(searchSources).includes(sourceKey)) {
      currentSearchSource.value = sourceKey
      storageUtils.setDefaultSearchSource(sourceKey)
    }
  }

  return {
    searchValue,
    sugList,
    selectedSugIndex,
    error,
    currentSearchSource,
    searchSources,
    performSearch,
    navigateUp,
    navigateDown,
    changeSearchSource,
    setSelectedIndex: (index: number | null) => {
      selectedSugIndex.value = index
    }
  }
}

<template>
  <div class="page-wrapper">
    <div class="article-container">
      <div v-if="article">
        <div class="article-header">
          <h1>{{ article.title }}</h1>
          <div class="meta">
            <span>{{ article.date }}</span>
            <span v-if="article.categories" class="category">{{ article.categories }}</span>
          </div>
          <div class="tags" v-if="article.tags && article.tags.length">
              <span v-for="tag in article.tags" :key="tag" class="tag">#{{ tag }}</span>
          </div>
        </div>
        <div class="markdown-body" v-html="contentHtml" @click="handleCopy"></div>
      </div>
      <div v-else class="loading">
        加载中...
      </div>
    </div>

    <aside class="toc-sidebar" v-if="toc.length > 0">
      <div class="toc-content">
        <div class="active-marker" :style="markerStyle"></div>
        <ul>
          <li v-for="item in toc" :key="item.id" :class="`toc-level-${item.level}`">
            <a 
              :href="`#${item.id}`" 
              :class="{ active: activeHeading === item.id }"
              @click.prevent="scrollToHeading(item.id)"
            >
              {{ item.text }}
            </a>
          </li>
        </ul>
      </div>
    </aside>
  </div>
</template>

<script setup>
import { ref, onMounted, nextTick, onUnmounted } from 'vue'
import { useRoute } from 'vue-router'
import { getArticleBySlug, markdownToHtml } from '@/utils/blogUtils'
import 'highlight.js/styles/atom-one-dark.css'

const route = useRoute()
const article = ref(null)
const contentHtml = ref('')
const toc = ref([])
const activeHeading = ref('')
const markerStyle = ref({ top: '0px', height: '0px', opacity: 0 })

watch(activeHeading, () => {
  nextTick(() => {
    updateMarker()
  })
})

const updateMarker = () => {
  if (!activeHeading.value) return
  
  // Find the link element in the TOC
  // We need to scope this to toc-content to avoid selecting other links if any
  const container = document.querySelector('.toc-content')
  if (!container) return

  const link = container.querySelector(`a[href="#${activeHeading.value}"]`)
  if (link) {
    // Calculate relative position
    const containerRect = container.getBoundingClientRect()
    const linkRect = link.getBoundingClientRect()
    
    // Adjust logic if toc-content has padding/relative positioning
    // Since marker is inside toc-content, we want position relative to it.
    // Using offsetTop is easier if offsetParent is toc-content
    
    markerStyle.value = {
      top: `${link.offsetTop}px`,
      height: `${link.offsetHeight}px`,
      opacity: 1
    }
  }
}

onMounted(async () => {
  const slug = route.params.slug
  const data = getArticleBySlug(slug)
  
  if (data) {
    article.value = data
    contentHtml.value = await markdownToHtml(data.content)
    
    await nextTick()
    generateToc()
    setupIntersectionObserver()
  }
})

onUnmounted(() => {
  if (observer) {
    observer.disconnect()
  }
})

const generateToc = () => {
  const headings = document.querySelectorAll('.markdown-body h1, .markdown-body h2, .markdown-body h3')
  toc.value = Array.from(headings).map(h => ({
    id: h.id,
    text: h.innerText,
    level: parseInt(h.tagName.substring(1))
  }))
}

const scrollToHeading = (id) => {
  const element = document.getElementById(id)
  if (element) {
    // Add offset for fixed header if exists, or just some padding
    const offset = 80 
    const elementPosition = element.getBoundingClientRect().top
    const offsetPosition = elementPosition + window.pageYOffset - offset

    window.scrollTo({
      top: offsetPosition,
      behavior: "smooth"
    })
    // Do not set activeHeading immediately; let IntersectionObserver handle it
    // activeHeading.value = id 
  }
}

let observer = null
const setupIntersectionObserver = () => {
  const options = {
    root: null,
    rootMargin: '-100px 0px -60% 0px', // Adjust these values to trigger activation appropriately
    threshold: 0.1
  }

  observer = new IntersectionObserver((entries) => {
    entries.forEach((entry) => {
      if (entry.isIntersecting) {
        activeHeading.value = entry.target.id
      }
    })
  }, options)

  document.querySelectorAll('.markdown-body h1, .markdown-body h2, .markdown-body h3').forEach((heading) => {
    observer.observe(heading)
  })
}

const handleCopy = async (event) => {
  const btn = event.target.closest('.copy-code-btn')
  if (!btn) return
  
  const wrapper = btn.closest('.code-block-wrapper')
  if (!wrapper) return
  
  const codeBlock = wrapper.querySelector('code')
  if (!codeBlock) return
  
  const text = codeBlock.innerText
  
  try {
    await navigator.clipboard.writeText(text)
    
    // Temporary success state
    btn.classList.add('copied')
    const originalHtml = btn.innerHTML
    
    // Simple checkmark icon
    btn.innerHTML = '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="20 6 9 17 4 12"></polyline></svg>'
    
    setTimeout(() => {
      btn.classList.remove('copied')
      btn.innerHTML = originalHtml
    }, 2000)
  } catch (err) {
    console.error('Failed to copy:', err)
  }
}
</script>

<style scoped>
.page-wrapper {
  max-width: 800px;
  margin: 0 auto;
  position: relative;
}

.article-container {
  width: 100%;
  margin: 30px 0;
  padding: 40px;
  background: var(--color-background);
  min-height: 100vh;
  border-radius: 16px;
  box-shadow: 0 4px 20px rgba(0,0,0,0.05);
}

.toc-sidebar {
  position: absolute;
  left: 100%;
  top: 80px; /* Align with article margin-top */
  bottom: 0;
  width: 250px;
  margin-left: 20px;
  display: none;
}

@media (min-width: 1350px) {
  .toc-sidebar {
    display: block;
  }
}

.toc-content {
  position: sticky;
  top: 100px;
  /* background: var(--color-background); Remove bg so marker can be seen if behind? Or put marker inside */
  /* Actually keep bg but ensure marker is visible. Relative pos needed for marker */
  background: var(--color-background);
  padding: 20px;
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(0,0,0,0.05);
  max-height: calc(100vh - 120px);
  overflow-y: auto;
  position: sticky; /* Repeated in search block, keeping it safe */
}

.active-marker {
  position: absolute;
  left: 0;
  width: 4px;
  background-color: var(--color-primary, #007bff);
  transition: top 0.3s ease, height 0.3s ease;
  border-radius: 0 2px 2px 0;
}

.toc-content h3 {
  margin-top: 0;
  margin-bottom: 15px;
  font-size: 1.1em;
  color: var(--color-text);
  font-weight: 600;
  padding-bottom: 10px;
  border-bottom: 1px solid #eee;
}

.toc-content ul {
  list-style: none;
  padding: 0;
  margin: 0;
}

.toc-content li {
  margin-bottom: 8px;
  line-height: 1.4;
}

.toc-content a {
  text-decoration: none;
  color: #666;
  font-size: 0.9em;
  transition: all 0.2s;
  display: block;
  padding-left: 15px; /* Increased padding since we removed border */
  position: relative;
}

.toc-content a:hover {
  color: var(--color-primary, #007bff);
  transform: translateX(5px); /* Hover move animation */
}

.toc-content a.active {
  color: var(--color-primary, #007bff);
  font-weight: 500;
}

/* Indentation for nested levels */
.toc-level-1 { padding-left: 0; }
.toc-level-2 { padding-left: 0; }
.toc-level-3 { padding-left: 15px; }
.toc-level-4 { padding-left: 30px; }
.toc-level-5 { padding-left: 45px; }
.toc-level-6 { padding-left: 60px; }

.article-header {
  margin-bottom: 40px;
  text-align: center;
  border-bottom: 1px solid #eee;
  padding-bottom: 20px;
}

.article-header h1 {
  font-size: 2.5em;
  margin-bottom: 20px;
  color: var(--color-text);
}

.meta {
  color: #666;
  margin-bottom: 10px;
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 15px;
}

.category {
  padding: 2px 8px;
  background: var(--color-light);
  color: white;
  border-radius: 4px;
  font-size: 0.9em;
}

.tags {
    display: flex;
    justify-content: center;
    gap: 10px;
}
.tag {
    color: var(--color-light);
    font-size: 0.9em;
}

/* Basic Markdown Styles */
:deep(.markdown-body) {
  line-height: 1.8;
  color: var(--color-text);
  font-size: 1.1em;
}

:deep(.markdown-body h1),
:deep(.markdown-body h2),
:deep(.markdown-body h3) {
  margin-top: 32px;
  margin-bottom: 16px;
  font-weight: 600;
  line-height: 1.25;
  color: var(--color-text);
}

:deep(.markdown-body h2) {
    border-bottom: 1px solid #eee;
    padding-bottom: 0.3em;
}

:deep(.markdown-body p) {
  margin-bottom: 20px;
}

:deep(.markdown-body a) {
    color: var(--color-light);
    text-decoration: none;
}
:deep(.markdown-body a:hover) {
    text-decoration: underline;
}

:deep(.markdown-body code) {
  padding: 0.2em 0.4em;
  margin: 0;
  font-size: 85%;
  background-color: rgba(127, 127, 127, 0.1);
  border-radius: 3px;
  font-family: monospace;
}

/* Code Block Container Styles */
:deep(.code-block-wrapper) {
  margin-bottom: 1.5rem;
  border-radius: 8px;
  overflow: hidden;
  background-color: #282c34; /* Match atom-one-dark bg */
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  color: #dfe2e5;
}

:deep(.code-header) {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 16px;
  background-color: #21252b;
  border-bottom: 1px solid #333;
  font-family: monospace;
}

:deep(.code-lang) {
  font-size: 0.85em;
  color: #abb2bf;
  text-transform: uppercase;
  font-weight: 600;
}

:deep(.copy-code-btn) {
  background: transparent;
  border: none;
  color: #abb2bf;
  cursor: pointer;
  padding: 4px;
  border-radius: 4px;
  transition: all 0.2s ease;
  display: flex;
  align-items: center;
  justify-content: center;
}

:deep(.copy-code-btn:hover) {
  background-color: rgba(255, 255, 255, 0.1);
  color: white;
}

:deep(.copy-code-btn.copied) {
  color: #98c379; /* Green for success */
}

:deep(.markdown-body pre) {
  margin: 0;
  padding: 1rem;
  overflow: auto;
  font-size: 0.9em;
  line-height: 1.5;
  background-color: transparent; /* Let wrapper handle bg */
  border-radius: 0 0 8px 8px;
}

:deep(.markdown-body pre code) {
  background-color: transparent;
  padding: 0;
  color: inherit;
  font-family: 'Fira Code', 'Consolas', monospace;
}

/* Scrollbar for code blocks */
:deep(.markdown-body pre::-webkit-scrollbar) {
  height: 8px;
}

:deep(.markdown-body pre::-webkit-scrollbar-track) {
  background: #21252b;
}

:deep(.markdown-body pre::-webkit-scrollbar-thumb) {
  background: #4b5363;
  border-radius: 4px;
}

:deep(.markdown-body pre::-webkit-scrollbar-thumb:hover) {
  background: #5c6579;
}

:deep(.markdown-body blockquote) {
    margin: 0 0 20px 0;
    padding: 0 1em;
    color: #6a737d;
    border-left: 0.25em solid #dfe2e5;
}

:deep(.markdown-body ul),
:deep(.markdown-body ol) {
    padding-left: 2em;
    margin-bottom: 20px;
}

:deep(.markdown-body img) {
    max-width: 100%;
    border-radius: 4px;
    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
}

.loading {
    text-align: center;
    padding: 50px;
    color: #666;
}
</style>

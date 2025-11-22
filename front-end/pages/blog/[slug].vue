<template>
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
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { getArticleBySlug, markdownToHtml } from '@/utils/blogUtils'
import 'highlight.js/styles/atom-one-dark.css'

const route = useRoute()
const article = ref(null)
const contentHtml = ref('')

onMounted(async () => {
  const slug = route.params.slug
  const data = getArticleBySlug(slug)
  
  if (data) {
    article.value = data
    contentHtml.value = await markdownToHtml(data.content)
  }
})

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
.article-container {
  max-width: 800px;
  margin: 80px auto;
  padding: 40px;
  background: var(--color-background);
  min-height: 100vh;
  border-radius: 16px;
  box-shadow: 0 4px 20px rgba(0,0,0,0.05);
}

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

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
      <div class="markdown-body" v-html="contentHtml"></div>
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

:deep(.markdown-body pre) {
  padding: 16px;
  overflow: auto;
  font-size: 85%;
  line-height: 1.45;
  background-color: #f6f8fa;
  border-radius: 6px;
  margin-bottom: 20px;
}
/* Dark mode adjustments for code blocks if needed, simplified here */
@media (prefers-color-scheme: dark) {
    :deep(.markdown-body pre) {
        background-color: #2d2d2d;
    }
}

:deep(.markdown-body pre code) {
  background-color: transparent;
  padding: 0;
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

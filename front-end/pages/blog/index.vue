<template>
  <div class="blog-container">
    <div class="article-list">
      <div v-for="article in articles" :key="article.slug" class="article-card" @click="router.push(`/blog/${article.slug}`)">
        <h2>{{ article.title }}</h2>
        <div class="meta">
          <span class="date">{{ article.date }}</span>
          <span v-if="article.categories" class="category">{{ article.categories }}</span>
        </div>
        <div class="excerpt markdown-body" v-if="article.excerpt" v-html="article.excerpt"></div>
        <div class="tags" v-if="article.tags && article.tags.length">
          <span v-for="tag in article.tags" :key="tag" class="tag">#{{ tag }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { getAllArticles } from '@/utils/blogUtils'
import 'highlight.js/styles/atom-one-dark.css'

const router = useRouter()
const articles = ref([])

onMounted(() => {
  articles.value = getAllArticles()
})
</script>

<style scoped>
.blog-container {
  max-width: 800px;
  margin: 0px auto;
  padding-top: 80px;
}

h1 {
  text-align: center;
  margin-bottom: 40px;
  color: var(--color-text);
}

.article-list {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.article-card {
  padding: 20px;
  border-radius: 12px;
  background: var(--color-background);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  cursor: pointer;
  transition: all 0.3s ease;
  border: 1px solid transparent;
}

.article-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.15);
  border-color: var(--color-light);
}

.article-card h2 {
  margin: 0 0 10px 0;
  color: var(--color-text);
  font-size: 1.5em;
}

.meta {
  display: flex;
  align-items: center;
  gap: 10px;
  color: #666;
  font-size: 0.9em;
  margin-bottom: 10px;
}

.excerpt {
  color: #555;
  font-size: 1em;
  line-height: 1.6;
  margin-bottom: 15px;
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
  text-overflow: ellipsis;
}

/* Reset markdown paragraph margins inside excerpt to avoid huge gaps */
.excerpt :deep(p) {
  margin: 0 0 10px 0;
}
.excerpt :deep(p:last-child) {
  margin-bottom: 0;
}

.category {
  padding: 2px 8px;
  background: var(--color-light);
  color: var(--color-background);
  border-radius: 4px;
  font-size: 0.8em;
}

.tags {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
}

.tag {
  color: var(--color-light);
  font-size: 0.85em;
}
</style>

import { marked } from 'marked'
import hljs from 'highlight.js'

export interface ArticleMeta {
  title: string
  date: string
  categories?: string
  tags?: string[]
  slug: string
}

export interface Article extends ArticleMeta {
  content: string
  excerpt: string
}

// Simple Front Matter Parser (Replacing gray-matter for browser compatibility)
function parseFrontMatter(text: string) {
  const pattern = /^---\r?\n([\s\S]*?)\r?\n---\r?\n([\s\S]*)$/;
  const match = text.match(pattern);
  
  if (!match) {
    return {
      data: {},
      content: text
    };
  }

  const yamlBlock = match[1];
  const content = match[2];
  const data: Record<string, any> = {};

  yamlBlock.split(/\r?\n/).forEach(line => {
    if (!line.trim() || line.trim().startsWith('#')) return;
    
    const parts = line.split(':');
    if (parts.length >= 2) {
      const key = parts[0].trim();
      let value = parts.slice(1).join(':').trim();
      
      // Handle basic types
      if (value.startsWith('[') && value.endsWith(']')) {
        // Array: [a, b, c]
        const arrayContent = value.substring(1, value.length - 1);
        data[key] = arrayContent.split(',').map(item => item.trim());
      } else {
        // String/Date
        data[key] = value;
      }
    }
  });

  return { data, content };
}

// Import all markdown files as raw strings
const articleFiles = import.meta.glob('~/assets/articles/*.md', { as: 'raw', eager: true })

// 获取所有文章元数据
export function getAllArticles(): ArticleMeta[] {
  try {
    const articles = Object.keys(articleFiles).map((filePath) => {
      const fileContent = articleFiles[filePath] as string
      const { data } = parseFrontMatter(fileContent)
      const slug = filePath.split('/').pop()?.replace(/\.md$/, '') || ''
      
      return {
        slug,
        title: data.title || slug,
        date: data.date || data.data || '',
        categories: data.categories,
        tags: data.tags || []
      }
    })

    return articles.sort((a, b) => {
      // 按日期降序排列
      return new Date(b.date).getTime() - new Date(a.date).getTime()
    })
  } catch (error) {
    console.error('Error reading articles:', error)
    return []
  }
}

// 根据slug获取单篇文章
export function getArticleBySlug(slug: string): Article | null {
  try {
    // Find the file path that ends with /slug.md
    const filePath = Object.keys(articleFiles).find(path => path.endsWith(`/${slug}.md`))
    
    if (!filePath) {
      return null
    }

    const fileContents = articleFiles[filePath] as string
    const { data, content } = parseFrontMatter(fileContents)

    // 提取摘要（<!-- more -->之前的内容）
    const excerptMatch = content.match(/^([\s\S]*?)<!-- more -->/)
    const excerpt = excerptMatch ? excerptMatch[1].trim() : content.substring(0, 200)

    return {
      slug,
      title: data.title || slug,
      date: data.date || data.data || '',
      categories: data.categories,
      tags: data.tags || [],
      content,
      excerpt
    }
  } catch (error) {
    console.error(`Error reading article ${slug}:`, error)
    return null
  }
}

// Configure marked with highlight.js and custom renderer
const renderer = new marked.Renderer()

renderer.code = ({ text, lang }) => {
  const language = hljs.getLanguage(lang || '') ? lang : 'plaintext'
  const highlighted = hljs.highlight(text, { language: language || 'plaintext' }).value
  
  return `
<div class="code-block-wrapper">
  <div class="code-header">
    <span class="code-lang">${language || 'text'}</span>
    <button class="copy-code-btn" aria-label="Copy code">
      <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
        <rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect>
        <path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path>
      </svg>
    </button>
  </div>
  <pre><code class="hljs language-${language}">${highlighted}</code></pre>
</div>`
}

marked.use({ renderer })

// 将Markdown转换为HTML
export async function markdownToHtml(markdown: string): Promise<string> {
  return marked.parse(markdown)
}

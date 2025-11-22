import { marked } from 'marked'

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

// 将Markdown转换为HTML
export async function markdownToHtml(markdown: string): Promise<string> {
  return marked.parse(markdown)
}

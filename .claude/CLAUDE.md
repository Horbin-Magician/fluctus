# Fluctus 项目概览 (云边小铺)

## 项目简介

个人全栈 Web 应用，名为"云边小铺"。前后端分离架构，包含搜索引擎聚合、日历、旅行日记、秘密留言、博客等功能模块。

## 技术栈

| 层级 | 技术 | 版本要求 |
|------|------|----------|
| 前端框架 | Nuxt 3 (SPA 模式, SSR 关闭) | ^3.17.5 |
| UI 框架 | Naive UI | ^2.41.0 |
| 视图层 | Vue 3 + Vue Router 4 | ^3.5.16 |
| 构建工具 | Vite | ^6.3.5 |
| 包管理器 | Yarn 1.x | 1.22.22 |
| 后端框架 | Flask | >=3.1.1 |
| Python 版本 | Python | >=3.11 |
| 数据库 | SQLite | - |
| 地图服务 | 高德地图 (AMap) | ^1.0.1 |
| Markdown | marked + highlight.js + gray-matter | - |

## 目录结构

```
fluctus/
├── back-end/
│   ├── application.py              # Flask 入口
│   ├── pyproject.toml              # Python 依赖 (uv 管理)
│   ├── www/
│   │   ├── __init__.py             # Flask app 初始化
│   │   ├── settings.py             # 配置 (SECRET_KEY, DB 路径等)
│   │   ├── decorators.py           # 装饰器 (速率限制)
│   │   └── bp_api/
│   │       ├── __init__.py         # Blueprint 注册, 路由汇总
│   │       └── views/
│   │           ├── login.py        # 登录/注册/JWT 认证
│   │           ├── user.py         # 用户管理
│   │           ├── authority.py    # 角色权限管理
│   │           ├── secret.py       # 秘密留言
│   │           ├── travel.py       # 旅行日记 (开发中)
│   │           └── searcher/
│   │               └── baidu.py    # 百度搜索代理
│   ├── tools/
│   │   └── dbControllers/
│   │       ├── BaseDbController.py      # SQLite 基类
│   │       ├── SecretDbController.py    # 秘密留言 DB
│   │       ├── TravelDbController.py    # 旅行日记 DB (开发中)
│   │       └── FavouritesDbController.py # 收藏 DB
│   └── datas/
│       ├── base.sqlite             # 用户/权限数据
│       ├── travel.sqlite           # 旅行日记数据
│       └── secret                  # 每日秘密 (文本文件)
│
├── front-end/
│   ├── nuxt.config.ts              # Nuxt 配置 (SPA, 代理 /api -> :5000)
│   ├── package.json                # 前端依赖
│   ├── app.vue                     # 根组件
│   ├── pages/
│   │   ├── index.vue               # 首页 (搜索引擎聚合)
│   │   ├── Calendar.vue            # 日历 (含农历/月相)
│   │   ├── Travel.vue              # 旅行日记 (开发中)
│   │   ├── Secret.vue              # 秘密留言
│   │   ├── Admin.vue               # 后台管理
│   │   ├── About.vue               # 关于页面
│   │   ├── Repository.vue          # 仓库 (WIP)
│   │   └── blog/
│   │       ├── index.vue           # 博客列表
│   │       └── [slug].vue          # 博客详情
│   ├── components/
│   │   ├── AppHeader.vue           # 顶部导航栏
│   │   ├── AppFooter.vue           # 底部栏
│   │   ├── MapContainer.vue        # 高德地图组件
│   │   ├── ThemeToggle.vue         # 深色/浅色主题切换
│   │   ├── SearchSourceSelector.vue # 搜索引擎选择
│   │   └── AppAlert.vue            # 全局提示
│   ├── api/
│   │   ├── ajax.ts                 # HTTP 客户端 (fetch 封装)
│   │   ├── baseAPI.ts              # 用户/权限 API
│   │   ├── searchAPI.ts            # 搜索 API
│   │   ├── secretAPI.ts            # 秘密留言 API
│   │   ├── types.ts                # TypeScript 类型定义
│   │   └── index.ts                # API 统一导出
│   ├── composables/
│   │   └── useSearch.ts            # 搜索逻辑 composable
│   ├── utils/
│   │   ├── userUtils.js            # 用户认证/JWT 管理
│   │   ├── storageUtils.js         # LocalStorage 封装
│   │   ├── blogUtils.ts            # Markdown 博客解析
│   │   ├── calendarUtils.js        # 农历/月相计算
│   │   └── memoryUtils.js          # 内存状态管理
│   ├── middleware/
│   │   └── auth.ts                 # 路由鉴权守卫
│   ├── plugins/
│   │   └── initUser.client.ts      # 客户端用户初始化
│   ├── content/blog/               # Markdown 博客文章
│   └── assets/css/                 # 全局样式
│       └── global.css
```

## API 路由

| 方法 | 路径 | 功能 |
|------|------|------|
| POST | `/api/login` | 用户登录 (JWT) |
| POST | `/api/register` | 用户注册 |
| GET | `/api/user/info` | 获取当前用户信息 |
| GET | `/api/user/list` | 获取用户列表 (管理员) |
| PUT | `/api/user/<id>` | 更新用户信息 |
| DELETE | `/api/user/<id>` | 删除用户 |
| GET | `/api/authority/list` | 获取角色列表 |
| POST | `/api/authority` | 创建角色 |
| PUT | `/api/authority/<id>` | 更新角色 |
| DELETE | `/api/authority/<id>` | 删除角色 |
| GET | `/api/secret` | 获取今日秘密 |
| POST | `/api/secret` | 提交秘密留言 |
| GET | `/api/travel/list` | 获取旅行日记列表 |
| POST | `/api/travel` | 创建旅行日记 |
| GET | `/api/searcher/baidu` | 百度搜索建议代理 |

## 认证机制

- JWT Token 认证，存储在 LocalStorage
- 密码使用 MD5 哈希
- 登录接口有速率限制 (decorators.py 中的 rate_limit 装饰器，线程安全)
- 前端 auth middleware 保护需要登录的页面 (如 Admin)

## 数据库结构

**base.sqlite:**
- `user` 表: id, username, password, authority_id, create_time
- `authority` 表: id, name, description, create_time

**travel.sqlite:**
- `travel` 表: id, title, content, location, lng, lat, images, create_time

## 开发与运行

```bash
# 前端开发
cd front-end && yarn dev        # 启动开发服务器 (默认 :3000)

# 后端开发
cd back-end && uv run python application.py  # 启动 Flask (默认 :5000)

# 前端构建
cd front-end && yarn build
```

- 开发时前端通过 Vite proxy 将 `/api` 请求转发到 `http://127.0.0.1:5000`
- Python 依赖通过 `uv` 管理

## 功能模块概述

1. **搜索聚合** - 首页支持百度/必应/Google 搜索，百度有搜索建议代理
2. **日历** - 支持农历、月相显示的日历组件
3. **旅行日记** - 集成高德地图，支持地点标记和日记记录 (开发中)
4. **秘密留言** - 每日一条秘密留言，文本文件存储
5. **博客** - Markdown 文件驱动，支持代码高亮
6. **后台管理** - 用户管理、角色权限管理 (需管理员权限)
7. **主题切换** - 深色/浅色模式

## 当前开发状态

正在开发旅行日记 (Travel) 功能，涉及:
- `back-end/www/bp_api/views/travel.py` (新增)
- `back-end/tools/dbControllers/TravelDbController.py` (新增)
- `front-end/pages/Travel.vue` (修改中)
- `front-end/components/MapContainer.vue` (修改中)

---
title: 使用Hexo搭建个人博客
data: 2025-01-09 12:42:34
categories: 技术分享
tags: [博客, 部署]
---

# Hexo初体验

Hexo 是一个快速、简洁且功能强大的静态博客框架，常用于搭建个人博客、技术文档或小型网站。它基于 Node.js，使用 Markdown 文件生成静态网页，依赖于其高效的生成流程和丰富的插件及主题生态，受到许多开发者和写作爱好者的喜爱。

本文旨在介绍笔者搭建 Hexo 的关键过程，以供参考。

<!-- more -->

## 环境准备

Hexo需要安装下列应用程序：

- [Git](http://git-scm.com/)
- [Node.js](http://nodejs.org/) (Node.js 版本需不低于 10.13，建议使用 Node.js 12.0 及以上版本)

### 安装Git

- Windows：下载并安装 [git](https://git-scm.com/download/win)。
- Mac：使用 [Homebrew](http://mxcl.github.com/homebrew/), [MacPorts](http://www.macports.org/) 或者下载 [安装程序](http://sourceforge.net/projects/git-osx-installer/)。
- Linux (Ubuntu, Debian)：`sudo apt-get install git-core`
- Linux (Fedora, Red Hat, CentOS)：`sudo yum install git-core`

### 安装Node.js

Node.js 为大多数平台提供了官方的 [安装程序](https://nodejs.org/zh-cn/download/)。

其它的安装方法：

- Windows：通过 [nvs](https://github.com/jasongin/nvs/)（推荐）或者 [nvm](https://github.com/nvm-sh/nvm) 安装（我是通过自带的 [WinGet](https://learn.microsoft.com/zh-cn/windows/package-manager/winget/) 安装的）。
- Mac：使用 [Homebrew](https://brew.sh/) 或 [MacPorts](http://www.macports.org/) 安装。
- Linux（DEB/RPM-based）：从 [NodeSource](https://github.com/nodesource/distributions) 安装。
- 其它：使用相应的软件包管理器进行安装。 可以参考由 Node.js 提供的 [指导](https://nodejs.org/en/download/package-manager/)。

对于 Mac 和 Linux 同样建议使用 nvs 或者 nvm，以避免可能会出现的权限问题。

## Hexo安装与博客初始化

### 安装Hexo

所有必备的应用程序安装完成后，即可使用 npm 安装 Hexo。

```bash
npm install -g hexo-cli
```

> 当然也可以仅局部安装 `hexo` 包，但首次使用或者你不清楚这意味着什么，推荐上述全局安装方式。

### 博客初始化

安装 Hexo 完成后，请执行下列命令，Hexo 将会在指定文件夹中新建所需要的文件。

```bash
hexo init <folder>
cd <folder>
npm install
```

初始化后，您的项目文件夹将如下所示：

```
.
├── _config.yml
├── package.json
├── scaffolds
├── source
|   ├── _drafts
|   └── _posts
└── themes
```

其中：

* _config.yml 是网站的 [配置](https://hexo.io/zh-cn/docs/configuration) 文件。
* package.json 是网站所使用的包信息。其中默认安装了如 [EJS](https://ejs.co/), [Stylus](http://learnboost.github.io/stylus/) 和 [Markdown](http://daringfireball.net/projects/markdown/) 渲染引擎等包。
* scaffolds 是 [模版](https://hexo.io/zh-cn/docs/writing#模版（Scaffold）) 文件夹。当新建文章时，Hexo 会根据 scaffold 来创建文件。
* source 是资源文件夹。里面存放了所有用户资源，如文章、图片等。除 `_posts` 文件夹之外，开头命名为 `_` (下划线)的文件 / 文件夹和隐藏的文件将会被忽略。 Markdown 和 HTML 文件会被解析并放到 `public` 文件夹，而其他文件会被拷贝过去。
* themes 是 [主题](https://hexo.io/zh-cn/docs/themes) 文件夹。 Hexo 会根据主题来生成静态页面。

## 相关命令

初始化项目并进入项目文件夹后，我们可以在该路径下通过相关命令来操作博客。

> 这里只介绍相对常用的命令和参数，详细介绍请参考 [文档](https://hexo.io/zh-cn/docs/commands)。

### new

```bash
hexo new [layout] <title>
```

使用 `layout` 新建一篇名为 `title` 的文章。`layout` 可以为之前提到的模板文件夹 scaffolds 中的任何一种，默认有 draft（草稿）、page（页面）、post（文章）三种。如果没有设置 `layout` 的话，默认使用 [_config.yml](https://hexo.io/zh-cn/docs/configuration) 中的 `default_layout` 参数代替。 如果标题包含空格的话，请使用引号括起来。

| 选项              | 描述                            |
| :---------------- | :------------------------------ |
| `-p`, `--path`    | 文章的路径。 自定义文章的路径。 |
| `-r`, `--replace` | 如果存在的话，替换当前的文章。  |
| `-s`, `--slug`    | 文章别名。 自定义文章的 URL。   |

默认情况下，Hexo 会使用文章的标题来决定文章文件的路径。 对于独立页面来说，Hexo 会创建一个以标题为名字的目录，并在目录中放置一个 `index.md` 文件。 你可以使用 `--path` 参数来覆盖上述行为、自行决定文件的目录：

```
hexo new page --path about/me "About me"
```

以上命令会创建一个 `source/about/me.md` 文件，同时 Front Matter 中的 title 为 `"About me"`

### generate

```bash
hexo generate
```

生成静态文件。

| 选项                  | 描述                                         |
| :-------------------- | :------------------------------------------- |
| `-d`, `--deploy`      | 在生成完成后部署。                           |
| `-w`, `--watch`       | 监视文件变动                                 |
| `-b`, `--bail`        | 生成过程中如果发生任何未处理的异常则抛出异常 |
| `-f`, `--force`       | 强制重新生成                                 |
| `-c`, `--concurrency` | 要同时生成的文件的最大数量。 默认无限制      |

### publish

```bash
hexo publish [layout] <filename>
```

发表草稿。

### server

```bash
hexo server
```

启动服务器。 默认情况下，访问网址为： `http://localhost:4000/`。

| 选项             | 描述                               |
| :--------------- | :--------------------------------- |
| `-p`, `--port`   | 重设端口                           |
| `-s`, `--static` | 只使用静态文件                     |
| `-l`, `--log`    | 启用日志。 Override logger format. |

### deploy

```bash
hexo deploy
```

部署你的网站。

| 选项               | 描述         |
| :----------------- | :----------- |
| `-g`, `--generate` | 在部署前生成 |

### clean

```bash
hexo clean
```

清除缓存文件 (`db.json`) 和已生成的静态文件 (`public`)。

# NexT主题

Hexo 的默认主题是非常简陋的，但幸运的是 Hexo 可以很容易地更换主题，社区也有很多优秀的主题可供选择。笔者选择的是以简洁著称的 [NexT 主题](https://github.com/next-theme/hexo-theme-next)。

## 安装

Hexo 安装主题非常简单，只需要把主题文件放入 themes 目录即可。官方推荐的方式是直接使用git将项目克隆到 themes 目录，即使用：

```bash
git clone https://github.com/next-theme/hexo-theme-next themes/next
```

但是该方法会同时下载 NexT 的 git 相关文件，这似乎会影响后续使用 git 对自己博客的管理，因此笔者选择直接下载项目代码后手动解压到 themes/next 的方式。这两种方式唯一的区别是后者没有包括 NexT 的 git 相关文件。

## 使用与设置

上一步完成后，需要在 Hexo 设置中将主题修改为 `next`， 即打开 `_config.yml` 文件，修改下面一行：

``````yaml
theme: next
``````

这时再运行博客，我们就能看到更改主题后的样子。

NexT 主题也有很多可以自定义的属性，最简单地，我们可以直接修改 `themes/next` 文件夹中的 `_config.yml`，但是这不利于后续更新主题的同时也因与 Hexo 本身配置分属两地而不利于管理。因此这里推荐的方式是在博客根目录新建一个名为 `_config.next.yml` 的配置文件，并把 `themes/next/_config.yml` 中的内容拷贝进来。后续我们只需要修改 `_config.next.yml` 即可。Hexo 会自动识别该文件，并覆盖相应主题目录下的配置。

具体的配置参数参考 [NexT官方文档](https://theme-next.js.org/docs/)。

# 部署到服务器

经过上述步骤后，我们就拥有了一个可以在本地运行的博客服务器。有经验的人应该可以很快地把它部署到自己的服务器，或者像是[GitHub Pages](https://pages.github.com/)，[Vercel](https://vercel.com/horbin-magicians-projects)，[Cloudflare](https://www.cloudflare.com/zh-cn/) 等代理平台中。本文并不计划讲述这部分内容，而是记录一下笔者通过 [GitHub Actions](https://github.com/features/actions) 实现自动部署的方式。其实 Hexo 自带了部署功能，但是如果本就计划用 GitHub 管理博客网站，不如直接用 GitHub Actions 来的方便。

具体方式也很简单，只需要在 `.github/workflows` 中创建一个workflows，这里将它命名为 `build.yml`，具体内容如下：

``````yaml
name: Build and deploy to aliyun

on:
  push:
    branches: ['master']
  workflow_dispatch:

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout
        uses: actions/checkout@v3
      - name: Setup Node
        uses: actions/setup-node@v3
        with:
          node-version: 23
      - name: Install dependencies and build
        run: |
          npm install
          npm run build
      - name: Deploy web to aliyun
        uses: easingthemes/ssh-deploy@v3
        with:
          SSH_PRIVATE_KEY: ${{ secrets.ALIYUN_SEVER_KEY }}
          ARGS: "-avz --delete"
          SOURCE: "public/"
          REMOTE_HOST: "blog_url"
          REMOTE_USER: "user_name"
          TARGET: "/path/of/your/blog/"
``````

具体细节如有疑问请询问AI，这里的工作流主要是当 push 代码到 GitHub 或者手动触发工作流后：启动 ubuntu 镜像、拉取最新代码、安装 Node.js、安装代码所需库、构建网站、最后将构建后的网站（public目录下）上传到服务器中的目标目录。

需要注意的是，上传这一步需要用到密钥登录，其中 `${{ secrets.ALIYUN_SEVER_KEY }}` 就是需要传入的密钥，这里使用的是 GitHub 的 Repository secrets 以防止暴露。其他的例如 `blog_url`、`user_name`、`/path/of/your/blog/` 请修改为你所使用服务器的具体值。

# 参考文献

* [Hexo官方文档](https://hexo.io/zh-cn/docs/)
* [NexT主题文档](https://theme-next.js.org/docs/)

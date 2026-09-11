# ☔ こさめ (Kosame) Maid Blog Archive & Static Site Generator

> 秋葉原本店5階所属 メイド「**こさめ**」のブログアーカイブ（2022年11月〜2024年7月・卒業）。  
> @home cafe 官方 API 全量 295 篇博文数据与照片的爬虫与 GitHub Pages 静态网站生成器。

---

## 🌟 核心特性

- 🎯 **一键抓取与生成**：自动对接 @home cafe 会员系统 API，完整获取博文标题、正文、发布时间、配图及个人档案。
- 💾 **断点续传与缓存**：单篇博文独立缓存至 `data/raw_posts/`，支持增量更新，中断无需从头开始。
- 🖼️ **配图本地化保存**：支持一键将博文正文配图与头像下载至本地，消除外链失效风险。
- 🎨 **治愈系现代 UI 设计**：
  - 以「こさめ（小雨・水滴）」为主题的轻量现代设计，兼顾萌系可爱风格与极佳的阅读质感。
  - **实时前端搜索**：即时按标题和正文摘要检索文章。
  - **年份/全期间筛选**：2022年、2023年、2024年快速筛选与排序（最新 / 最早）。
  - **年代时间轴归档（Timeline Archive）**：清晰展现按年、月分类的完整成长轨迹。
  - **图片灯箱（Lightbox）**：点击文章内任意图片全屏放大，支持 ESC 键退出。
  - **阅读进度条与回到顶部**：平滑滚动体验。
- 🚀 **零配置 GitHub Pages**：生成产物直接输出到 `docs/` 目录，并包含 `.nojekyll`，推送至 GitHub 后开箱即用。

---

## 📁 目录结构

```text
kosame-blog/
├── crawler.py             # 博客数据抓取脚本（支持断点续传、图片下载、清洗HTML）
├── generate.py            # 静态站点生成器（Jinja2 模板渲染至 docs/）
├── build.py               # 一键化入口脚本（抓取 + 生成 + 本地预览）
├── requirements.txt       # Python 依赖清单
├── templates/             # 页面模板 (Jinja2)
│   ├── base.html          # 全局布局底板（导航栏、页脚、背景动画、灯箱组件）
│   ├── index.html         # 首页（个人卡片、搜索筛选、文章网格卡片）
│   ├── post.html          # 单篇博文详情页（面包屑、排版、上一篇/下一篇）
│   ├── archive.html       # 年代别时间轴归档页
│   └── about.html         # 女仆个人详细资料页
├── static/                # 静态静态资源
│   ├── css/style.css      # 现代高颜值样式表
│   └── js/main.js         # 前端交互（搜索过滤、阅读进度、灯箱）
├── data/                  # 抓取的原始与清洗数据
│   ├── maid.json          # 女仆个人档案数据
│   ├── posts.json         # 295篇清洗后文章索引与内容
│   └── raw_posts/         # 各篇独立原始 JSON 缓存
└── docs/                  # 【GitHub Pages 发布目录】
    ├── index.html
    ├── archive.html
    ├── about.html
    ├── posts/             # 295 篇静态 HTML
    └── static/
```

---

## 🛠️ 环境准备

建议使用 Python 3.8 及以上版本。

安装依赖：
```bash
pip install -r requirements.txt
```

依赖项非常轻量：
- `requests` (API 请求与下载)
- `jinja2` (静态模板渲染)
- `beautifulsoup4` (HTML 解析与清洗)
- `tqdm` (终端美观进度条)

---

## 🚀 使用方法

### 1. 一键全流程（抓取 + 生成静态网站）

```bash
python build.py
```

### 2. 下载所有配图到本地（推荐长期保存）

如果你希望将所有文章中的图片和头像全部下载到本地，使网站彻底脱机独立运行：
```bash
python build.py --download-images
```

### 3. 本地预览生成的网站

构建完成后自动开启本地 HTTP 服务器预览：
```bash
python build.py --skip-crawl --serve
```
然后在浏览器中打开 [http://localhost:8000](http://localhost:8000) 即可查看效果。

### 4. 仅重新生成网页（不重新抓取）

如果已抓取过数据，修改了模板或样式后仅需重新编译网页：
```bash
python generate.py
```

---

## 🌐 部署至 GitHub Pages 教程

1. **新建 GitHub 仓库**：
   在 GitHub 上创建一个新的仓库（例如 `kosame-blog`）。

2. **提交并推送到 GitHub**：
   ```bash
   git init
   git add .
   git commit -m "feat: Kosame maid blog archive and static site"
   git branch -M main
   git remote add origin https://github.com/<你的用户名>/kosame-blog.git
   git push -u origin main
   ```

3. **启用 GitHub Pages**：
   - 打开仓库页面的 **Settings**（设置） > **Pages**。
   - 在 **Build and deployment** 下：
     - **Source**: 选择 `Deploy from a branch`。
     - **Branch**: 选择 `main` 分支，文件夹选择 `/docs`。
     - 点击 **Save**（保存）。

4. **访问你的站点**：
   等待 1~2 分钟部署完成后，即可通过 `https://<你的用户名>.github.io/kosame-blog/` 访问！

---

## 💡 进阶参数说明

`build.py` 与 `crawler.py` 支持以下命令行参数：

| 参数 | 默认值 | 作用说明 |
| :--- | :--- | :--- |
| `--maid-id` | `1598` | 目标女仆 ID（固定为こさめ的 1598） |
| `--data-dir` | `data` | 数据存放目录 |
| `--output-dir` | `docs` | 静态网站生成目标目录（默认 docs 适配 GitHub Pages） |
| `--download-images` | 否 | 下载文章中所有图片与头像到本地 |
| `--skip-crawl` | 否 | 跳过网络抓取，直接用现有数据生成页面 |
| `--limit N` | 全部 | 仅抓取前 N 篇博文（调试用） |
| `--force` | 否 | 忽略本地缓存，强制重新请求 API |
| `--serve` | 否 | 生成完毕后自动启动本地预览服务 |
| `--port` | `8000` | 本地预览服务端口 |

---

## 💖 致谢

- 数据来源：[@home cafe (あっとほぉーむカフェ)](https://www.cafe-athome.com/)
- 纪念女仆：秋葉原本店5階 **こさめ (Kosame)**
- 「きらきらあまつぶでご主人様・お嬢様のココロをうるおすこさめです☔️」
# kosame-blog

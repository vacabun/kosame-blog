# こさめ (Kosame) Blog Archive

@home cafe 秋葉原本店5階所属 メイド「こさめ」博客全量（295篇）爬虫与 GitHub Pages 静态站点生成器。

---

## 🛠️ 安装依赖

```bash
pip3 install -r requirements.txt
```

---

## 🚀 使用方法

### 1. 一键全流程（抓取 + 生成静态网站）

```bash
python3 build.py
```

### 2. 本地预览已生成的博客

```bash
python3 build.py --skip-crawl --serve
```
在浏览器中打开 [http://localhost:8000](http://localhost:8000) 即可访问。

### 3. 下载全部配图至本地（脱机保存）

```bash
python3 build.py --download-images
```

### 4. 仅重新生成静态页面（修改模板/样式后）

```bash
python3 generate.py
```

---

## 🌐 部署至 GitHub Pages

1. **推送代码至 GitHub**：
   ```bash
   git add .
   git commit -m "feat: build static site"
   git push
   ```

2. **配置 GitHub Pages**：
   - 打开仓库页面的 **Settings** > **Pages**
   - **Source** 选择 `Deploy from a branch`
   - **Branch** 选择 `main` 分支，文件夹选择 `/docs`
   - 点击 **Save** 保存

等待 1~2 分钟后即可通过 `https://<你的用户名>.github.io/kosame-blog/` 访问。

---

## ⚙️ 常用命令行参数

| 参数 | 说明 |
| :--- | :--- |
| `--skip-crawl` | 跳过爬取步骤，直接使用已有数据生成页面 |
| `--download-images` | 下载文章内的所有图片与头像到本地保存 |
| `--force` | 强制重新拉取所有博文数据（忽略缓存） |
| `--limit N` | 仅拉取前 N 篇博文（用于测试） |
| `--serve` | 生成后自动开启本地预览 HTTP 服务 |
| `--port 8000` | 指定本地预览服务的端口号 |

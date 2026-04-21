---
name: web-crawler
description: "网页爬虫工具，支持静态和动态页面爬取、媒体下载、反爬虫规避。激活条件：用户提到爬虫、爬取、crawler、scraper、抓取网页、下载媒体"
metadata:
  version: "1.0.0"
  openclaw:
    emoji: "🕷️"
---

# Web Crawler Skill

通用网页爬虫，可处理各种类型网站，包括带防护机制或动态渲染的页面。

## 快速使用

```bash
cd /home/node/.openclaw/workspace/web-crawler

# 爬取页面（需要先 cd 到项目目录）
node -e "
const crawler = require('./src/index.js');
const c = new crawler({maxPages: 1});
c.crawl('https://example.com').then(r => console.log(r.title));
"
```

## 核心功能

1. **静态页面爬取** - HTTP/HTTPS, cheerio解析, 代理支持
2. **动态页面爬取** - Puppeteer + 系统Chrome, JS渲染
3. **媒体下载** - 图片/视频/音频自动下载到 outputs/
4. **反爬虫规避** - UA轮换, 请求延迟, 代理轮换

## 配置

编辑 `config/default.json`:
- `crawling.maxDepth` - 最大爬取深度
- `crawling.maxPages` - 最大页面数  
- `media.enabled` - 启用媒体下载
- `antiBot.proxyList` - 代理列表 ["http://ip:port", ...]
- `puppeteer.executablePath` - Puppeteer 浏览器路径

## 代理配置

已配置代理:
- http://192.168.10.222:7890
- http://192.168.10.222:37890

代理故障自动降级到直接连接。

## 输出目录

- `outputs/html/` - HTML文件
- `outputs/text/` - 纯文本  
- `outputs/screenshots/` - 截图
- `outputs/media/` - 媒体文件
- `outputs/data.json` - 结构化数据

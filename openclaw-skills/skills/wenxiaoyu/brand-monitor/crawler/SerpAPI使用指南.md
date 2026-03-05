# SerpAPI 爬虫使用指南

## 简介

`search_crawler_serpapi.py` 是使用 SerpAPI 的最终版本爬虫，提供可靠的搜索功能。

## 特点

- ✅ 使用 SerpAPI 专业搜索服务
- ✅ 支持 Google、百度、Bing 等多个搜索引擎
- ✅ 自动识别平台（微博、小红书、知乎等）
- ✅ 支持时间过滤
- ✅ 提供 Mock 模式用于测试
- ✅ 稳定可靠，无需维护爬虫代码

## 快速开始

### 1. 获取 SerpAPI Key

访问 [https://serpapi.com/](https://serpapi.com/) 注册账号：

1. 点击 "Sign Up" 注册
2. 验证邮箱
3. 进入 Dashboard
4. 复制 API Key

**免费额度：** 100 次搜索/月

### 2. 设置环境变量

**Linux/macOS:**

```bash
export SERPAPI_KEY='your_api_key_here'
```

**Windows (CMD):**

```cmd
set SERPAPI_KEY=your_api_key_here
```

**Windows (PowerShell):**

```powershell
$env:SERPAPI_KEY='your_api_key_here'
```

**永久设置（添加到配置文件）:**

```bash
# Linux/macOS
echo 'export SERPAPI_KEY="your_api_key_here"' >> ~/.bashrc
source ~/.bashrc

# Windows (添加到系统环境变量)
# 控制面板 -> 系统 -> 高级系统设置 -> 环境变量
```

### 3. 运行爬虫

**基础用法：**

```bash
python search_crawler_serpapi.py "理想汽车" "weibo,xiaohongshu,zhihu" 10 24
```

**参数说明：**
- 参数1: 搜索关键词（必需）
- 参数2: 平台列表，逗号分隔（可选，默认：weibo,xiaohongshu,zhihu）
- 参数3: 每平台最大结果数（可选，默认：10）
- 参数4: 时间范围（小时，可选，默认：24）
- --mock: 使用模拟数据（可选）

## 使用示例

### 示例 1：搜索微博和知乎

```bash
python search_crawler_serpapi.py "理想汽车" "weibo,zhihu" 10 24
```

### 示例 2：搜索所有平台

```bash
python search_crawler_serpapi.py "理想汽车" "weibo,xiaohongshu,zhihu,autohome,dongchedi" 5 24
```

### 示例 3：搜索最近一周的内容

```bash
python search_crawler_serpapi.py "理想汽车" "weibo" 20 168
```

### 示例 4：使用 Mock 模式测试

```bash
python search_crawler_serpapi.py "理想汽车" "weibo,zhihu" 10 24 --mock
```

## 支持的平台

| 平台 | 标识符 | 说明 |
|------|--------|------|
| 微博 | weibo | 新浪微博 |
| 小红书 | xiaohongshu | 小红书笔记 |
| 知乎 | zhihu | 知乎问答 |
| 汽车之家 | autohome | 汽车之家论坛 |
| 懂车帝 | dongchedi | 懂车帝评测 |
| 易车网 | yiche | 易车网资讯 |
| 百度贴吧 | tieba | 百度贴吧 |
| 抖音 | douyin | 抖音短视频 |
| 快手 | kuaishou | 快手短视频 |

## 搜索引擎选择

通过 `SERPAPI_ENGINE` 环境变量选择搜索引擎：

```bash
# 使用 Google（默认，推荐）
export SERPAPI_ENGINE=google

# 使用百度（适合国内内容）
export SERPAPI_ENGINE=baidu

# 使用 Bing
export SERPAPI_ENGINE=bing
```

**推荐：**
- 国际内容：Google
- 国内内容：百度
- 平衡选择：Google

## 输出格式

爬虫输出 JSON 格式的结果：

```json
{
  "weibo": [
    {
      "platform": "weibo",
      "title": "标题",
      "content": "内容摘要",
      "url": "链接",
      "source": "serpapi_google",
      "publish_time": "发布时间",
      "author": "",
      "author_id": "",
      "followers": 0,
      "verified": false,
      "likes": 0,
      "comments": 0,
      "shares": 0
    }
  ],
  "xiaohongshu": [...],
  "zhihu": [...]
}
```

## 在 Skill 中使用

### 更新 prompts/monitor.md

将爬虫调用命令改为：

```bash
cd ~/.openclaw/workspace/skills/brand-monitor/crawler
python search_crawler_serpapi.py "{{brand_name}}" "{{platforms_list}}" 20 {{monitor_hours}}
```

### 配置环境变量

在 OpenClaw 配置中添加：

```bash
# 编辑 ~/.bashrc 或 ~/.zshrc
export SERPAPI_KEY='your_api_key_here'
export SERPAPI_ENGINE='google'
```

### 测试 Skill

```bash
openclaw agent --message "执行品牌监控"
```

## 成本计算

### SerpAPI 定价

| 计划 | 价格 | 搜索次数 | 适用场景 |
|------|------|---------|---------|
| Free | $0 | 100次/月 | 测试和小规模使用 |
| Developer | $50/月 | 5,000次/月 | 个人和小团队 |
| Production | $130/月 | 15,000次/月 | 中小企业 |
| Enterprise | 定制 | 定制 | 大型企业 |

### 使用成本估算

**每次监控消耗：**
- 监控 3 个平台 = 3 次搜索
- 监控 5 个平台 = 5 次搜索
- 监控 8 个平台 = 8 次搜索

**月度成本：**

| 监控频率 | 平台数 | 月搜索次数 | 推荐计划 | 月成本 |
|---------|--------|-----------|---------|--------|
| 每天 1 次 | 3 | 90 | Free | $0 |
| 每天 1 次 | 5 | 150 | Developer | $50 |
| 每天 2 次 | 3 | 180 | Developer | $50 |
| 每天 3 次 | 5 | 450 | Developer | $50 |
| 每小时 1 次 | 3 | 2,160 | Developer | $50 |

## 优化建议

### 1. 减少搜索次数

```bash
# 只监控重点平台
python search_crawler_serpapi.py "理想汽车" "weibo,xiaohongshu" 10 24
```

### 2. 调整监控频率

```bash
# 每天 1 次而不是每小时
0 9 * * * python search_crawler_serpapi.py "理想汽车" "weibo,xiaohongshu,zhihu" 10 24
```

### 3. 使用缓存

```python
# 缓存搜索结果，避免重复搜索
import json
import os
from datetime import datetime

cache_file = f"cache_{keyword}_{platform}_{date}.json"
if os.path.exists(cache_file):
    with open(cache_file) as f:
        return json.load(f)
```

### 4. 批量搜索

```bash
# 一次搜索多个关键词
python search_crawler_serpapi.py "理想汽车 OR 理想L9 OR 理想L8" "weibo" 20 24
```

## 故障排查

### 问题 1：API Key 错误

**错误信息：**
```
❌ 错误: 未设置 SERPAPI_KEY 环境变量
```

**解决方法：**
```bash
export SERPAPI_KEY='your_api_key_here'
```

### 问题 2：配额用完

**错误信息：**
```
SerpAPI 请求失败: 403 Forbidden
```

**解决方法：**
1. 检查配额使用情况：https://serpapi.com/dashboard
2. 升级到付费计划
3. 等待下月配额重置
4. 使用 Mock 模式测试：`--mock`

### 问题 3：搜索无结果

**可能原因：**
- 关键词太具体
- 时间范围太短
- 平台没有相关内容

**解决方法：**
```bash
# 扩大时间范围
python search_crawler_serpapi.py "理想汽车" "weibo" 20 168

# 使用更通用的关键词
python search_crawler_serpapi.py "理想" "weibo" 20 24

# 增加结果数量
python search_crawler_serpapi.py "理想汽车" "weibo" 50 24
```

### 问题 4：网络超时

**错误信息：**
```
SerpAPI 请求失败: Timeout
```

**解决方法：**
```bash
# 检查网络连接
ping serpapi.com

# 使用代理
export HTTP_PROXY=http://your-proxy:port
export HTTPS_PROXY=http://your-proxy:port
```

## 高级用法

### 1. 自定义搜索参数

修改 `search_crawler_serpapi.py`，添加更多搜索参数：

```python
search_params = {
    'location': 'China',  # 地理位置
    'hl': 'zh-cn',        # 语言
    'gl': 'cn',           # 国家
}
```

### 2. 结果后处理

```python
# 过滤低质量结果
results = [r for r in results if len(r['content']) > 50]

# 去重
seen_urls = set()
unique_results = []
for r in results:
    if r['url'] not in seen_urls:
        seen_urls.add(r['url'])
        unique_results.append(r)
```

### 3. 并行搜索

```python
from concurrent.futures import ThreadPoolExecutor

def search_platform_parallel(platforms):
    with ThreadPoolExecutor(max_workers=3) as executor:
        futures = {executor.submit(search_platform, p): p for p in platforms}
        results = {}
        for future in futures:
            platform = futures[future]
            results[platform] = future.result()
    return results
```

## 与其他方案对比

| 特性 | SerpAPI | 自建爬虫 | Brave API | Perplexity API |
|------|---------|---------|-----------|---------------|
| 稳定性 | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| 成本 | $50/月 | $0 | $0-5/月 | $2-5/月 |
| 维护成本 | 低 | 高 | 低 | 低 |
| 数据质量 | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| 平台覆盖 | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐ |
| 配置难度 | 简单 | 复杂 | 简单 | 简单 |

## 推荐使用场景

### 使用 SerpAPI 如果：

- ✅ 需要稳定可靠的搜索
- ✅ 预算充足（$50/月可接受）
- ✅ 不想维护爬虫代码
- ✅ 需要多平台覆盖
- ✅ 监控频率较高

### 使用其他方案如果：

- ❌ 预算有限 → 使用 Brave API（免费）
- ❌ 只需要简单搜索 → 使用 Perplexity API
- ❌ 需要特定平台数据 → 自建爬虫
- ❌ 只是测试 → 使用 Mock 模式

## 最佳实践

1. **开发阶段：** 使用 Mock 模式（`--mock`）
2. **测试阶段：** 使用免费额度测试
3. **生产阶段：** 升级到付费计划
4. **监控配额：** 定期检查使用情况
5. **优化搜索：** 只监控重点平台
6. **缓存结果：** 避免重复搜索
7. **错误处理：** 实现重试机制

## 相关文档

- [SerpAPI 官方文档](https://serpapi.com/docs)
- [SerpAPI 定价](https://serpapi.com/pricing)
- [SerpAPI Dashboard](https://serpapi.com/dashboard)
- `README-实际使用.md` - 方案对比
- `使用说明.md` - 快速开始

## 获取帮助

- SerpAPI 支持：support@serpapi.com
- 查看示例：https://serpapi.com/playground
- 社区论坛：https://forum.serpapi.com/

---

**现在你可以使用 SerpAPI 进行可靠的品牌监控了！** 🎉

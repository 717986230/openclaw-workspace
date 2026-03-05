---
name: suno
description: Suno AI 音乐创作助手 — 自动登录、创建歌曲、下载音频。当用户要求生成音乐、写歌、创作歌曲、用 Suno 生成 AI 音乐时使用。支持自定义歌词、音乐风格、自动解决 hCaptcha 验证码。
metadata: {"openclaw": {"emoji": "🎵", "requires": {"bins": ["google-chrome"]}}}
---

# 🎵 Suno AI 音乐创作助手

两大核心能力：**账号登录**（通过 Google OAuth）和 **歌曲创作**（自定义歌词+风格+下载）。

---

## 零、前置检查

每次操作前必须先执行环境检查：

```bash
bash {baseDir}/suno/check_env.sh
```

返回码：`0` = 正常已登录 → 可直接创建歌曲；`1` = 缺少依赖 → 安装依赖；`2` = 未登录 → 登录流程。

---

## 一、登录流程

**⚠️ 重要：不要在 skill 代码中硬编码账号密码！必须先询问用户的 Gmail 邮箱和密码。**

### 1.1 询问用户凭据

当需要登录时，**必须先向用户询问**：

> 需要登录 Suno.com（通过 Google 账号）。请提供：
> 1. **Gmail 邮箱地址**
> 2. **Gmail 密码**
>
> ⚠️ 你的凭据仅用于本次登录，不会被存储或传输到任何第三方。

### 1.2 执行登录

用户提供邮箱和密码后：

```bash
cd {baseDir}/suno
python3 suno_login.py --email "<用户邮箱>" --password "<用户密码>"
```

**登录模式说明**：
- **macOS/有GUI环境**：会弹出 Chrome 窗口，自动完成 Google 登录
- **Linux 云服务器**：自动使用 Xvfb 虚拟显示（需 `apt install xvfb && pip install PyVirtualDisplay`）
- **首次登录必须使用 GUI 模式**（默认行为），后续检查状态可以 headless

### 1.3 检查登录状态

```bash
cd {baseDir}/suno
python3 suno_login.py --check-only
```

退出码 `0` = 已登录，`2` = 未登录。

### 1.4 强制重新登录

```bash
cd {baseDir}/suno
python3 suno_login.py --email "<邮箱>" --password "<密码>" --force-login
```

---

## 二、创建歌曲

### 2.1 前置条件

1. 已完成登录（`suno_login.py --check-only` 返回 0）
2. 需要 **Gemini API Key**（用于自动解决 hCaptcha 验证码）

### 2.2 获取 Gemini API Key

如果用户没有 Gemini API Key，引导用户获取：

> 创建歌曲时 Suno 会弹出验证码，需要 Gemini API Key 来自动解决。
> 1. 访问 https://aistudio.google.com/app/apikey
> 2. 点击 "Create API key"
> 3. 复制生成的 Key

获取后保存到环境文件：

```bash
mkdir -p ~/.suno
echo "GEMINI_API_KEY=<用户的key>" > ~/.suno/.env
```

或通过环境变量：

```bash
export GEMINI_API_KEY="<用户的key>"
```

### 2.3 hCaptcha 兼容补丁

首次使用前需运行一次（Suno 使用自定义 hCaptcha 域名，需打补丁）：

```bash
cd {baseDir}/suno
python3 patch_hcaptcha.py
```

### 2.4 创建歌曲命令

```bash
cd {baseDir}/suno
python3 suno_create_song.py \
  --lyrics "<歌词内容>" \
  --style "<音乐风格标签>" \
  --title "<歌曲标题>" \
  --output-dir "<下载目录>"
```

也可以从文件读取歌词：

```bash
cd {baseDir}/suno
python3 suno_create_song.py \
  --lyrics-file "<歌词文件路径>" \
  --style "<音乐风格标签>" \
  --title "<歌曲标题>"
```

### 2.5 参数说明

| 参数 | 说明 | 必填 | 默认值 |
|------|------|:---:|--------|
| `--lyrics` | 歌词内容（与 `--lyrics-file` 二选一） | ✅ | - |
| `--lyrics-file` | 歌词文件路径（与 `--lyrics` 二选一） | ✅ | - |
| `--style` | 音乐风格标签（英文，逗号分隔） | ❌ | `rock, electric guitar, energetic, male vocals` |
| `--title` | 歌曲标题 | ❌ | `My Song` |
| `--output-dir` | MP3 下载目录 | ❌ | `{baseDir}/output_mp3` |
| `--gemini-key` | Gemini API Key（也可通过环境变量或 ~/.suno/.env） | ❌ | 自动读取 |

### 2.6 音乐风格标签参考

常用风格标签（英文，可自由组合）：

- **流派**: rock, pop, jazz, blues, electronic, hip-hop, R&B, classical, folk, metal, country, reggae, latin, indie
- **乐器**: electric guitar, acoustic guitar, piano, synthesizer, drums, bass, violin, saxophone, trumpet
- **情绪**: energetic, emotional, melancholic, upbeat, dark, dreamy, aggressive, peaceful, romantic
- **人声**: male vocals, female vocals, choir, rap, whisper, powerful vocals, falsetto
- **语言**: chinese, japanese, korean, english, spanish
- **其他**: fast tempo, slow tempo, instrumental, lo-fi, cinematic, epic

**示例**：
- 摇滚: `rock, electric guitar, energetic, male vocals, chinese`
- 抒情: `pop, piano, emotional, female vocals, slow tempo, chinese`
- 电子: `electronic, synthesizer, upbeat, fast tempo, dance`
- 说唱: `hip-hop, rap, bass, drums, energetic, chinese`

---

## 三、完整使用示例

### 示例 1：创建中文摇滚歌曲

```bash
# 1. 检查环境
bash {baseDir}/suno/check_env.sh

# 2. 如果未登录，先登录（需要用户提供邮箱密码）
cd {baseDir}/suno
python3 suno_login.py --email "user@gmail.com" --password "password123"

# 3. 确保 hCaptcha 补丁已应用
python3 patch_hcaptcha.py

# 4. 创建歌曲
python3 suno_create_song.py \
  --lyrics "窗外的麻雀 在电线杆上多嘴
你说这一句 很有夏天的感觉
手中的铅笔 在纸上来来回回
我用几行字形容你是我的谁" \
  --style "rock, electric guitar, energetic, male vocals, chinese" \
  --title "七里香摇滚版"
```

### 示例 2：从文件读取歌词

```bash
cd {baseDir}/suno
python3 suno_create_song.py \
  --lyrics-file /path/to/lyrics.txt \
  --style "pop, piano, emotional, female vocals, chinese" \
  --title "我的歌"
```

---

## 四、安装依赖（仅首次）

### macOS

```bash
# 安装 Python 依赖
cd {baseDir}/suno
pip3 install -r requirements.txt
playwright install

# 确保已安装 Google Chrome
# 下载地址: https://www.google.com/chrome/
```

### Linux 云服务器

```bash
# 系统依赖
sudo apt update && sudo apt install -y xvfb google-chrome-stable fonts-noto-cjk

# Python 依赖
cd {baseDir}/suno
pip3 install -r requirements.txt
pip3 install PyVirtualDisplay
playwright install
```

---

## 五、技术原理

### 登录方案
- 使用 Playwright + 真实 Chrome 浏览器 (`channel='chrome'`)
- `persistent context` 保持浏览器状态（cookies、localStorage）
- `headless=False`（GUI 模式）通过 Google 反自动化检测
- Linux 服务器使用 Xvfb 虚拟显示支持 GUI 模式
- 首次登录后 persistent context 自动保持会话

### 歌曲创建方案
- 浏览器自动化操作 suno.com/create 页面
- hcaptcha-challenger + Gemini API 自动解决 hCaptcha 验证码
- 通过拦截浏览器网络响应捕获新生成的 clip ID
- 通过 Suno 内部 API (`studio-api.prod.suno.com`) 轮询歌曲生成状态
- 生成完成后自动下载 MP3 文件

### 文件结构

```
suno/
├── suno_login.py          # 登录工具（通过 Google OAuth）
├── suno_create_song.py    # 歌曲创建+下载工具
├── patch_hcaptcha.py      # hCaptcha 域名兼容补丁
├── check_env.sh           # 环境检查脚本
├── requirements.txt       # Python 依赖
└── qilixiang_lyrics.txt   # 示例歌词（七里香）
```

---

## 六、注意事项

1. **不要硬编码账号密码** — 每次都需要询问用户
2. Suno 免费账号每天有积分限制，每首歌消耗约 100 积分
3. 歌曲生成通常需要 1-3 分钟
4. 每次创建会生成 2 首不同版本的歌曲
5. 如果遇到 Google 登录被拒（rejected），等待 10-30 分钟后重试
6. Gemini API 免费额度：每分钟 15 次请求，每天 1500 次
7. `headless=True` 模式会被 Google 检测拦截，**登录必须使用 GUI 模式**
8. hCaptcha 可能需要多次尝试，成功率取决于 Gemini 模型的图片识别能力

## 七、故障排查

```bash
# 检查环境
bash {baseDir}/suno/check_env.sh

# 查看登录截图
ls -la /tmp/suno_debug_*.png

# 检查 persistent context
ls -la ~/.suno/chrome_gui_profile/

# 查看 cookies
python3 -c "import json; d=json.load(open('$HOME/.suno/cookies.json')); print(f'{len(d)} cookies')"

# 查看 Gemini API Key
cat ~/.suno/.env

# 查看下载的歌曲
ls -la {baseDir}/output_mp3/
```

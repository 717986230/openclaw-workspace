---
name: gemini-image-generator
description: >-
  Generate, edit, and compose images using Gemini models. Activate when user asks to generate images, draw, create logos/posters/icons/banners, edit/modify photos, combine images, or any image creation task.
  画图、生成图片、做图、P图、修图、合成图、做logo、做海报、做图标、做封面、品牌视觉、Nano Banana、Banana。

metadata:
  openclaw:
    emoji: "🎨"
    category: creative
    homepage: "https://github.com/wangyan/gemini-image-generator"
    requires:
      bins:
        - python3
        - uv
      env:
        - GEMINI_API_KEY
        - GEMINI_BASE_URL
    primaryEnv: GEMINI_API_KEY
    tags:
      - image-generation
      - image-editing
      - image-composition
      - text-to-image
      - logo-design
      - poster-design
      - brand-visual
      - gemini
      - nano-banana
      - nano-banana-pro
      - openai-compatible
---

# Gemini Image Generator

通过 `Nano Banana` 实现文生图、图片编辑与多图合成，支持 OpenAI 兼容和 Google 原生两种 API 格式，可自定义端点和密钥。

---

## ⚠️ 重要规则

1. **必须调用脚本**：命中图像生成/编辑/合成意图时，必须执行本技能脚本，禁止用文本描述替代图片输出。  
2. **依赖缺失报错**：`python3` 或 `uv` 不可用时，返回 `缺失依赖：{名称}` + 安装命令，不做文本兜底。  
3. **自检输出产物**：执行后检查输出是否含 `MEDIA:` 行。无产物则自动重试 1 次；仍失败输出 `图片生成失败 - 原因/建议`。

## 🎯 触发判断

1. **触发**：画图、生成图片、做logo/海报/图标/封面、P图、修图、合成图、draw/generate/create image/logo/banner  
2. **不触发**：图片分析、OCR、格式转换、图片搜索、图片评价

---

## 🚀 使用方法

### 生成图片

```bash
uv run {baseDir}/scripts/generate_image.py --prompt "图片描述" --filename "output.png"
```

### 编辑图片（单图）

```bash
uv run {baseDir}/scripts/generate_image.py --prompt "编辑指令" --filename "edited.png" -i "/path/input.png" --resolution 2K
```

### 合成多张图片（最多 14 张）

```bash
uv run {baseDir}/scripts/generate_image.py --prompt "合成指令" --filename "composed.png" -i img1.png -i img2.png -i img3.png
```

### 自定义端点

```bash
uv run {baseDir}/scripts/generate_image.py --prompt "描述" --filename "output.png" \
  --base-url "https://example.com/v1" --api-key "sk-xxx" --model "gemini-3-pro-preview"
```

### 使用 Google 原生格式

```bash
uv run {baseDir}/scripts/generate_image.py --prompt "描述" --filename "output.png" --api-format google
```

---

## ⚙️ 配置参考

优先级：命令行参数 > 环境变量（由 `skills.entries.gemini-image-generator.env` 注入）

| 参数 | 环境变量 | 说明 |
|------|---------|------|
| `--api-key` / `-k` | `apiKey`（通过 primaryEnv 注入） | API 密钥（必填） |
| `--base-url` / `-b` | `GEMINI_BASE_URL` | API 端点 URL（必填） |
| `--model` / `-m` | `GEMINI_MODEL` | 模型名称（默认 `gemini-3-pro-preview`） |
| `--api-format` / `-F` | `GEMINI_API_FORMAT` | `openai`（默认）或 `google` |
| `--timeout` / `-t` | `GEMINI_TIMEOUT` | 超时秒数（默认 300） |
| `--resolution` / `-r` | `GEMINI_RESOLUTION` | `1K`（默认）、`2K`、`4K` |
| `--output-dir` / `-o` | `GEMINI_OUTPUT_DIR` | 输出目录（默认 `images`） |

可选参数：

- `--input-image` / `-i`：输入图片路径（可重复，最多 14 张）
- `--quality`：`standard`（默认）或 `hd`
- `--style`：`natural`（默认）或 `vivid`
- `--aspect-ratio` / `-a`：宽高比（如 `1:1`、`16:9`、`9:16`、`4:3`、`3:4`）
- `--verbose` / `-v`：输出详细调试

支持模型：

- `gemini-2.5-flash-image`
- `gemini-3-pro-image-preview`
- `gemini-3.1-flash-image-preview`

---

## 📝 注意事项

- 文件名使用时间戳格式：`yyyy-mm-dd-hh-mm-ss-name.png`  
- 脚本输出 `MEDIA:` 行供 OpenClaw 自动附件到聊天  
- 不要回读图片内容，只报告保存路径  
- 编辑模式下未指定分辨率时，自动根据输入图片尺寸推断  
- 内置 429 限流和超时自动重试（最多 3 次）  
- API 响应格式详见 [references/api-formats.md](references/api-formats.md)
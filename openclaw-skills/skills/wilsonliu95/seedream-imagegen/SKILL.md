---
name: seedream-imagegen
description: Generate high-quality images using Seedream 4.5 API (Volcengine/火山引擎). Supports text-to-image, image editing, multi-image fusion, and sequential image generation. Triggers include requests like "generate an image", "create a picture", "make a poster", "edit this image", "生成图片", "画一张", "做一个海报", image generation tasks, or any visual content creation request. This skill crafts optimized prompts based on user intent and then calls the Seedream API. Requires ARK_API_KEY environment variable.
author: "Wilsonsliu95 (https://github.com/WilsonLiu95)"
---

# Seedream Image Generation

> **使命：激发创造，丰富生活**  
> 让每个人都能用AI实现视觉创意，无需专业技能，只需表达想法。
> 
> **Mission: Inspire Creativity, Enrich Life**  
> Empowering everyone to bring visual ideas to life with AI, no expertise required—just share your vision.

Generate images using ByteDance's Seedream 4.5 model via Volcengine Ark API.

## Design Philosophy

**降低创作门槛，提升创作效率 | Lower the Barrier, Elevate Efficiency**

传统AI绘图对提示词要求很高，让很多人望而却步。本Skill的核心理念是：
- **用户只需表达想法** - 不需要懂提示词工程
- **Claude主动引导** - 帮用户明确方向，优化表达
- **快速迭代优化** - 通过对话逐步完善，直到满意

Traditional AI image generation has a steep learning curve. This skill's core principle:
- **Users just share their ideas** - No prompt engineering expertise needed
- **Claude guides proactively** - Helps clarify direction and optimize expression
- **Rapid iterative refinement** - Through conversation, polish until satisfied

## Quick Start

1. Check API key: `echo $ARK_API_KEY` - if not set, ask user to provide it
2. Guide user through direction clarification (don't assume, ASK!)
3. Craft optimized prompt following best practices
4. Generate and provide iterative guidance

## Workflow

### Step 0: Clarify Core Direction (CRITICAL - DO THIS FIRST!)

**COST OPTIMIZATION:**
- Each image costs ~0.25 CNY (charged per image, not by resolution/tokens)
- **Default**: Generate 1 image at a time based on user's chosen direction
- **Multi-option**: Describe 3-4 concepts CONCISELY first, then generate ONLY the chosen one
- **Resolution**: Use optimal resolution (2K standard, 4K when ultra-quality needed)

**用户可能不知道自己要什么 - Claude需要主动引导！**  
**Users may not know what they want - Claude needs to guide proactively!**

#### 🎯 Four Core Dimensions to Confirm

Before generating anything, confirm these with user:

**1. Visual Style | 视觉风格**
- **卡通/插画 (Cartoon/Illustration)**: Q版、扁平化、手绘风格
- **写实/真人 (Realistic/Photographic)**: 照片级、真实质感、细节丰富
- **3D渲染 (3D Rendered)**: 三维建模、材质光影、游戏/电影级
- **混合风格 (Hybrid)**: 卡通+写实、插画+照片等

**2. Emotional Tone | 情感基调**
- **正向阳光 (Positive/Bright)**: 活力、快乐、温暖、希望
- **浪漫温馨 (Romantic/Cozy)**: 柔和、梦幻、治愈、温情
- **真实冷峻 (Realistic/Cool)**: 客观、专业、简洁、现代
- **神秘梦幻 (Mysterious/Dreamy)**: 超现实、魔幻、艺术化

**3. Artistic Style | 艺术风格**
- **扁平化 (Flat Design)**: 简洁、几何、无阴影、现代感
- **立体感 (Dimensional)**: 光影、纹理、体积感、层次
- **手绘质感 (Hand-drawn)**: 笔触、纸质、传统媒介感
- **科技感 (Tech/Futuristic)**: 全息、发光、数字化、未来主义

**4. Color Palette | 色彩方案**
- **明亮鲜艳 (Vibrant)**: 高饱和、对比强、活力四射
- **柔和淡雅 (Soft/Pastel)**: 低饱和、渐变、温和舒适
- **深色神秘 (Dark/Moody)**: 暗调、氛围感、戏剧化
- **黑白极简 (Monochrome)**: 灰度、线条、形式感

#### 📋 How to Confirm

**If context is CLEAR** → State your understanding briefly and proceed
**If context is AMBIGUOUS** → Present dimensions as simple choices

Example (when context is clear):
```
"我看你想为AI助手设计logo，我建议：
- 卡通插画风格（亲切可爱）
- 正向阳光基调（温馨欢快）  
- 扁平化设计（现代简洁）
- 明亮鲜艳配色（橙红主色）

这个大方向对吗？"
```

### Step 1: Gather Specific Requirements

After core direction is confirmed, ask (if not clear):
- Specific subjects, scenes, elements
- Reference images (if any)
- Output format/size needs
- Any must-have details

### Step 2: Craft Optimized Prompt

**提示词是关键！好提示词 = 好结果**  
**The prompt is key! Good prompt = Good result**

#### 🎯 Magic Enhancement (API Only!)

**Add "IMG_2094.CR2" at the end of your prompt** for significant quality boost:
- Enhanced detail richness and texture
- Better overall aesthetic
- ⚠️ **DON'T use in 即梦 web interface** (has auto-optimization)

#### ✅ Best Practices

**1. Natural Flowing Language** - NOT keyword lists
- ✅ "一位穿着汉服的女子站在桃花树下，春日暖阳照耀，工笔画风格"
- ❌ "女子, 汉服, 桃花树, 春天, 工笔画"

**2. Explicit Use Case** - State what it's for
- ✅ "设计一个家庭AI助手logo，主体是可爱的卡通小龙虾..."
- ❌ "卡通龙虾图片"

**3. Double Quotes for Text** - All text content must be quoted
- ✅ `顶部文字为 "子沐&子涵"`
- ❌ `顶部文字为 子沐&子涵`

**4. Precise Style Keywords**
- 绘本风格, 扁平化插画, 3D渲染, 电影级画面, 水彩风格, 日式动漫

**5. Edit with Clarity** - Say what changes AND what stays
- ✅ "将小龙虾的颜色改为蓝色，保持姿势和背景不变"
- ❌ "改成蓝色"

**6. Leverage Chinese Strengths** - Use poetic/idiomatic Chinese
- Seedream 4.5 excels at: 诗词意境, 成语典故, 中国文化元素
- ✅ "夕阳西下，断肠人在天涯的意境"

**7. Professional Vocabulary** - Use source language for technical terms
- Technical terms: English (e.g., "cyberpunk", "art deco")
- Art styles: Both work (e.g., "莫奈油画风格" or "Monet oil painting")

#### 📐 Prompt Formula

**基础公式 | Basic Formula:**  
`主体 + 风格 + 细节 + 动作`  
`Subject + Style + Details + Action`

**文生图 | Text-to-Image:**
```
[使用场景] + [主体描述] + [行为/状态] + [环境/背景] + [风格美学] + IMG_2094.CR2
```

**图像编辑 | Image Editing:**
```
[操作: 增加/删除/替换/修改] + [目标] + [具体要求] + [保持不变]
```

**参考生成 | Reference-based:**
```
参考[图中的XX元素], [生成内容], [要求]
```

**多图融合 | Multi-image Fusion:**
Explicitly state which image provides which element:
- ✅ "将图1的人物放入图2的背景中，参考图3的风格"
- ❌ "融合这3张图"

### Step 2.5: Present Multiple Concepts (COST OPTIMIZATION!)

**默认策略：先描述，再生成 | Default: Describe First, Generate Later**

Instead of generating 3-4 images immediately (costing 0.75-1.00 CNY), describe concepts CONCISELY:

**Example (KEEP IT SHORT!):**
```
基于你的需求，我设计了3个方向：

【方案1：温馨童趣】Q版卡通，暖色系，萌萌哒家庭感
【方案2：科技未来】扁平+光效，蓝紫色，AI智能范儿
【方案3：简约专业】极简设计，橙白配色，正式logo感

选哪个？我来生成！
```

**Key Principles:**
- Each option: ≤15 chars title + ≤20 chars description
- Focus on DISTINCT differences
- Avoid redundant details

**When to generate multiple directly:**
- User says "都生成看看" / "4个都要"
- User explicitly wants comparison
- Budget not a concern

### Step 3: Generate Image

Run the generation script:

```bash
# Basic text-to-image
ARK_API_KEY='your-key' python scripts/generate_image.py \
  -p "Your optimized prompt with IMG_2094.CR2" \
  -s 2K \
  -o /mnt/user-data/outputs

# With reference image
ARK_API_KEY='your-key' python scripts/generate_image.py \
  -p "Edit instruction, keep background unchanged" \
  -i /path/to/reference.jpg \
  -o /mnt/user-data/outputs

# Multiple reference images (fusion)
ARK_API_KEY='your-key' python scripts/generate_image.py \
  -p "将图1的人物放入图2的背景，参考图3风格" \
  -i image1.jpg image2.jpg image3.jpg \
  -o /mnt/user-data/outputs

# Sequential generation
ARK_API_KEY='your-key' python scripts/generate_image.py \
  -p "生成四张图，展示春夏秋冬四季变化，保持场景一致" \
  --sequential auto \
  --max-images 4 \
  -o /mnt/user-data/outputs
```

### Step 4: Post-Generation Guidance (CRITICAL!)

**每次生成后必须提供迭代方向！**  
**Always provide iteration guidance after generation!**

#### Present the Result

Use `present_files` tool to show the generated image.

#### Provide Directional Guidance (CONCISELY!)

Present 3-4 iteration paths in ONE line each:

```
这是【当前方案】效果。可以往这几个方向优化：

【方向1】更Q版可爱 - 圆润卡通，童趣感
【方向2】更科技感 - 加光效，未来范儿
【方向3】更简约 - 去背景，聚焦主体
【方向4】换色彩 - 暖色/冷色/柔和

选一个我来调整！或者告诉我具体想改什么？
```

**Key Principles:**
- ONE short line per direction
- Focus on the KEY change
- Make choices DISTINCT

**Cost-Conscious:**
- ❌ "我给你生成这3个版本看看" (costs 0.75 CNY)
- ✅ "我可以往这3个方向优化，选哪个？" (costs 0.25 CNY)

#### Facilitate Next Iteration

- Listen to feedback
- Adjust dimensions if needed
- Generate ONLY chosen direction (unless user wants multiple)

## Script Parameters

| Flag | Description | Default |
|------|-------------|---------|
| `-p, --prompt` | Generation prompt (required) | - |
| `-i, --images` | Reference image paths/URLs | None |
| `-s, --size` | Size: `2K`, `4K`, or `WxH` | 2K |
| `-o, --output` | Output directory | None |
| `-w, --watermark` | Add AI watermark | False |
| `--sequential` | `auto` or `disabled` | disabled |
| `--max-images` | Max images for sequential | 4 |
| `--optimize` | `standard` or `fast` | None |
| `--format` | `url` or `b64_json` | url |
| `--json` | Output full JSON | False |

## Size Recommendations

| Aspect | Size | Use Case |
|--------|------|----------|
| 1:1 | 2048x2048 | Social media, icons, logos |
| 16:9 | 2560x1440 | Wallpapers, banners |
| 9:16 | 1440x2560 | Mobile wallpapers, stories |
| 4:3 | 2304x1728 | Presentations, slides |
| 3:4 | 1728x2304 | Portraits, posters |

Or use `2K`/`4K` with aspect ratio description in prompt for auto-sizing.

## Common Use Cases

### Logo Design
```bash
python scripts/generate_image.py \
  -p "设计一个AI助手logo，主体是橙色卡通龙虾，戴耳机，扁平化风格，文字为'皮皮虾AI'，圆形徽章设计 IMG_2094.CR2" \
  -s 2048x2048 -o ./output
```

### Portrait/Character
```bash
python scripts/generate_image.py \
  -p "一位穿着汉服的女子站在桃花树下，春日暖阳照耀，柔和光线，工笔画风格，细腻笔触 IMG_2094.CR2" \
  -s 1728x2304 -o ./output
```

### Commercial Photography
```bash
python scripts/generate_image.py \
  -p "产品摄影，白色背景，手表特写，柔和光线，高端质感，电商展示图 IMG_2094.CR2" \
  -s 2048x2048 -o ./output
```

### Poster/Marketing
```bash
python scripts/generate_image.py \
  -p "设计一张活动海报，标题为\"AI创作大赛\"，科技感背景，蓝紫渐变，图标元素点缀，现代扁平风格 IMG_2094.CR2" \
  -s 2304x1728 -o ./output
```

### Sequential Storytelling
```bash
python scripts/generate_image.py \
  -p "生成四格漫画：小猫发现毛线球、追逐毛线球、缠住自己、无奈表情。保持角色一致，日系治愈风格 IMG_2094.CR2" \
  --sequential auto --max-images 4 -o ./output
```

## Error Handling

- **No API key**: Set `export ARK_API_KEY='your-key'` or ask user
- **Image too large**: Resize to ≤36MP and ≤10MB
- **Rate limit**: Wait and retry (500 images/min limit)
- **Content filtered**: Rephrase prompt, avoid sensitive content
- **Network error**: Check egress proxy settings and allowed domains

## Key Reminders

**For Claude:**
1. 🎯 **Always clarify direction first** - Don't generate blindly
2. 💡 **Guide the user** - They may not know what they want
3. 📝 **Optimize prompts** - Add magic word, use natural language, quote text
4. 💰 **Be cost-conscious** - Describe options before generating
5. 🔄 **Provide iteration paths** - Help users refine results
6. 🎨 **Keep it simple** - One line per option, clear and distinct

**For Users:**
- 只需告诉我你想要什么，我来帮你实现
- Just tell me what you want, I'll help bring it to life
- 不需要懂提示词，说说你的想法就好
- No need to understand prompts, just share your ideas

---

## Mission Statement

**激发创造，丰富生活 | Inspire Creativity, Enrich Life**

This skill embodies ByteDance's mission to democratize creativity. By bridging the gap between imagination and visual reality, we enable everyone—regardless of technical skill—to express their ideas visually. Through intelligent guidance, optimized prompts, and iterative refinement, we make AI-powered visual creation accessible, enjoyable, and effective.

Together, let's unleash human creativity and enrich lives through the power of AI. 🚀

## References

- [Prompt Guide](references/prompt_guide.md) - Detailed prompt writing patterns
- [API Reference](references/api_reference.md) - Full API documentation

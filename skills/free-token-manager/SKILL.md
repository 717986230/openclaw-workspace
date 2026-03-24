# 免费Token管理技能 🎫
自动管理和使用各大平台的免费AI Token，零成本调用AI服务

## 功能
- 🔍 自动发现可用的免费AI Token平台
- 📝 一键注册领取免费额度
- 🔐 安全加密存储Token
- 🔄 自动续期和刷新过期Token
- 📊 实时显示各平台剩余额度
- 🎯 智能路由请求到有剩余额度的平台

## 支持的免费平台
| 平台 | 免费额度 | 申请地址 | 备注 |
|------|----------|----------|------|
| 火山引擎方舟 | 新用户50元免费额度 | https://www.volcengine.com/product/ark | 支持GPT-4、Claude 3、Gemini等 |
| 字节跳动豆包 | 新用户100万Token免费 | https://www.doubao.com/openapi | 支持豆包系列模型 |
| 百度文心一言 | 新用户免费调用额度 | https://cloud.baidu.com/product/wenxinworkshop | 支持文心系列模型 |
| 腾讯混元 | 新用户免费额度 | https://cloud.tencent.com/product/hunyuan | 支持混元系列模型 |
| 阿里通义千问 | 新用户免费额度 | https://www.aliyun.com/product/dashscope | 支持通义系列模型 |
| OpenRouter | 新用户免费5美元额度 | https://openrouter.ai | 支持几乎所有主流模型 |
| Together.ai | 新用户免费25美元额度 | https://www.together.ai | 开源模型调用 |
| Groq | 永久免费速率限制调用 | https://groq.com | 超高速开源模型调用 |
| Claude.ai | 免费网页版API逆向 | https://claude.ai | 免费使用Claude 3 |
| Gemini API | 免费额度调用 | https://ai.google.dev | Google Gemini模型 |

## 配置文件
配置文件路径：`~/.openclaw/config/free_tokens.json`
自动加密存储所有Token，安全可靠

## 使用方法
### 1. 扫描可用平台
```
/free-token scan
```
扫描所有支持的平台，显示可领取的免费额度

### 2. 注册领取Token
```
/free-token claim <平台名>
```
自动引导注册并领取对应平台的免费Token

### 3. 查看所有Token状态
```
/free-token list
```
显示所有已配置的Token和剩余额度

### 4. 测试Token可用性
```
/free-token test <平台名>
```
测试对应平台的Token是否可用

### 5. 删除Token
```
/free-token delete <平台名>
```
删除对应平台的Token配置

### 6. 自动刷新Token
```
/free-token refresh
```
自动刷新所有即将过期的Token

## 安全说明
- 所有Token都使用AES-256加密存储
- 不会上传任何Token到第三方服务器
- 只在本地使用，安全可控
- 支持导出/导入备份配置

## 自动使用
配置完成后，技能会自动在调用AI服务时选择有剩余额度的平台，无需手动切换

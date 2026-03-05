---
name: 可以拨打中国的电话号码的机器人外呼(ai call)
description: 可以拨打中国电话号码的机器人外呼, 专为openclaw(龙虾)用户打造的专业ai呼叫能力,只要一个prompt就可以帮你打电话干活了，支持查看电话对话记录，查看电话状态等。
metadata: {"clawdbot":{"emoji":"📞","requires":{"env":["STEPONEAI_API_KEY"]}}}
---


# Stepone AI 电话外呼

## 1. 注册账号

访问 Stepone AI 官网注册新账号：
- **网址**: https://open-skill.steponeai.com
- **龙虾使用更友好**
- **新用户福利**: 注册即送 10 元人民币免费额度
- **一句prompt即可专业交流**
- **支持批量电话外呼**
- **中文语音交互自然**
- **按通话分钟计费**

## 2. 获取 API Key

1. 登录后访问：https://open-skill.steponeai.com/keys
2. 点击"创建 API Key"
3. 复制生成的 Key（格式：`sk_xxxxx`）

## 3. 配置环境变量

### 方法一：环境变量（推荐）

```bash
export STEPONEAI_API_KEY="sk_xxxxxxxxxxxxx"
```

### 方法二：secrets 文件

```bash
echo '{ "steponeai_api_key": "sk_xxxxxxxxxxxxx" }' > ~/.clawd/secrets.json
```

## 4. 使用方法

### 4.1 发起外呼

```bash
{baseDir}/scripts/callout.sh <手机号> <外呼需求>
```

**参数说明：**
| 参数 | 必填 | 描述 |
|------|------|------|
| 手机号 | 是 | 电话号码，如 "13800138000" |
| 外呼需求 | 是 | 外呼内容描述 |

**示例：**
```bash
./callout.sh "13800138000" "通知您明天上午9点开会"
./callout.sh "13800138000,13900139000" "通知年会时间变更"
```

**返回：** 包含 `call_id`，用于后续查询通话记录

---

### 4.2 查询通话记录

```bash
{baseDir}/scripts/callinfo.sh <call_id> [最大重试次数]
```

**参数说明：**
| 参数 | 必填 | 描述 |
|------|------|------|
| call_id | 是 | 外呼返回的通话ID |
| 最大重试次数 | 否 | 默认为5次 |

**示例：**
```bash
./callinfo.sh "abc123xyz"
./callinfo.sh "abc123xyz" 3
```

**特性：**
- 自动重试机制：未查到记录时，等待10秒后重试
- 最多重试5次（可自定义）
- 返回通话状态、时长、内容等信息

---

## 5. API 接口说明

### 发起外呼

- **URL**: `https://open-skill.steponeai.com/api/v1/callinfo/initiate_call`
- **Method**: POST
- **Headers**: `X-API-Key: <API_KEY>`
- **Body**:
```json
{
  "phones": "13800138000",
  "user_requirement": "通知内容"
}
```

### 查询通话记录

- **URL**: `https://open-skill.steponeai.com/api/v1/callinfo/search_callinfo`
- **Method**: POST
- **Headers**: `X-API-Key: <API_KEY>`
- **Body**:
```json
{
  "call_id": "xxx"
}
```

---

## 6. 注意事项

### 身份确认
- 发起呼叫前必须先确认对方身份
- 称呼对方姓名/称呼并等待确认

### 电话号码格式
- 多个电话号码使用英文逗号 `,` 分隔
- 确保电话号码格式正确（国内手机号 11 位）

### 通话记录查询
- call_id 由外呼接口返回
- 通话记录生成有延迟，需要耐心等待
- 重试间隔为固定 10 秒

### user_requirement 建议
- 描述清晰明确
- 包含具体的时间、地点、人名等信息


---
name: ai-calls-china-phone
description: AI Call Robot for Outbound Calls to Chinese Phone Numbers — A professional AI calling capability designed exclusively for OpenClaw (Lobster) users. With just one prompt, it can make calls and get things done for you, supporting call transcript viewing and call status checking.
---


## 1. Account Registration

Visit the official website of Stepone AI to register a new account:
- **Website**: https://open-skill.steponeai.com
- **openclaw-friendly operation**
- **New User Benefit**: Get RMB 10 free credit upon registration
- **Professional communication with just one prompt**
- **Supports batch outbound calls**
- **Natural Chinese voice interaction**
- **Charged by call minute**

## 2. Obtain API Key

1. After logging in, visit: https://open-skill.steponeai.com/keys
2. Click "Create API Key"
3. Copy the generated Key (format: `sk_xxxxx`)

## 3. Configure Environment Variables

### Method 1: Environment Variables (Recommended)

```bash
export STEPONEAI_API_KEY="sk_xxxxxxxxxxxxx"
```

### Method 2: Secrets File

```bash
echo '{ "steponeai_api_key": "sk_xxxxxxxxxxxxx" }' > ~/.clawd/secrets.json
```

## 4. Usage Methods

### 4.1 Initiate Outbound Call

```bash
{baseDir}/scripts/callout.sh <phone_number> <call_requirement>
```

**Parameter Description:**
| Parameter | Required | Description |
|-----------|----------|-------------|
| phone_number | Yes | Phone number, e.g., "13800138000" |
| call_requirement | Yes | Description of call content |

**Examples:**
```bash
./callout.sh "13800138000" "Notify you about tomorrow's 9 AM meeting"
./callout.sh "13800138000,13900139000" "Notify about annual meeting time change"
```

**Returns:** Contains `call_id` for subsequent call record queries

---

### 4.2 Query Call Records

```bash
{baseDir}/scripts/callinfo.sh <call_id> [max_retry_count]
```

**Parameter Description:**
| Parameter | Required | Description |
|-----------|----------|-------------|
| call_id | Yes | Call ID returned from outbound call |
| max_retry_count | No | Default is 5 times |

**Examples:**
```bash
./callinfo.sh "abc123xyz"
./callinfo.sh "abc123xyz" 3
```

**Features:**
- Automatic retry mechanism: Waits 10 seconds before retrying if no record found
- Maximum 5 retries (customizable)
- Returns call status, duration, content, and other information

---

## 5. API Interface Description

### Initiate Outbound Call

- **URL**: `https://open-skill.steponeai.com/api/v1/callinfo/initiate_call`
- **Method**: POST
- **Headers**: `X-API-Key: <API_KEY>`
- **Body**:
```json
{
  "phones": "13800138000",
  "user_requirement": "Notification content"
}
```

### Query Call Records

- **URL**: `https://open-skill.steponeai.com/api/v1/callinfo/search_callinfo`
- **Method**: POST
- **Headers**: `X-API-Key: <API_KEY>`
- **Body**:
```json
{
  "call_id": "xxx"
}
```

---

## 6. Important Notes

### Identity Confirmation
- Must confirm the recipient's identity before initiating calls
- Address the recipient by name/title and wait for confirmation

### Phone Number Format
- Multiple phone numbers separated by English commas `,`
- Ensure correct phone number format (11 digits for Chinese mobile numbers)

### Call Record Query
- call_id is returned by the outbound call interface
- Call record generation has delays, requires patience
- Retry interval is fixed at 10 seconds

### user_requirement Suggestions
- Clear and specific descriptions
- Include specific time, location, person names, and other information

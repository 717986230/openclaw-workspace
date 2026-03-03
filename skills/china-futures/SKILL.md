---
name: china-futures
description: 查询国内商品期货行情，支持上海期货交易所（SHFE）、大连商品交易所（DCE）、郑州商品交易所（CZCE）的品种，包括螺纹钢、燃料油、铜、铝、橡胶、豆粕、豆油、白糖、棉花等。使用免费公开数据源，无需API key。
---

# 国内期货行情查询

查询国内商品期货实时行情，免费使用，无需API key。

## 📊 支持的交易所和品种

### 上海期货交易所 (SHFE)
- 螺纹钢 (rb)
- 燃料油 (fu)
- 铜 (cu)
- 铝 (al)
- 锌 (zn)
- 橡胶 (ru)
- 黄金 (au)
- 白银 (ag)
- 原油 (sc)

### 大连商品交易所 (DCE)
- 豆粕 (m)
- 豆油 (y)
- 棕榈油 (p)
- 玉米 (c)
- 铁矿石 (i)
- 焦炭 (j)
- 焦煤 (jm)

### 郑州商品交易所 (CZCE)
- 白糖 (SR)
- 棉花 (CF)
- PTA (TA)
- 甲醇 (MA)
- 玻璃 (FG)

## 🌐 免费数据源

### 1. 新浪财经（推荐）
**API格式**: `https://hq.sinajs.cn/list=品种代码`

**示例**:
```powershell
# 螺纹钢主力合约
Invoke-RestMethod -Uri "https://hq.sinajs.cn/list=rb0" -UseBasicParsing

# 燃料油主力合约
Invoke-RestMethod -Uri "https://hq.sinajs.cn/list=fu0" -UseBasicParsing

# 铜主力合约
Invoke-RestMethod -Uri "https://hq.sinajs.cn/list=cu0" -UseBasicParsing
```

### 2. 东方财富
**API格式**: `http://push2.eastmoney.com/api/qt/stock/get?secid=期货代码`

## 🚀 使用示例

### 查询单个品种
```powershell
function Get-FuturePrice {
    param([string]$Symbol = "rb0")
    
    $url = "https://hq.sinajs.cn/list=$Symbol"
    $response = Invoke-RestMethod -Uri $url -UseBasicParsing
    
    # 解析返回数据
    if ($response -match '="([^"]+)"') {
        $data = $matches[1] -split ','
        return [PSCustomObject]@{
            名称 = $data[0]
            开盘价 = $data[1]
            昨收价 = $data[2]
            现价 = $data[3]
            最高价 = $data[4]
            最低价 = $data[5]
            买价 = $data[6]
            卖价 = $data[7]
            成交量 = $data[8]
            持仓量 = $data[9]
            日期 = $data[30]
            时间 = $data[31]
        }
    }
}

# 查询螺纹钢
Get-FuturePrice -Symbol "rb0"

# 查询燃料油
Get-FuturePrice -Symbol "fu0"
```

### 常用品种代码
| 品种 | 代码 |
|------|------|
| 螺纹钢主力 | rb0 |
| 燃料油主力 | fu0 |
| 铜主力 | cu0 |
| 铝主力 | al0 |
| 橡胶主力 | ru0 |
| 黄金主力 | au0 |
| 豆粕主力 | m0 |
| 豆油主力 | y0 |
| 棕榈油主力 | p0 |
| 铁矿石主力 | i0 |
| 白糖主力 | SR0 |
| 棉花主力 | CF0 |

### 查询多个品种
```powershell
$symbols = @("rb0", "fu0", "cu0", "au0")
$results = @()

foreach ($symbol in $symbols) {
    $data = Get-FuturePrice -Symbol $symbol
    if ($data) {
        $results += $data
    }
}

$results | Format-Table 名称, 现价, 涨跌幅
```

## 📋 输出示例

```
📊 国内期货行情

螺纹钢 (rb0)
├── 现价: 3,680 元/吨
├── 涨跌幅: +1.25%
├── 最高价: 3,720
├── 最低价: 3,650
├── 成交量: 1,234,567 手
└── 持仓量: 890,123 手

燃料油 (fu0)
├── 现价: 3,250 元/吨
├── 涨跌幅: -0.45%
├── 最高价: 3,280
├── 最低价: 3,230
├── 成交量: 456,789 手
└── 持仓量: 234,567 手

更新时间: 2026-03-03 20:15:00
```

## ⚠️ 注意事项

1. **数据源延迟**: 免费数据源可能有几秒到几分钟的延迟
2. **交易时间**: 国内期货交易时间：
   - 日盘: 09:00-10:15, 10:30-11:30, 13:30-15:00
   - 夜盘: 21:00-02:30（部分品种）
3. **仅供参考**: 免费行情仅供参考，不构成投资建议
4. **Rate Limit**: 不要过于频繁请求，避免被限制

## 🔗 更多数据源

如果新浪财经不可用，可以试试：
- 东方财富: http://push2.eastmoney.com/api/qt/stock/get
- 和讯期货: http://futures.hexun.com/
- 同花顺: http://www.10jqka.com.cn/

---

*投资有风险，入市需谨慎*

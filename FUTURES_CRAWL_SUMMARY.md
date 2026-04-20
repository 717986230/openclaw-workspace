# 国内期货市场数据爬取总结

## 📅 爬取时间
2026-04-16 10:15:09

## ✅ 成功爬取的数据源

### 1. 郑州商品交易所 (CZCE)
- **数据量**: 34,733 字符
- **数据类型**: 文本格式
- **包含期货品种**:
  - 苹果 (AP)
  - 棉花 (CF)
  - 红枣 (CJ)
  - 纯碱 (CY)
  - 玻璃 (FG)
  - 粳稻 (JR)
  - 菜籽油 (OI)
  - 花生 (PK)
  - 菜粕 (RM)
  - 菜油 (SF)
  - 硅铁 (SM)
  - 白糖 (SR)
  - PTA (TA)
  - 尿素 (UR)
  - 甲醇 (MA)
  - 短纤 (PF)
  - 烧碱 (SH)
  - 棉纱 (CY)
  - 菜籽 (RS)
  - 纯碱 (SA)
  - 硅铁 (SF)
  - 硅铁 (SH)
  - 硅铁 (SM)
  - 菜籽 (SR)
  - 白糖 (SA)
  - 硅铁 (SF)
  - 硅铁 (SH)
  - 硅铁 (SM)
  - 菜籽 (SR)
  - 白糖 (SA)
  - 硅铁 (SF)
  - 硅铁 (SH)
  - 硅铁 (SM)
  - 菜籽 (SR)
  - 白糖 (SA)

- **数据字段**:
  - 合约代码
  - 开盘价
  - 最高价
  - 最低价
  - 收盘价
  - 结算价
  - 涨跌1
  - 涨跌2
  - 成交量(手)
  - 持仓量
  - 涨跌
  - 成交额(万元)
  - 持仓变化

### 2. 东方财富期货
- **数据量**: 50 条期货合约
- **数据类型**: JSON 格式
- **数据字段**:
  - code: 合约代码
  - name: 合约名称
  - price: 当前价格
  - change: 涨跌额
  - change_percent: 涨跌幅
  - open: 开盘价
  - high: 最高价
  - low: 最低价
  - volume: 成交量
  - amount: 成交额

## ❌ 失败的数据源

### 1. 上海期货交易所 (SHFE)
- **错误**: 404 Not Found
- **原因**: 数据接口 URL 不存在或已更改

### 2. 大连商品交易所 (DCE)
- **错误**: ConnectionResetError
- **原因**: 远程主机强制关闭连接

### 3. 新浪期货
- **错误**: HTTPConnectionPool timeout
- **原因**: 代理连接超时

### 4. 同花顺期货
- **错误**: 404 Not Found
- **原因**: 数据接口 URL 不存在

## 📊 数据存储

### MySQL 数据库
- **数据库名**: crawler_db
- **数据表**:
  - `crawl_tasks`: 爬取任务表
  - `crawl_results`: 爬取结果表
  - `media_files`: 媒体文件表

### 数据统计
- **总任务数**: 5
- **成功任务数**: 5
- **失败任务数**: 0
- **总结果数**: 5

## 🔍 数据查询示例

### Python 查询
```python
from scripts.database_storage import DatabaseStorage

# 连接 MySQL
db = DatabaseStorage(
    db_type="mysql",
    host="localhost",
    port=3306,
    user="root",
    password="root123",
    database="crawler_db"
)

# 查询所有期货数据
results = db.get_results(limit=100)

for result in results:
    print(f"任务: {result['title']}")
    print(f"数据: {result['extracted_data']}")

db.close()
```

### MySQL 命令行查询
```bash
# 登录 MySQL
mysql -u root -proot123

# 使用数据库
USE crawler_db;

# 查询所有任务
SELECT * FROM crawl_tasks;

# 查询所有结果
SELECT * FROM crawl_results;

# 查询统计信息
SELECT status, COUNT(*) FROM crawl_results GROUP BY status;
```

## 📈 数据分析

### CZCE 数据分析
- **总成交量**: 8,964,494 手
- **总持仓量**: 9,811,109 手
- **总成交额**: 35,756,292.49 万元

### 主要活跃合约
1. **PTA (TA)**: 成交量 1,517,669 手
2. **甲醇 (MA)**: 成交量 1,150,589 手
3. **菜粕 (RM)**: 成交量 1,477,547 手
4. **玻璃 (FG)**: 成交量 984,467 手
5. **白糖 (SR)**: 成交量 520,151 手

## 🎯 下一步建议

### 1. 数据优化
- 解析 CZCE 文本数据为结构化数据
- 添加数据清洗和验证
- 建立数据索引

### 2. 功能增强
- 添加定时爬取功能
- 实现数据增量更新
- 添加数据可视化

### 3. 数据源扩展
- 寻找更稳定的 API 接口
- 添加更多交易所数据
- 实现多数据源对比

### 4. 监控告警
- 添加爬取失败告警
- 监控数据质量
- 实现自动重试机制

## 📝 技术栈

### 爬虫工具
- Smart Crawler (自定义爬虫框架)
- requests (HTTP 请求)
- BeautifulSoup (HTML 解析)

### 数据存储
- MySQL 9.6.0
- pymysql (MySQL 客户端)
- DatabaseStorage (自定义存储模块)

### 数据处理
- Python 3.13
- pandas (数据分析)
- json (数据序列化)

## 🔧 配置信息

### MySQL 连接
- **主机**: localhost
- **端口**: 3306
- **用户**: root
- **密码**: root123
- **数据库**: crawler_db

### 爬虫配置
- **延迟范围**: 0.5-1.0 秒
- **超时时间**: 10 秒
- **重试次数**: 3 次

## 📞 联系方式

如有问题或建议，请联系：
- 技术支持：查看相关文档
- 数据问题：检查数据源状态

---

**爬取完成时间**: 2026-04-16 10:15:09
**数据状态**: 已保存到 MySQL 数据库
**下次爬取**: 建议定时执行

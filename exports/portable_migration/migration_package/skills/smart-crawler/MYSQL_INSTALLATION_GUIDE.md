# MySQL 安装配置指南

## 方案 1：使用 SQLite（推荐，已配置完成）

✅ **当前已可用** - 无需安装任何额外软件

### 使用方法
```python
from scripts.database_storage import DatabaseStorage

# 使用 SQLite
db = DatabaseStorage(db_type="sqlite", db_path="my_crawler.db")

# 创建任务
task_id = db.create_task("我的任务", "https://example.com")

# 保存结果
result_id = db.save_result(
    task_id=task_id,
    url="https://example.com",
    title="示例页面",
    extracted_data={"title": "示例", "price": 100}
)

# 查询结果
results = db.get_results(task_id=task_id)
```

### 优势
- ✅ 无需安装任何软件
- ✅ 零配置，开箱即用
- ✅ 适合中小规模数据
- ✅ 文件型数据库，易于备份

---

## 方案 2：安装 MySQL（适合大规模数据）

### Windows 安装步骤

#### 1. 下载 MySQL
访问官网下载：https://dev.mysql.com/downloads/mysql/

选择：
- **MySQL Community Server** (免费)
- 版本：8.0.x (推荐最新稳定版)
- 平台：Windows (x86, 64-bit)

#### 2. 安装 MySQL
1. 运行下载的安装程序
2. 选择 "Developer Default" 或 "Server only"
3. 设置 root 密码（记住这个密码！）
4. 端口：默认 3306
5. 完成安装

#### 3. 配置 MySQL
打开 MySQL 命令行客户端：

```bash
# 方式 1：使用 MySQL Command Line Client
# 开始菜单 -> MySQL -> MySQL Command Line Client
# 输入 root 密码登录

# 方式 2：使用命令行
mysql -u root -p
# 输入密码
```

#### 4. 创建数据库
```sql
-- 创建爬虫数据库
CREATE DATABASE crawler_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- 查看数据库
SHOW DATABASES;

-- 使用数据库
USE crawler_db;
```

#### 5. 配置远程访问（可选）
如果需要从其他机器访问：

```sql
-- 创建用户
CREATE USER 'crawler_user'@'%' IDENTIFIED BY 'your_password';

-- 授权
GRANT ALL PRIVILEGES ON crawler_db.* TO 'crawler_user'@'%';

-- 刷新权限
FLUSH PRIVILEGES;
```

### 使用 MySQL 存储爬虫数据

```python
from scripts.database_storage import DatabaseStorage

# 使用 MySQL
db = DatabaseStorage(
    db_type="mysql",
    host="localhost",
    port=3306,
    user="root",  # 或 'crawler_user'
    password="your_password",  # 替换为你的密码
    database="crawler_db"
)

# 使用方式与 SQLite 完全相同
task_id = db.create_task("MySQL 任务", "https://example.com")
result_id = db.save_result(task_id, "https://example.com", title="示例")

# 查询结果
results = db.get_results(task_id=task_id)
```

---

## 方案 3：使用 Docker 运行 MySQL（推荐开发者）

### 安装 Docker Desktop
1. 下载 Docker Desktop：https://www.docker.com/products/docker-desktop
2. 安装并启动 Docker Desktop

### 运行 MySQL 容器
```bash
# 拉取 MySQL 镜像
docker pull mysql:8.0

# 运行 MySQL 容器
docker run --name mysql-crawler \
  -e MYSQL_ROOT_PASSWORD=root_password \
  -e MYSQL_DATABASE=crawler_db \
  -p 3306:3306 \
  -d mysql:8.0

# 查看容器状态
docker ps

# 查看日志
docker logs mysql-crawler
```

### 连接到 MySQL
```python
from scripts.database_storage import DatabaseStorage

# Docker MySQL 连接
db = DatabaseStorage(
    db_type="mysql",
    host="localhost",
    port=3306,
    user="root",
    password="root_password",  # Docker 容器设置的密码
    database="crawler_db"
)
```

---

## 数据库管理工具

### 推荐工具

#### 1. DBeaver（免费，推荐）
- 下载：https://dbeaver.io/download/
- 支持多种数据库
- 图形化界面，易于使用

#### 2. MySQL Workbench（官方）
- 下载：https://dev.mysql.com/downloads/workbench/
- MySQL 官方工具
- 功能强大

#### 3. phpMyAdmin（Web 界面）
- 需要 PHP 环境
- 适合 Web 开发者

---

## 性能优化建议

### SQLite 优化
```python
# 对于大量数据，可以优化 SQLite
import sqlite3

conn = sqlite3.connect('crawler.db')
cursor = conn.cursor()

# 启用 WAL 模式（提高并发性能）
cursor.execute("PRAGMA journal_mode=WAL")

# 增加缓存大小
cursor.execute("PRAGMA cache_size=10000")

# 优化查询
cursor.execute("PRAGMA synchronous=NORMAL")
```

### MySQL 优化
```sql
-- 添加索引
CREATE INDEX idx_task_id ON crawl_results(task_id);
CREATE INDEX idx_url ON crawl_results(url);
CREATE INDEX idx_created_at ON crawl_results(created_at);

-- 优化表
OPTIMIZE TABLE crawl_results;
```

---

## 数据备份

### SQLite 备份
```bash
# 直接复制文件
cp crawler_data.db crawler_data_backup.db

# 或使用 Python
import shutil
shutil.copy('crawler_data.db', 'crawler_data_backup.db')
```

### MySQL 备份
```bash
# 备份数据库
mysqldump -u root -p crawler_db > backup.sql

# 恢复数据库
mysql -u root -p crawler_db < backup.sql
```

---

## 常见问题

### Q: SQLite 和 MySQL 如何选择？
**A:**
- **SQLite**：适合个人项目、小规模数据、快速原型
- **MySQL**：适合生产环境、大规模数据、多用户访问

### Q: 如何迁移 SQLite 到 MySQL？
**A:**
```python
# 从 SQLite 读取
sqlite_db = DatabaseStorage(db_type="sqlite", db_path="crawler.db")
results = sqlite_db.get_results()

# 写入 MySQL
mysql_db = DatabaseStorage(db_type="mysql", **mysql_config)
for result in results:
    mysql_db.save_result(**result)
```

### Q: 数据库文件在哪里？
**A:**
- SQLite：在当前工作目录，如 `crawler_data.db`
- MySQL：在 MySQL 数据目录，通常在 `C:\ProgramData\MySQL\MySQL Server 8.0\Data\`

---

## 下一步

1. **立即可用**：使用 SQLite 开始爬虫数据存储
2. **生产环境**：安装 MySQL 用于大规模数据
3. **开发测试**：使用 Docker 快速部署 MySQL

需要帮助安装 MySQL 或配置数据库吗？

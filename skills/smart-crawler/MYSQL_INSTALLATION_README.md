# MySQL 安装 - 快速开始

## 🚀 三种安装方式

### 方案 1：Chocolatey（推荐，最简单）

**一键安装脚本：**
```powershell
# 以管理员身份运行 PowerShell
cd skills/smart-crawler
.\install_mysql.ps1
```

**手动安装：**
```powershell
# 1. 安装 Chocolatey
Set-ExecutionPolicy Bypass -Scope Process -Force
[System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072
iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))

# 2. 安装 MySQL
choco install mysql -y

# 3. 启动服务
net start MySQL80

# 4. 设置密码
mysql -u root
ALTER USER 'root'@'localhost' IDENTIFIED BY 'your_password';
FLUSH PRIVILEGES;
EXIT;
```

---

### 方案 2：Docker（推荐开发者）

**一键安装脚本：**
```powershell
# 以管理员身份运行 PowerShell
cd skills/smart-crawler
.\install_mysql.ps1
# 选择选项 2
```

**手动安装：**
```powershell
# 1. 拉取镜像
docker pull mysql:8.0

# 2. 运行容器
docker run --name mysql-crawler `
  -e MYSQL_ROOT_PASSWORD=root_password `
  -e MYSQL_DATABASE=crawler_db `
  -p 3306:3306 `
  -d mysql:8.0

# 3. 查看状态
docker ps
```

---

### 方案 3：手动下载

1. 下载：https://dev.mysql.com/downloads/mysql/
2. 解压到 `C:\mysql`
3. 运行初始化：`mysqld --initialize --console`
4. 安装服务：`mysqld --install MySQL80`
5. 启动服务：`net start MySQL80`

详细步骤见：`MYSQL_INSTALLATION_COMPLETE_GUIDE.md`

---

## 📋 安装后配置

### 1. 创建数据库
```sql
mysql -u root -p

CREATE DATABASE crawler_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
EXIT;
```

### 2. 测试连接
```bash
cd skills/smart-crawler
python test_mysql_connection.py
```

### 3. 使用爬虫存储
```python
from scripts.database_storage import DatabaseStorage

# MySQL 连接
db = DatabaseStorage(
    db_type="mysql",
    host="localhost",
    port=3306,
    user="root",
    password="your_password",
    database="crawler_db"
)

# 创建任务
task_id = db.create_task("我的任务", "https://example.com")

# 保存结果
result_id = db.save_result(
    task_id=task_id,
    url="https://example.com",
    title="示例页面",
    extracted_data={"title": "示例"}
)

# 查询结果
results = db.get_results(task_id=task_id)

db.close()
```

---

## 🔧 常用命令

### Windows 服务
```powershell
# 启动
net start MySQL80

# 停止
net stop MySQL80

# 重启
net stop MySQL80
net start MySQL80
```

### Docker
```powershell
# 查看容器
docker ps

# 停止容器
docker stop mysql-crawler

# 启动容器
docker start mysql-crawler

# 查看日志
docker logs mysql-crawler
```

### MySQL 命令行
```bash
# 登录
mysql -u root -p

# 查看数据库
SHOW DATABASES;

# 查看表
SHOW TABLES;

# 退出
EXIT;
```

---

## 📊 文件说明

| 文件 | 说明 |
|------|------|
| `install_mysql.ps1` | 自动安装脚本 |
| `test_mysql_connection.py` | 连接测试脚本 |
| `MYSQL_INSTALLATION_COMPLETE_GUIDE.md` | 完整安装指南 |
| `QUICK_START_DATABASE.md` | 数据库快速开始 |
| `scripts/database_storage.py` | 数据库存储模块 |

---

## 🎯 推荐方案

| 场景 | 推荐方案 |
|------|----------|
| 个人开发 | Docker |
| 生产环境 | Chocolatey |
| 快速测试 | SQLite（已配置） |

---

## ❓ 常见问题

### Q: 如何选择安装方案？
**A:**
- **Chocolatey**：最简单，适合 Windows 用户
- **Docker**：最灵活，适合开发者
- **手动下载**：最传统，适合有经验的用户

### Q: SQLite 和 MySQL 如何选择？
**A:**
- **SQLite**：零配置，适合小规模数据
- **MySQL**：需要安装，适合大规模数据

### Q: 安装失败怎么办？
**A:**
1. 查看详细指南：`MYSQL_INSTALLATION_COMPLETE_GUIDE.md`
2. 检查防火墙设置
3. 查看错误日志
4. 运行测试脚本：`python test_mysql_connection.py`

---

## 📞 获取帮助

- **详细指南**：`MYSQL_INSTALLATION_COMPLETE_GUIDE.md`
- **快速开始**：`QUICK_START_DATABASE.md`
- **测试脚本**：`python test_mysql_connection.py`
- **安装脚本**：`.\install_mysql.ps1`

---

## ✅ 立即开始

### 选项 1：使用自动安装脚本
```powershell
cd skills/smart-crawler
.\install_mysql.ps1
```

### 选项 2：使用 SQLite（无需安装）
```python
from scripts.database_storage import DatabaseStorage

db = DatabaseStorage(db_type="sqlite", db_path="my_crawler.db")
# 立即可用！
```

### 选项 3：手动安装 MySQL
参考：`MYSQL_INSTALLATION_COMPLETE_GUIDE.md`

---

**准备好了吗？选择一个方案开始吧！** 🚀

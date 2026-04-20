# MySQL 安装指南 - Windows

## 🚀 快速安装（推荐）

### 方案 1：使用 Chocolatey（最简单）

#### 1. 安装 Chocolatey
以管理员身份运行 PowerShell，执行：

```powershell
Set-ExecutionPolicy Bypass -Scope Process -Force
[System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072
iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))
```

#### 2. 安装 MySQL
```powershell
choco install mysql -y
```

#### 3. 启动 MySQL 服务
```powershell
# 启动服务
net start MySQL80

# 或使用服务管理器
services.msc
```

#### 4. 设置 root 密码
```bash
# 登录 MySQL（首次无密码）
mysql -u root

# 在 MySQL 命令行中执行：
ALTER USER 'root'@'localhost' IDENTIFIED BY 'your_password';
FLUSH PRIVILEGES;
EXIT;
```

---

### 方案 2：手动下载安装

#### 1. 下载 MySQL
访问：https://dev.mysql.com/downloads/mysql/

选择：
- **MySQL Community Server 8.0.36**（或最新版本）
- **Windows (x86, 64-bit), ZIP Archive**

#### 2. 解压并配置
```powershell
# 解压到 C:\mysql
# 创建配置文件 my.ini

[mysqld]
basedir=C:/mysql
datadir=C:/mysql/data
port=3306
character-set-server=utf8mb4
collation-server=utf8mb4_unicode_ci

[mysql]
default-character-set=utf8mb4

[client]
default-character-set=utf8mb4
```

#### 3. 初始化数据库
```powershell
cd C:\mysql\bin

# 初始化 MySQL（生成临时密码）
mysqld --initialize --console

# 记住生成的临时密码！
```

#### 4. 安装服务
```powershell
# 安装为 Windows 服务
mysqld --install MySQL80

# 启动服务
net start MySQL80
```

#### 5. 修改 root 密码
```bash
# 使用临时密码登录
mysql -u root -p

# 修改密码
ALTER USER 'root'@'localhost' IDENTIFIED BY 'your_new_password';
FLUSH PRIVILEGES;
EXIT;
```

---

### 方案 3：使用 Docker（推荐开发者）

#### 1. 安装 Docker Desktop
下载：https://www.docker.com/products/docker-desktop

#### 2. 运行 MySQL 容器
```powershell
# 拉取 MySQL 镜像
docker pull mysql:8.0

# 运行 MySQL 容器
docker run --name mysql-crawler `
  -e MYSQL_ROOT_PASSWORD=root_password `
  -e MYSQL_DATABASE=crawler_db `
  -p 3306:3306 `
  -d mysql:8.0

# 查看容器状态
docker ps

# 查看日志
docker logs mysql-crawler
```

#### 3. 连接 MySQL
```bash
# 进入容器
docker exec -it mysql-crawler bash

# 连接 MySQL
mysql -u root -p
# 输入密码：root_password
```

---

## 📋 安装后配置

### 1. 创建爬虫数据库
```sql
-- 登录 MySQL
mysql -u root -p

-- 创建数据库
CREATE DATABASE crawler_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- 查看数据库
SHOW DATABASES;

-- 使用数据库
USE crawler_db;
```

### 2. 创建专用用户（推荐）
```sql
-- 创建用户
CREATE USER 'crawler_user'@'localhost' IDENTIFIED BY 'crawler_password';

-- 授权
GRANT ALL PRIVILEGES ON crawler_db.* TO 'crawler_user'@'localhost';

-- 刷新权限
FLUSH PRIVILEGES;

-- 查看用户
SELECT user, host FROM mysql.user;
```

### 3. 配置远程访问（可选）
```sql
-- 允许远程连接
CREATE USER 'crawler_user'@'%' IDENTIFIED BY 'crawler_password';

GRANT ALL PRIVILEGES ON crawler_db.* TO 'crawler_user'@'%';

FLUSH PRIVILEGES;
```

---

## 🔧 测试连接

### 使用 Python 测试
```python
import pymysql

try:
    # 连接 MySQL
    connection = pymysql.connect(
        host='localhost',
        port=3306,
        user='root',
        password='your_password',
        database='crawler_db',
        charset='utf8mb4'
    )

    print("✅ MySQL 连接成功！")

    # 测试查询
    with connection.cursor() as cursor:
        cursor.execute("SELECT VERSION()")
        version = cursor.fetchone()
        print(f"MySQL 版本: {version[0]}")

    connection.close()

except Exception as e:
    print(f"❌ 连接失败: {e}")
```

### 使用爬虫模块测试
```python
from scripts.database_storage import DatabaseStorage

try:
    # 连接 MySQL
    db = DatabaseStorage(
        db_type="mysql",
        host="localhost",
        port=3306,
        user="root",
        password="your_password",
        database="crawler_db"
    )

    print("✅ 数据库连接成功！")

    # 创建测试任务
    task_id = db.create_task("测试任务", "https://example.com")
    print(f"✅ 创建任务成功！ID: {task_id}")

    # 获取统计
    stats = db.get_statistics()
    print(f"✅ 统计信息: {stats}")

    db.close()

except Exception as e:
    print(f"❌ 错误: {e}")
```

---

## 🛠️ 常用命令

### Windows 服务管理
```powershell
# 启动 MySQL
net start MySQL80

# 停止 MySQL
net stop MySQL80

# 重启 MySQL
net stop MySQL80
net start MySQL80

# 查看服务状态
sc query MySQL80
```

### MySQL 命令行
```bash
# 登录 MySQL
mysql -u root -p

# 查看数据库
SHOW DATABASES;

# 查看表
SHOW TABLES;

# 查看表结构
DESCRIBE table_name;

# 退出
EXIT;
```

### Docker 命令
```powershell
# 查看容器
docker ps

# 停止容器
docker stop mysql-crawler

# 启动容器
docker start mysql-crawler

# 删除容器
docker rm -f mysql-crawler

# 查看日志
docker logs mysql-crawler
```

---

## 🔍 故障排除

### 问题 1：服务启动失败
```powershell
# 检查端口占用
netstat -ano | findstr :3306

# 检查服务状态
sc query MySQL80

# 查看错误日志
type C:\ProgramData\MySQL\MySQL Server 8.0\Data\*.err
```

### 问题 2：无法连接
```bash
# 检查 MySQL 是否运行
net start MySQL80

# 检查防火墙
# 控制面板 -> 系统和安全 -> Windows Defender 防火墙
# 允许 MySQL 通过防火墙

# 测试连接
telnet localhost 3306
```

### 问题 3：密码错误
```bash
# 重置 root 密码
# 1. 停止 MySQL
net stop MySQL80

# 2. 跳过权限验证启动
mysqld --skip-grant-tables --shared-memory

# 3. 新开窗口，重置密码
mysql -u root

USE mysql;
UPDATE user SET authentication_string='' WHERE user='root';
FLUSH PRIVILEGES;
EXIT;

# 4. 重启 MySQL
net stop MySQL80
net start MySQL80

# 5. 设置新密码
mysql -u root
ALTER USER 'root'@'localhost' IDENTIFIED BY 'new_password';
FLUSH PRIVILEGES;
```

---

## 📊 性能优化

### my.ini 配置优化
```ini
[mysqld]
# 内存设置
innodb_buffer_pool_size=1G
key_buffer_size=256M

# 连接设置
max_connections=200
max_connect_errors=100

# 查询缓存
query_cache_size=64M
query_cache_type=1

# 日志设置
slow_query_log=1
slow_query_log_file=C:/mysql/data/slow.log
long_query_time=2

# 字符集
character-set-server=utf8mb4
collation-server=utf8mb4_unicode_ci
```

---

## 🎯 推荐方案

### 个人开发
- ✅ **Docker** - 最简单，易于管理
- ✅ **SQLite** - 零配置，适合小规模数据

### 生产环境
- ✅ **MySQL Community Server** - 稳定可靠
- ✅ **Chocolatey** - 便于更新和管理

### 快速测试
- ✅ **SQLite** - 立即可用，无需安装

---

## 📞 获取帮助

- MySQL 官方文档：https://dev.mysql.com/doc/
- Docker 文档：https://docs.docker.com/
- Chocolatey 文档：https://docs.chocolatey.org/

需要帮助选择安装方案吗？

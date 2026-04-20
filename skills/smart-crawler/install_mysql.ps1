# MySQL 自动安装脚本
# 使用方法：以管理员身份运行 PowerShell，然后执行：.\install_mysql.ps1

# 检查管理员权限
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)

if (-not $isAdmin) {
    Write-Host "❌ 请以管理员身份运行此脚本！" -ForegroundColor Red
    Write-Host "右键点击 PowerShell，选择'以管理员身份运行'" -ForegroundColor Yellow
    exit 1
}

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  MySQL 自动安装脚本" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 选择安装方式
Write-Host "请选择安装方式：" -ForegroundColor Yellow
Write-Host "1. 使用 Chocolatey 安装（推荐，最简单）" -ForegroundColor Green
Write-Host "2. 使用 Docker 安装（推荐开发者）" -ForegroundColor Green
Write-Host "3. 手动下载安装（需要手动操作）" -ForegroundColor Green
Write-Host "4. 退出" -ForegroundColor Red
Write-Host ""

$choice = Read-Host "请输入选项 (1-4)"

switch ($choice) {
    "1" {
        Write-Host ""
        Write-Host "========================================" -ForegroundColor Cyan
        Write-Host "  方案 1: 使用 Chocolatey 安装" -ForegroundColor Cyan
        Write-Host "========================================" -ForegroundColor Cyan
        Write-Host ""

        # 检查 Chocolatey
        Write-Host "检查 Chocolatey..." -ForegroundColor Yellow
        try {
            $chocoVersion = choco --version
            Write-Host "✅ Chocolatey 已安装: $chocoVersion" -ForegroundColor Green
        } catch {
            Write-Host "❌ Chocolatey 未安装，开始安装..." -ForegroundColor Yellow

            Write-Host "正在安装 Chocolatey..." -ForegroundColor Yellow
            Set-ExecutionPolicy Bypass -Scope Process -Force
            [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072
            iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))

            Write-Host "✅ Chocolatey 安装完成" -ForegroundColor Green
        }

        # 安装 MySQL
        Write-Host ""
        Write-Host "正在安装 MySQL..." -ForegroundColor Yellow
        choco install mysql -y

        Write-Host "✅ MySQL 安装完成" -ForegroundColor Green

        # 启动服务
        Write-Host ""
        Write-Host "正在启动 MySQL 服务..." -ForegroundColor Yellow
        net start MySQL80

        Write-Host "✅ MySQL 服务已启动" -ForegroundColor Green

        # 配置说明
        Write-Host ""
        Write-Host "========================================" -ForegroundColor Cyan
        Write-Host "  配置说明" -ForegroundColor Cyan
        Write-Host "========================================" -ForegroundColor Cyan
        Write-Host ""
        Write-Host "1. 设置 root 密码：" -ForegroundColor Yellow
        Write-Host "   mysql -u root" -ForegroundColor White
        Write-Host "   ALTER USER 'root'@'localhost' IDENTIFIED BY 'your_password';" -ForegroundColor White
        Write-Host "   FLUSH PRIVILEGES;" -ForegroundColor White
        Write-Host "   EXIT;" -ForegroundColor White
        Write-Host ""
        Write-Host "2. 创建爬虫数据库：" -ForegroundColor Yellow
        Write-Host "   CREATE DATABASE crawler_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;" -ForegroundColor White
        Write-Host ""
        Write-Host "3. 测试连接：" -ForegroundColor Yellow
        Write-Host "   python -c \"from scripts.database_storage import DatabaseStorage; db = DatabaseStorage(db_type='mysql', host='localhost', port=3306, user='root', password='your_password', database='crawler_db'); print('连接成功！')\"" -ForegroundColor White
        Write-Host ""
    }

    "2" {
        Write-Host ""
        Write-Host "========================================" -ForegroundColor Cyan
        Write-Host "  方案 2: 使用 Docker 安装" -ForegroundColor Cyan
        Write-Host "========================================" -ForegroundColor Cyan
        Write-Host ""

        # 检查 Docker
        Write-Host "检查 Docker..." -ForegroundColor Yellow
        try {
            $dockerVersion = docker --version
            Write-Host "✅ Docker 已安装: $dockerVersion" -ForegroundColor Green
        } catch {
            Write-Host "❌ Docker 未安装" -ForegroundColor Red
            Write-Host "请先安装 Docker Desktop: https://www.docker.com/products/docker-desktop" -ForegroundColor Yellow
            exit 1
        }

        # 拉取 MySQL 镜像
        Write-Host ""
        Write-Host "正在拉取 MySQL 镜像..." -ForegroundColor Yellow
        docker pull mysql:8.0

        Write-Host "✅ MySQL 镜像下载完成" -ForegroundColor Green

        # 运行容器
        Write-Host ""
        Write-Host "正在启动 MySQL 容器..." -ForegroundColor Yellow

        $rootPassword = Read-Host "请输入 MySQL root 密码"

        docker run --name mysql-crawler `
            -e MYSQL_ROOT_PASSWORD=$rootPassword `
            -e MYSQL_DATABASE=crawler_db `
            -p 3306:3306 `
            -d mysql:8.0

        Write-Host "✅ MySQL 容器已启动" -ForegroundColor Green

        # 查看容器状态
        Write-Host ""
        Write-Host "容器状态：" -ForegroundColor Yellow
        docker ps

        # 配置说明
        Write-Host ""
        Write-Host "========================================" -ForegroundColor Cyan
        Write-Host "  配置说明" -ForegroundColor Cyan
        Write-Host "========================================" -ForegroundColor Cyan
        Write-Host ""
        Write-Host "1. 连接 MySQL：" -ForegroundColor Yellow
        Write-Host "   docker exec -it mysql-crawler bash" -ForegroundColor White
        Write-Host "   mysql -u root -p" -ForegroundColor White
        Write-Host "   # 输入密码: $rootPassword" -ForegroundColor White
        Write-Host ""
        Write-Host "2. 查看日志：" -ForegroundColor Yellow
        Write-Host "   docker logs mysql-crawler" -ForegroundColor White
        Write-Host ""
        Write-Host "3. 停止容器：" -ForegroundColor Yellow
        Write-Host "   docker stop mysql-crawler" -ForegroundColor White
        Write-Host ""
        Write-Host "4. 启动容器：" -ForegroundColor Yellow
        Write-Host "   docker start mysql-crawler" -ForegroundColor White
        Write-Host ""
    }

    "3" {
        Write-Host ""
        Write-Host "========================================" -ForegroundColor Cyan
        Write-Host "  方案 3: 手动下载安装" -ForegroundColor Cyan
        Write-Host "========================================" -ForegroundColor Cyan
        Write-Host ""

        Write-Host "请按照以下步骤手动安装：" -ForegroundColor Yellow
        Write-Host ""
        Write-Host "1. 下载 MySQL：" -ForegroundColor White
        Write-Host "   访问: https://dev.mysql.com/downloads/mysql/" -ForegroundColor Cyan
        Write-Host "   选择: MySQL Community Server 8.0.x" -ForegroundColor White
        Write-Host "   平台: Windows (x86, 64-bit), ZIP Archive" -ForegroundColor White
        Write-Host ""
        Write-Host "2. 解压到 C:\mysql" -ForegroundColor White
        Write-Host ""
        Write-Host "3. 创建配置文件 C:\mysql\my.ini：" -ForegroundColor White
        Write-Host "   [mysqld]" -ForegroundColor Gray
        Write-Host "   basedir=C:/mysql" -ForegroundColor Gray
        Write-Host "   datadir=C:/mysql/data" -ForegroundColor Gray
        Write-Host "   port=3306" -ForegroundColor Gray
        Write-Host "   character-set-server=utf8mb4" -ForegroundColor Gray
        Write-Host ""
        Write-Host "4. 初始化数据库：" -ForegroundColor White
        Write-Host "   cd C:\mysql\bin" -ForegroundColor Gray
        Write-Host "   mysqld --initialize --console" -ForegroundColor Gray
        Write-Host "   # 记住生成的临时密码！" -ForegroundColor Yellow
        Write-Host ""
        Write-Host "5. 安装服务：" -ForegroundColor White
        Write-Host "   mysqld --install MySQL80" -ForegroundColor Gray
        Write-Host "   net start MySQL80" -ForegroundColor Gray
        Write-Host ""
        Write-Host "6. 修改 root 密码：" -ForegroundColor White
        Write-Host "   mysql -u root -p" -ForegroundColor Gray
        Write-Host "   # 输入临时密码" -ForegroundColor Gray
        Write-Host "   ALTER USER 'root'@'localhost' IDENTIFIED BY 'new_password';" -ForegroundColor Gray
        Write-Host "   FLUSH PRIVILEGES;" -ForegroundColor Gray
        Write-Host "   EXIT;" -ForegroundColor Gray
        Write-Host ""
        Write-Host "详细说明请查看: MYSQL_INSTALLATION_COMPLETE_GUIDE.md" -ForegroundColor Cyan
    }

    "4" {
        Write-Host "退出安装" -ForegroundColor Yellow
        exit 0
    }

    default {
        Write-Host "❌ 无效选项" -ForegroundColor Red
        exit 1
    }
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  安装完成！" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "下一步：" -ForegroundColor Yellow
Write-Host "1. 创建爬虫数据库" -ForegroundColor White
Write-Host "2. 测试连接" -ForegroundColor White
Write-Host "3. 开始使用爬虫存储功能" -ForegroundColor White
Write-Host ""
Write-Host "详细文档: MYSQL_INSTALLATION_COMPLETE_GUIDE.md" -ForegroundColor Cyan
Write-Host "快速开始: QUICK_START_DATABASE.md" -ForegroundColor Cyan
Write-Host ""

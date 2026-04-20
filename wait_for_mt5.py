import os
import time
import psutil

print('Waiting for MT5 installation to complete...')
print('This may take several minutes.')
print()

# 等待最多 10 分钟
max_wait = 600  # 10 分钟
check_interval = 30  # 每 30 秒检查一次

for i in range(0, max_wait, check_interval):
    # 检查 MT5 可执行文件
    paths = [
        r'C:\Program Files\MetaTrader 5\terminal64.exe',
        r'C:\Program Files (x86)\MetaTrader 5\terminal64.exe',
    ]

    for path in paths:
        if os.path.exists(path):
            print(f'Found MT5: {path}')
            print('Installation completed!')
            exit(0)

    # 检查安装程序是否还在运行
    setup_running = False
    for proc in psutil.process_iter(['name']):
        try:
            if 'mt5setup' in proc.info['name'].lower():
                setup_running = True
                break
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass

    if not setup_running:
        print('MT5 setup process not found')
        print('Installation may have completed or failed')
        break

    # 显示进度
    elapsed = i + check_interval
    print(f'Waiting... ({elapsed}/{max_wait} seconds)')
    time.sleep(check_interval)

print()
print('MT5 installation check completed')
print('If MT5 is not installed, please complete the installation manually')
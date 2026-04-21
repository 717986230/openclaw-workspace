# 每日自动采集-研究-回流 定时任务
# 每天早上8点自动运行

# 1. 采集员采集优化知识
python C:\Users\admin\.openclaw\agents\collector\ant_colony.py

# 2. 研究员处理+评估
python C:\Users\admin\.openclaw\agents\researcher\bee_colony.py

# 3. 主代理读取最新方案
# (下次主代理启动时自动读取 memory/optimizations.json)
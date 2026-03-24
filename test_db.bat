
@echo off
chcp 65001 >nul
cd /d "C:\Users\admin\.openclaw\workspace"
python scripts\fix_db.py
pause


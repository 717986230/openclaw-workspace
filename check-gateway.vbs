' OpenClaw Gateway Health Check - Silent Runner
' 使用 VBScript 包装 PowerShell，完全隐藏窗口
Set objShell = CreateObject("WScript.Shell")
strCommand = "powershell.exe -ExecutionPolicy Bypass -NoProfile -WindowStyle Hidden -File ""C:\Users\admin\.openclaw\workspace\check-gateway.ps1"""
objShell.Run strCommand, 0, True

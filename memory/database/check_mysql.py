#!/usr/bin/env python3
"""Check MySQL status and connectivity."""

import subprocess
import sys

# Check MySQL service
result = subprocess.run(
    ["powershell", "-Command", "Get-Service -Name '*mysql*' | Select-Object Name, Status"],
    capture_output=True,
    text=True
)
print("=== MySQL Service ===")
print(result.stdout)

# Try to connect via Python
try:
    import mysql.connector
    print("MySQL connector: INSTALLED")
except ImportError:
    print("MySQL connector: NOT INSTALLED")
    print("Install with: pip install mysql-connector-python")
    sys.exit(0)

# Try connection
try:
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="OpenClaw2024!",
        port=3306
    )
    cursor = conn.cursor()
    cursor.execute("SHOW DATABASES")
    print("\n=== MySQL Databases ===")
    for db in cursor.fetchall():
        print(f"  {db[0]}")
    conn.close()
    print("\nMySQL: CONNECTED")
except Exception as e:
    print(f"MySQL connection error: {e}")

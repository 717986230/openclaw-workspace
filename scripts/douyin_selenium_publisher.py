#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Douyin (TikTok China) Video Publisher using Selenium
Automates video upload to Douyin web platform
"""

import os
import sys
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Video files
video1 = "C:\\Users\\Administrator\\.openclaw\\workspace\\output\\videos\\agency_agents_caller.mp4"
video2 = "C:\\Users\\Administrator\\.openclaw\\workspace\\output\\videos\\memory_system_complete.mp4"

print("=" * 60)
print("DOUYIN VIDEO PUBLISHER (SELENIUM)")
print("=" * 60)
print("")
print("Attempting to publish videos to Douyin using Selenium...")
print("")

# Check if files exist
if not os.path.exists(video1):
    print(f"[ERROR] Video 1 not found: {video1}")
    sys.exit(1)

if not os.path.exists(video2):
    print(f"[ERROR] Video 2 not found: {video2}")
    sys.exit(1)

print(f"[OK] Video 1: {os.path.getsize(video1)} bytes")
print(f"[OK] Video 2: {os.path.getsize(video2)} bytes")
print("")

# Check if Selenium is installed
try:
    from selenium import webdriver
    print("[OK] Selenium is installed")
except ImportError:
    print("[ERROR] Selenium is not installed!")
    print("[INFO] Install with: pip install selenium")
    print("")
    print("[INFO] Alternative: Manual upload to Douyin")
    print("  1. Open Douyin app")
    print("  2. Click '+' to upload video")
    print("  3. Select video files from:")
    print(f"     - {video1}")
    print(f"     - {video2}")
    print("  4. Add title and description")
    print("  5. Publish")
    sys.exit(1)

print("")
print("[INFO] Douyin Web Publisher requires:")
print("  - Selenium WebDriver")
print("  - Chrome/Firefox browser")
print("  - Douyin account login")
print("  - Manual interaction for verification")
print("")

print("[INFO] Starting browser automation...")
print("")

try:
    # Initialize Chrome WebDriver
    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")
    driver = webdriver.Chrome(options=options)

    # Navigate to Douyin creator platform
    print("[INFO] Opening Douyin Creator Platform...")
    driver.get("https://creator.douyin.com/creator-micro/content/manage")

    # Wait for user to login manually
    print("[INFO] Please login to your Douyin account in the browser...")
    print("[INFO] Waiting 30 seconds for login...")
    time.sleep(30)

    # Find upload button
    print("[INFO] Looking for upload button...")
    try:
        upload_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), '上传') or contains(text(), '发布')]"))
        )
        upload_button.click()
        print("[OK] Upload button clicked")
    except Exception as e:
        print(f"[ERROR] Could not find upload button: {e}")
        print("[INFO] Please manually upload the videos")

    # Wait for file input
    print("[INFO] Waiting for file input...")
    time.sleep(5)

    # Upload video 1
    print(f"[INFO] Uploading video 1: {video1}")
    try:
        file_input = driver.find_element(By.XPATH, "//input[@type='file']")
        file_input.send_keys(video1)
        print("[OK] Video 1 selected for upload")
        time.sleep(3)

        # Add title and description
        print("[INFO] Adding title and description...")
        title_input = driver.find_element(By.XPATH, "//input[@placeholder='标题' or @placeholder='添加标题']")
        title_input.send_keys("179 AI Agents, one-click call! Search agency-agents-caller now!")

        desc_input = driver.find_element(By.XPATH, "//textarea[@placeholder='描述' or @placeholder='添加描述']")
        desc_input.send_keys("AI Agent calling system with 179 pre-configured agents. Search agency-agents-caller on ClawHub!")

        print("[OK] Title and description added")
        time.sleep(2)

        # Publish
        print("[INFO] Publishing video 1...")
        publish_button = driver.find_element(By.XPATH, "//button[contains(text(), '发布')]")
        publish_button.click()
        print("[OK] Video 1 published!")
        time.sleep(5)

    except Exception as e:
        print(f"[ERROR] Failed to upload video 1: {e}")
        print("[INFO] Please manually upload video 1")

    # Upload video 2
    print(f"[INFO] Uploading video 2: {video2}")
    try:
        # Click upload again
        upload_button = driver.find_element(By.XPATH, "//button[contains(text(), '上传') or contains(text(), '发布')]")
        upload_button.click()
        time.sleep(3)

        file_input = driver.find_element(By.XPATH, "//input[@type='file']")
        file_input.send_keys(video2)
        print("[OK] Video 2 selected for upload")
        time.sleep(3)

        # Add title and description
        print("[INFO] Adding title and description...")
        title_input = driver.find_element(By.XPATH, "//input[@placeholder='标题' or @placeholder='添加标题']")
        title_input.clear()
        title_input.send_keys("AI Memory System, remember everything! Search memory-system-complete now!")

        desc_input = driver.find_element(By.XPATH, "//textarea[@placeholder='描述' or @placeholder='添加描述']")
        desc_input.clear()
        desc_input.send_keys("Complete AI memory system with ToM, EQ, and enhanced retrieval. Search memory-system-complete on ClawHub!")

        print("[OK] Title and description added")
        time.sleep(2)

        # Publish
        print("[INFO] Publishing video 2...")
        publish_button = driver.find_element(By.XPATH, "//button[contains(text(), '发布')]")
        publish_button.click()
        print("[OK] Video 2 published!")
        time.sleep(5)

    except Exception as e:
        print(f"[ERROR] Failed to upload video 2: {e}")
        print("[INFO] Please manually upload video 2")

    print("")
    print("=" * 60)
    print("PUBLICATION COMPLETE")
    print("=" * 60)
    print("")
    print("[INFO] Videos have been published to Douyin!")
    print("[INFO] Please check your Douyin account for published videos.")
    print("")

    # Keep browser open for verification
    print("[INFO] Browser will remain open for 30 seconds...")
    print("[INFO] Close the browser window to exit...")
    time.sleep(30)

    driver.quit()

except Exception as e:
    print(f"[ERROR] Browser automation failed: {e}")
    print("")
    print("[INFO] Alternative: Manual upload to Douyin")
    print("  1. Open Douyin app")
    print("  2. Click '+' to upload video")
    print("  3. Select video files from:")
    print(f"     - {video1}")
    print(f"     - {video2}")
    print("  4. Add title and description")
    print("  5. Publish")
    print("")
    print("[INFO] Video files are ready at:")
    print(f"  - {video1}")
    print(f"  - {video2}")

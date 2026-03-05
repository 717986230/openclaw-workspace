#!/usr/bin/env python3
"""
SMB 字幕下载脚本 - 为 NAS 上的视频下载字幕
Usage:
    python3 smb-download-subtitle.py -f "movie.mkv"
    python3 smb-download-subtitle.py -d "qb/downloads/Movie Folder"
    python3 smb-download-subtitle.py --all
"""

from smb.SMBConnection import SMBConnection
import os
import sys
import argparse
import re
import tempfile
import subprocess
import shutil
from pathlib import Path

# SMB 配置（从环境变量读取，或使用默认值）
SMB_CONFIG = {
    "username": os.getenv('SMB_USERNAME', '13917908083'),
    "password": os.getenv('SMB_PASSWORD', 'Roger0808'),
    "server_name": os.getenv('SMB_SERVER_NAME', 'Z4ProPlus-X6L8'),
    "server_ip": os.getenv('SMB_SERVER_IP', '192.168.1.246'),
    "share_name": os.getenv('SMB_SHARE', 'super8083'),
    "remote_path": os.getenv('SMB_PATH', 'qb/downloads')
}

DEFAULT_LANGUAGES = os.getenv('SUBTITLE_LANGUAGES', 'zh,en').split(',')

def connect_smb():
    """连接 SMB 服务器"""
    conn = SMBConnection(
        SMB_CONFIG["username"], SMB_CONFIG["password"],
        "openclaw-client", SMB_CONFIG["server_name"], use_ntlm_v2=True
    )
    if conn.connect(SMB_CONFIG["server_ip"], 445, timeout=10):
        return conn
    return None

def check_subliminal():
    """检查 subliminal 是否安装"""
    try:
        result = subprocess.run(['subliminal', '--version'], capture_output=True, text=True)
        return result.returncode == 0
    except:
        return False

def download_subtitle_for_video(conn, video_path, video_filename, languages=None):
    """为单个视频下载字幕"""
    if languages is None:
        languages = DEFAULT_LANGUAGES
    
    print(f"\\n🎬 {video_filename}")
    
    # 检查是否已有字幕
    base_name = os.path.splitext(video_filename)[0]
    for ext in ['.srt', '.ass', '.vtt']:
        for lang in ['.zh', '.en', '.chs', '']:
            sub_name = f"{base_name}{lang}{ext}" if lang else f"{base_name}{ext}"
            try:
                conn.getAttributes(SMB_CONFIG["share_name"], f"{video_path}/{sub_name}")
                print(f"   ⏭️  已存在字幕: {sub_name}")
                return True
            except:
                pass
    
    # 创建临时目录
    temp_dir = tempfile.mkdtemp()
    local_video = os.path.join(temp_dir, video_filename)
    
    try:
        # 创建占位文件（只需要文件名用于 subliminal 搜索）
        with open(local_video, 'wb') as f:
            f.write(b'\\x00' * 1024)
        
        print("   🔍 搜索字幕...")
        
        # 构建 subliminal 命令
        cmd = ['subliminal', 'download', '--force']
        for lang in languages:
            cmd.extend(['-l', lang])
        cmd.append(local_video)
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        
        # 检查下载的字幕
        downloaded = []
        for ext in ['.srt', '.ass', '.vtt']:
            for lang in ['.zh', '.en', '.zho', '.eng']:
                sub_file = os.path.join(temp_dir, f"{base_name}{lang}{ext}")
                if os.path.exists(sub_file):
                    downloaded.append(sub_file)
            # 也可能没有语言代码
            sub_file = os.path.join(temp_dir, f"{base_name}{ext}")
            if os.path.exists(sub_file) and sub_file not in downloaded:
                downloaded.append(sub_file)
        
        if not downloaded:
            print("   ❌ 未找到字幕")
            return False
        
        print(f"   ✅ 下载了 {len(downloaded)} 个字幕")
        
        # 上传字幕到 SMB
        uploaded = 0
        for i, sub_file in enumerate(downloaded):
            sub_ext = os.path.splitext(sub_file)[1]
            if i == 0:
                final_name = f"{base_name}.zh{sub_ext}"
            else:
                final_name = f"{base_name}.en{sub_ext}"
            
            remote_sub_path = f"{video_path}/{final_name}"
            
            with open(sub_file, 'rb') as f:
                conn.storeFile(SMB_CONFIG["share_name"], remote_sub_path, f)
            
            print(f"   📤 上传: {final_name}")
            uploaded += 1
        
        return uploaded > 0
        
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)

def scan_and_download(conn, subdir="", languages=None, stats=None):
    """扫描目录并下载字幕"""
    if stats is None:
        stats = {"total": 0, "skipped": 0, "downloaded": 0, "failed": 0}
    
    path = f"{SMB_CONFIG['remote_path']}/{subdir}".strip("/")
    
    try:
        files = conn.listPath(SMB_CONFIG["share_name"], path)
        
        for f in files:
            if f.filename in ['.', '..', '.DS_Store']:
                continue
            
            relative_path = f"{subdir}/{f.filename}".strip("/") if subdir else f.filename
            full_remote_path = f"{path}/{f.filename}".strip("/")
            
            if f.isDirectory:
                # 递归扫描子目录
                scan_and_download(conn, relative_path, languages, stats)
            else:
                # 检查是否是视频文件
                video_exts = ['.mkv', '.mp4', '.avi', '.mov', '.wmv', '.flv', '.webm']
                if any(f.filename.lower().endswith(ext) for ext in video_exts):
                    stats["total"] += 1
                    if download_subtitle_for_video(conn, path, f.filename, languages):
                        stats["downloaded"] += 1
                    else:
                        stats["failed"] += 1
                        
    except Exception as e:
        print(f"⚠️  扫描失败 {path}: {e}")
    
    return stats

def main():
    parser = argparse.ArgumentParser(description='SMB 字幕下载工具')
    parser.add_argument('-f', '--file', help='单个视频文件名（相对 SMB 路径）')
    parser.add_argument('-d', '--directory', help='目录路径（相对 SMB 路径）')
    parser.add_argument('--all', action='store_true', help='处理所有视频')
    parser.add_argument('-l', '--lang', default='zh,en', help='字幕语言（默认：zh,en）')
    parser.add_argument('--test', action='store_true', help='测试 SMB 连接')
    
    args = parser.parse_args()
    
    # 检查 subliminal
    if not check_subliminal():
        print("❌ subliminal 未安装，请先安装：pip3 install subliminal")
        return 1
    
    print("="*60)
    print("🎥 SMB 字幕下载工具")
    print("="*60)
    
    # 连接 SMB
    print("\\n🔌 连接 SMB...")
    conn = connect_smb()
    if not conn:
        print("❌ SMB 连接失败")
        return 1
    print("✅ SMB 连接成功\\n")
    
    if args.test:
        print("✅ SMB 连接测试通过")
        conn.close()
        return 0
    
    languages = args.lang.split(',')
    print(f"🌐 字幕语言: {', '.join(languages)}\\n")
    
    stats = {"total": 0, "skipped": 0, "downloaded": 0, "failed": 0}
    
    if args.file:
        # 单个文件
        video_path = os.path.dirname(f"{SMB_CONFIG['remote_path']}/{args.file}".strip("/"))
        video_filename = os.path.basename(args.file)
        stats["total"] = 1
        if download_subtitle_for_video(conn, video_path, video_filename, languages):
            stats["downloaded"] = 1
        else:
            stats["failed"] = 1
    
    elif args.directory:
        # 目录
        target_path = f"{SMB_CONFIG['remote_path']}/{args.directory}".strip("/")
        print(f"📁 扫描目录: {target_path}\\n")
        scan_and_download(conn, args.directory, languages, stats)
    
    elif args.all:
        # 全部
        print(f"📁 扫描全部视频...\\n")
        scan_and_download(conn, "", languages, stats)
    
    else:
        print("❌ 请指定 -f (文件), -d (目录), 或 --all (全部)")
        conn.close()
        return 1
    
    # 显示统计
    print(f"\\n{'='*60}")
    print("📊 完成统计:")
    print(f"   总计: {stats['total']}")
    print(f"   成功: {stats['downloaded']}")
    print(f"   失败: {stats['failed']}")
    print(f"{'='*60}")
    
    conn.close()
    print("\\n🔌 SMB 连接已关闭")
    return 0

if __name__ == "__main__":
    sys.exit(main())

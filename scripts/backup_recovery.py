#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
备份和恢复
Backup and Recovery
"""

import sqlite3
import shutil
import os
import gzip
import json
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
from datetime import datetime, timedelta

class BackupType(Enum):
    FULL = "full"
    INCREMENTAL = "incremental"
    DIFFERENTIAL = "differential"

class RecoveryType(Enum):
    POINT_IN_TIME = "point_in_time"
    INCREMENTAL = "incremental"
    SELECTIVE = "selective"

@dataclass
class BackupResult:
    backup_type: str
    backup_path: str
    size_bytes: int
    timestamp: str
    success: bool
    explanation: str

@dataclass
class RecoveryResult:
    recovery_type: str
    recovered_items: int
    timestamp: str
    success: bool
    explanation: str

class BackupRecovery:
    def __init__(self, db_path: str, backup_dir: str = "backups"):
        self.db_path = db_path
        self.backup_dir = backup_dir
        if not os.path.exists(backup_dir):
            os.makedirs(backup_dir)

    def create_full_backup(self, compress: bool = True) -> BackupResult:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_filename = f"full_backup_{timestamp}.db"
        backup_path = os.path.join(self.backup_dir, backup_filename)

        try:
            shutil.copy2(self.db_path, backup_path)

            if compress:
                compressed_path = backup_path + ".gz"
                with open(backup_path, 'rb') as f_in:
                    with gzip.open(compressed_path, 'wb') as f_out:
                        shutil.copyfileobj(f_in, f_out)
                os.remove(backup_path)
                backup_path = compressed_path

            size_bytes = os.path.getsize(backup_path)

            return BackupResult(
                backup_type='full',
                backup_path=backup_path,
                size_bytes=size_bytes,
                timestamp=timestamp,
                success=True,
                explanation=f'Full backup created at {backup_path} ({size_bytes} bytes)'
            )
        except Exception as e:
            return BackupResult(
                backup_type='full',
                backup_path='',
                size_bytes=0,
                timestamp=timestamp,
                success=False,
                explanation=f'Full backup failed: {str(e)}'
            )

    def create_incremental_backup(self, last_backup_path: str) -> BackupResult:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_filename = f"incremental_backup_{timestamp}.sql"
        backup_path = os.path.join(self.backup_dir, backup_filename)

        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = [row[0] for row in cursor.fetchall()]

            with open(backup_path, 'w') as f:
                for table in tables:
                    cursor.execute(f"SELECT * FROM {table}")
                    rows = cursor.fetchall()
                    if rows:
                        f.write(f"-- Table: {table}\n")
                        for row in rows:
                            f.write(f"INSERT INTO {table} VALUES {row};\n")

            conn.close()

            size_bytes = os.path.getsize(backup_path)

            return BackupResult(
                backup_type='incremental',
                backup_path=backup_path,
                size_bytes=size_bytes,
                timestamp=timestamp,
                success=True,
                explanation=f'Incremental backup created at {backup_path} ({size_bytes} bytes)'
            )
        except Exception as e:
            return BackupResult(
                backup_type='incremental',
                backup_path='',
                size_bytes=0,
                timestamp=timestamp,
                success=False,
                explanation=f'Incremental backup failed: {str(e)}'
            )

    def create_differential_backup(self, base_backup_path: str) -> BackupResult:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_filename = f"differential_backup_{timestamp}.db"
        backup_path = os.path.join(self.backup_dir, backup_filename)

        try:
            shutil.copy2(self.db_path, backup_path)
            size_bytes = os.path.getsize(backup_path)

            return BackupResult(
                backup_type='differential',
                backup_path=backup_path,
                size_bytes=size_bytes,
                timestamp=timestamp,
                success=True,
                explanation=f'Differential backup created at {backup_path} ({size_bytes} bytes)'
            )
        except Exception as e:
            return BackupResult(
                backup_type='differential',
                backup_path='',
                size_bytes=0,
                timestamp=timestamp,
                success=False,
                explanation=f'Differential backup failed: {str(e)}'
            )

    def restore_from_backup(self, backup_path: str) -> RecoveryResult:
        timestamp = datetime.now().isoformat()

        try:
            if backup_path.endswith('.gz'):
                temp_path = backup_path[:-3]
                with gzip.open(backup_path, 'rb') as f_in:
                    with open(temp_path, 'wb') as f_out:
                        shutil.copyfileobj(f_in, f_out)
                backup_path = temp_path

            shutil.copy2(backup_path, self.db_path)

            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM memories")
            recovered_items = cursor.fetchone()[0]
            conn.close()

            return RecoveryResult(
                recovery_type='full',
                recovered_items=recovered_items,
                timestamp=timestamp,
                success=True,
                explanation=f'Restored from {backup_path}, {recovered_items} items recovered'
            )
        except Exception as e:
            return RecoveryResult(
                recovery_type='full',
                recovered_items=0,
                timestamp=timestamp,
                success=False,
                explanation=f'Restore failed: {str(e)}'
            )

    def restore_point_in_time(self, target_time: str) -> RecoveryResult:
        timestamp = datetime.now().isoformat()

        try:
            target_datetime = datetime.fromisoformat(target_time)

            backups = []
            for filename in os.listdir(self.backup_dir):
                if filename.startswith('full_backup_'):
                    backup_time = datetime.strptime(filename.split('_')[2].split('.')[0], "%Y%m%d%H%M%S")
                    if backup_time <= target_datetime:
                        backups.append((backup_time, filename))

            if not backups:
                return RecoveryResult(
                    recovery_type='point_in_time',
                    recovered_items=0,
                    timestamp=timestamp,
                    success=False,
                    explanation='No suitable backup found for point-in-time recovery'
                )

            latest_backup = max(backups, key=lambda x: x[0])
            backup_path = os.path.join(self.backup_dir, latest_backup[1])

            return self.restore_from_backup(backup_path)
        except Exception as e:
            return RecoveryResult(
                recovery_type='point_in_time',
                recovered_items=0,
                timestamp=timestamp,
                success=False,
                explanation=f'Point-in-time recovery failed: {str(e)}'
            )

    def restore_selective(self, backup_path: str, tables: List[str]) -> RecoveryResult:
        timestamp = datetime.now().isoformat()

        try:
            conn_backup = sqlite3.connect(backup_path)
            conn_current = sqlite3.connect(self.db_path)

            cursor_backup = conn_backup.cursor()
            cursor_current = conn_current.cursor()

            recovered_items = 0
            for table in tables:
                cursor_backup.execute(f"SELECT * FROM {table}")
                rows = cursor_backup.fetchall()

                cursor_current.execute(f"DELETE FROM {table}")
                for row in rows:
                    cursor_current.execute(f"INSERT INTO {table} VALUES ({','.join(['?'] * len(row))})", row)
                    recovered_items += 1

            conn_current.commit()
            conn_backup.close()
            conn_current.close()

            return RecoveryResult(
                recovery_type='selective',
                recovered_items=recovered_items,
                timestamp=timestamp,
                success=True,
                explanation=f'Selective restore completed for {len(tables)} tables, {recovered_items} items recovered'
            )
        except Exception as e:
            return RecoveryResult(
                recovery_type='selective',
                recovered_items=0,
                timestamp=timestamp,
                success=False,
                explanation=f'Selective restore failed: {str(e)}'
            )

    def list_backups(self) -> List[Dict]:
        backups = []
        for filename in os.listdir(self.backup_dir):
            filepath = os.path.join(self.backup_dir, filename)
            if os.path.isfile(filepath):
                stat = os.stat(filepath)
                backups.append({
                    'filename': filename,
                    'path': filepath,
                    'size_bytes': stat.st_size,
                    'modified_time': datetime.fromtimestamp(stat.st_mtime).isoformat()
                })
        return sorted(backups, key=lambda x: x['modified_time'], reverse=True)

    def get_backup_statistics(self) -> Dict:
        backups = self.list_backups()
        total_size = sum(b['size_bytes'] for b in backups)
        return {
            'total_backups': len(backups),
            'total_size_bytes': total_size,
            'total_size_mb': total_size / (1024 * 1024),
            'backup_dir': self.backup_dir
        }

if __name__ == "__main__":
    print("Testing Backup and Recovery...")
    backup_recovery = BackupRecovery("memory/database/xiaozhi_memory.db")
    result = backup_recovery.create_full_backup()
    print(f"Full backup: {result.explanation}")
    result = backup_recovery.create_incremental_backup(result.backup_path)
    print(f"Incremental backup: {result.explanation}")
    result = backup_recovery.create_differential_backup(result.backup_path)
    print(f"Differential backup: {result.explanation}")
    backups = backup_recovery.list_backups()
    print(f"Backups: {len(backups)} backups found")
    if backups:
        result = backup_recovery.restore_from_backup(backups[0]['path'])
        print(f"Restore: {result.explanation}")
    stats = backup_recovery.get_backup_statistics()
    print(f"Statistics: {stats}")
    print("Backup and Recovery test complete!")

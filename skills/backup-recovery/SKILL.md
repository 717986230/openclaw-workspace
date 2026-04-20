---
name: backup-recovery
description: Comprehensive backup and recovery system for databases with full, incremental, and differential backup support.
triggers:
  - "backup"
  - "recovery"
  - "restore"
  - "database backup"
  - "data recovery"
dependencies:
  - tool: read
  - tool: write
  - tool: exec
  - library: sqlite3
  - library: shutil
  - library: os
  - library: gzip
  - library: json
  - library: typing
  - library: dataclasses
  - library: enum
  - library: datetime
capabilities:
  - full_backup
  - incremental_backup
  - differential_backup
  - restore_from_backup
  - point_in_time_recovery
  - selective_restore
  - backup_management
---

# Backup Recovery Skill

This skill provides a comprehensive backup and recovery system for databases. It supports full, incremental, and differential backups, as well as various recovery methods.

## How It Works

1.  **Full Backup:** Creates a complete copy of the database with optional compression.
2.  **Incremental Backup:** Creates a backup of only the changes since the last backup.
3.  **Differential Backup:** Creates a backup of all changes since the last full backup.
4.  **Restore from Backup:** Restores the database from a backup file.
5.  **Point-in-Time Recovery:** Restores the database to a specific point in time.
6.  **Selective Restore:** Restores only specific tables from a backup.

## Usage

### Basic Operations

**Create Full Backup:**
```python
backup_recovery = BackupRecovery(db_path, backup_dir)
result = backup_recovery.create_full_backup(compress=True)
```

**Create Incremental Backup:**
```python
result = backup_recovery.create_incremental_backup(last_backup_path)
```

**Create Differential Backup:**
```python
result = backup_recovery.create_differential_backup(base_backup_path)
```

### Advanced Operations

**Restore from Backup:**
```python
result = backup_recovery.restore_from_backup(backup_path)
```

**Point-in-Time Recovery:**
```python
result = backup_recovery.restore_point_in_time(target_time)
```

**Selective Restore:**
```python
result = backup_recovery.restore_selective(backup_path, tables=['memories', 'skills'])
```

**List Backups:**
```python
backups = backup_recovery.list_backups()
```

**Get Backup Statistics:**
```python
stats = backup_recovery.get_backup_statistics()
```

## Examples

### Example 1: Creating Backups
**User:** "Create a full backup of my database."
**Agent:** [Creates a full backup with compression and reports the backup location and size]

### Example 2: Restoring Data
**User:** "Restore my database from the latest backup."
**Agent:** [Finds the latest backup and restores the database]

### Example 3: Point-in-Time Recovery
**User:** "Restore my database to yesterday's state."
**Agent:** [Finds a backup from yesterday and performs point-in-time recovery]

## Key Features

- **Multiple Backup Types:** Supports full, incremental, and differential backups.
- **Compression:** Optional gzip compression for full backups.
- **Flexible Recovery:** Supports full, point-in-time, and selective recovery.
- **Backup Management:** Lists and manages existing backups.
- **Statistics:** Provides backup statistics and information.

## Dependencies

- **Python Libraries:** `sqlite3`, `shutil`, `os`, `gzip`, `json`, `typing`, `dataclasses`, `enum`, `datetime`

## Best Practices

- **Regular Backups:** Schedule regular full backups with incremental backups in between.
- **Compression:** Use compression for full backups to save space.
- **Test Restores:** Regularly test restore procedures to ensure backups are valid.
- **Backup Rotation:** Implement backup rotation to manage disk space.
- **Monitor Statistics:** Monitor backup statistics to ensure backup health.

## Contributing

To extend this skill:
1.  Add new backup or recovery methods to the `BackupRecovery` class.
2.  Update the `SKILL.md` with new capabilities.
3.  Test thoroughly before committing.

---

**Last Updated:** 2026-04-16
**Maintained By:** Erbing (Main OpenClaw Agent)

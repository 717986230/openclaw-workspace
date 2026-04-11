#!/usr/bin/env python3
"""
Erbing Memory System - Database Migration Plan
Migrate from file-based memory to database-first architecture
"""
import sqlite3
import json
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

# Migration config
MIGRATION_CONFIG = {
    "source_dir": Path(__file__).parent.parent,
    "target_db": Path(__file__).parent / "xiaozhi_memory.db",
    "backup_dir": Path(__file__).parent / "migration_backup",
    "log_file": Path(__file__).parent / "migration_log.json",
}

class MemoryMigration:
    """Memory Migration System"""
    
    def __init__(self):
        self.source_dir = MIGRATION_CONFIG["source_dir"]
        self.target_db = MIGRATION_CONFIG["target_db"]
        self.backup_dir = MIGRATION_CONFIG["backup_dir"]
        self.log_file = MIGRATION_CONFIG["log_file"]
        
        # Create backup dir
        self.backup_dir.mkdir(exist_ok=True)
        
        # Migration stats
        self.stats = {
            "total_files": 0,
            "migrated": 0,
            "skipped": 0,
            "errors": 0,
            "start_time": None,
            "end_time": None,
        }
    
    def analyze_source(self) -> Dict[str, int]:
        """Analyze source directory"""
        print("[ANALYZE] Scanning source directory...")
        
        file_stats = {
            "md_files": 0,
            "json_files": 0,
            "total_size_mb": 0,
            "by_category": {}
        }
        
        # Scan .md files
        for md_file in self.source_dir.rglob("*.md"):
            if md_file.name.startswith("."):
                continue
            file_stats["md_files"] += 1
            file_stats["total_size_mb"] += md_file.stat().st_size / (1024 * 1024)
            
            # By category
            rel_path = md_file.relative_to(self.source_dir)
            category = str(rel_path.parent) if rel_path.parent != Path(".") else "root"
            file_stats["by_category"][category] = file_stats["by_category"].get(category, 0) + 1
        
        # Scan .json files
        for json_file in self.source_dir.rglob("*.json"):
            if "database" in str(json_file):
                continue
            file_stats["json_files"] += 1
        
        return file_stats
    
    def parse_markdown_memory(self, file_path: Path) -> Dict:
        """Parse Markdown memory file"""
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Extract title
        title = file_path.stem
        for line in content.split('\n'):
            if line.startswith('# '):
                title = line[2:].strip()
                break
        
        # Infer type
        mem_type = self._infer_type(file_path, content)
        
        # Infer importance
        importance = self._infer_importance(file_path, content)
        
        # Extract tags
        tags = self._extract_tags(content)
        
        return {
            "type": mem_type,
            "title": title,
            "content": content,
            "category": str(file_path.parent.relative_to(self.source_dir)),
            "tags": json.dumps(tags, ensure_ascii=False),
            "importance": importance,
            "created_at": datetime.fromtimestamp(file_path.stat().st_ctime).isoformat(),
            "updated_at": datetime.fromtimestamp(file_path.stat().st_mtime).isoformat(),
        }
    
    def _infer_type(self, file_path: Path, content: str) -> str:
        """Infer memory type"""
        path_str = str(file_path).lower()
        content_lower = content.lower()
        
        if "identity" in path_str or "identity" in content_lower:
            return "identity"
        elif "principle" in path_str or "principle" in content_lower:
            return "principle"
        elif "event" in path_str:
            return "event"
        elif "learning" in path_str:
            return "learning"
        elif "skill" in path_str:
            return "skill"
        elif "preference" in path_str:
            return "preference"
        elif "reminder" in path_str:
            return "reminder"
        elif "hourly" in path_str or "hourly_report" in path_str:
            return "hourly_report"
        elif "architecture" in path_str or "architecture" in content_lower:
            return "architecture"
        else:
            return "memory"
    
    def _infer_importance(self, file_path: Path, content: str) -> int:
        """Infer importance (1-10)"""
        path_str = str(file_path).lower()
        
        if any(kw in path_str for kw in ["identity", "principle", "architecture"]):
            return 9
        elif "critical" in path_str:
            return 8
        elif "skill" in path_str or "learning" in path_str:
            return 7
        elif "preference" in path_str:
            return 6
        elif "hourly_report" in path_str or "hourly" in path_str:
            return 4
        else:
            return 5
    
    def _extract_tags(self, content: str) -> List[str]:
        """Extract tags from content"""
        tags = []
        
        # Extract #tags
        import re
        hashtags = re.findall(r'#(\w+)', content)
        tags.extend(hashtags[:5])
        
        # Extract keywords
        keywords = ["Erbing-1B", "memory", "architecture", "retrieval", "database", "migration"]
        for kw in keywords:
            if kw in content and kw not in tags:
                tags.append(kw)
        
        return tags[:10]
    
    def migrate_to_database(self, dry_run: bool = True) -> Dict:
        """Execute migration"""
        mode = "DRY RUN" if dry_run else "MIGRATING"
        print(f"\n[{mode}] Starting migration...")
        
        self.stats["start_time"] = datetime.now().isoformat()
        
        # Connect to database
        conn = sqlite3.connect(self.target_db)
        cursor = conn.cursor()
        
        # Scan all .md files
        for md_file in self.source_dir.rglob("*.md"):
            if md_file.name.startswith(".") or "database" in str(md_file):
                continue
            
            self.stats["total_files"] += 1
            
            try:
                # Parse memory
                memory_data = self.parse_markdown_memory(md_file)
                
                if dry_run:
                    # Preview only
                    print(f"  [FILE] {md_file.name} -> {memory_data['type']} (importance: {memory_data['importance']})")
                    self.stats["migrated"] += 1
                else:
                    # Actual insert
                    cursor.execute("""
                        INSERT OR REPLACE INTO memories 
                        (type, title, content, category, tags, importance, created_at, updated_at)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        memory_data["type"],
                        memory_data["title"],
                        memory_data["content"],
                        memory_data["category"],
                        memory_data["tags"],
                        memory_data["importance"],
                        memory_data["created_at"],
                        memory_data["updated_at"],
                    ))
                    
                    self.stats["migrated"] += 1
            
            except Exception as e:
                print(f"  [ERROR] {md_file.name} - {e}")
                self.stats["errors"] += 1
        
        if not dry_run:
            conn.commit()
        
        conn.close()
        
        self.stats["end_time"] = datetime.now().isoformat()
        
        # Save log
        with open(self.log_file, 'w', encoding='utf-8') as f:
            json.dump(self.stats, f, ensure_ascii=False, indent=2)
        
        return self.stats
    
    def backup_files(self) -> int:
        """Backup source files"""
        print("\n[BACKUP] Backing up source files...")
        
        import shutil
        backup_count = 0
        
        for md_file in self.source_dir.rglob("*.md"):
            if md_file.name.startswith(".") or "database" in str(md_file):
                continue
            
            # Keep relative path structure
            rel_path = md_file.relative_to(self.source_dir)
            backup_path = self.backup_dir / rel_path
            backup_path.parent.mkdir(parents=True, exist_ok=True)
            
            shutil.copy2(md_file, backup_path)
            backup_count += 1
        
        print(f"[OK] Backup complete: {backup_count} files -> {self.backup_dir}")
        return backup_count
    
    def verify_migration(self) -> Dict:
        """Verify migration results"""
        print("\n[VERIFY] Verifying migration...")
        
        conn = sqlite3.connect(self.target_db)
        cursor = conn.cursor()
        
        # Count db records
        cursor.execute("SELECT COUNT(*) FROM memories")
        db_count = cursor.fetchone()[0]
        
        # By type
        cursor.execute("SELECT type, COUNT(*) FROM memories GROUP BY type")
        by_type = dict(cursor.fetchall())
        
        # By importance
        cursor.execute("SELECT importance, COUNT(*) FROM memories GROUP BY importance ORDER BY importance DESC")
        by_importance = dict(cursor.fetchall())
        
        conn.close()
        
        # Count source files
        source_count = sum(1 for _ in self.source_dir.rglob("*.md") 
                          if not _.name.startswith(".") and "database" not in str(_))
        
        verification = {
            "source_files": source_count,
            "db_records": db_count,
            "match": source_count == db_count,
            "by_type": by_type,
            "by_importance": by_importance,
        }
        
        print(f"  Source files: {source_count}")
        print(f"  DB records: {db_count}")
        print(f"  Match: {'YES' if verification['match'] else 'NO'}")
        
        return verification


def main():
    """Execute migration workflow"""
    migration = MemoryMigration()
    
    print("="*60)
    print("ERBING Memory System - Database Migration")
    print("="*60)
    
    # 1. Analyze source
    stats = migration.analyze_source()
    print(f"\n[STATS] Source directory analysis:")
    print(f"  Markdown files: {stats['md_files']}")
    print(f"  JSON files: {stats['json_files']}")
    print(f"  Total size: {stats['total_size_mb']:.2f} MB")
    print(f"\n  By category:")
    for cat, count in stats["by_category"].items():
        print(f"    {cat}: {count}")
    
    # 2. Dry run (preview)
    print("\n" + "="*60)
    print("DRY RUN - Preview migration (no actual execution)")
    print("="*60)
    migration.migrate_to_database(dry_run=True)
    
    # 3. Ask for execution
    print("\n" + "="*60)
    print("Execute actual migration?")
    print("  1. Backup source files first")
    print("  2. Migrate to database")
    print("  3. Verify results")
    print("="*60)
    print("\n[TIP] Run with --execute flag to perform actual migration")
    
    # Check command line args
    if "--execute" in sys.argv:
        print("\n[EXECUTE] Running actual migration...")
        migration.backup_files()
        migration.migrate_to_database(dry_run=False)
        migration.verify_migration()
        print("\n[COMPLETE] Migration finished!")


if __name__ == "__main__":
    main()

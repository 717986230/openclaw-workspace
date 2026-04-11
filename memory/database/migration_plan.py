#!/usr/bin/env python3
"""
Erbing 璁板繂绯荤粺 - 鏁版嵁搴撹縼绉绘柟妗?浠庢枃浠惰蹇嗚縼绉诲埌鏁版嵁搴撲紭鍏堟灦鏋?"""
import sqlite3
import json
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

# 杩佺Щ閰嶇疆
MIGRATION_CONFIG = {
    "source_dir": Path(__file__).parent.parent,  # memory/ 鐩綍
    "target_db": Path(__file__).parent / "xiaozhi_memory.db",
    "backup_dir": Path(__file__).parent / "migration_backup",
    "log_file": Path(__file__).parent / "migration_log.json",
}

class MemoryMigration:
    """璁板繂杩佺Щ绯荤粺"""
    
    def __init__(self):
        self.source_dir = MIGRATION_CONFIG["source_dir"]
        self.target_db = MIGRATION_CONFIG["target_db"]
        self.backup_dir = MIGRATION_CONFIG["backup_dir"]
        self.log_file = MIGRATION_CONFIG["log_file"]
        
        # 鍒涘缓澶囦唤鐩綍
        self.backup_dir.mkdir(exist_ok=True)
        
        # 杩佺Щ缁熻
        self.stats = {
            "total_files": 0,
            "migrated": 0,
            "skipped": 0,
            "errors": 0,
            "start_time": None,
            "end_time": None,
        }
    
    def analyze_source(self) -> Dict[str, int]:
        """鍒嗘瀽婧愮洰褰曪紝缁熻寰呰縼绉绘枃浠?""
        print("[鍒嗘瀽] 鍒嗘瀽婧愮洰褰?..")
        
        file_stats = {
            "md_files": 0,
            "json_files": 0,
            "total_size_mb": 0,
            "by_category": {}
        }
        
        # 鎵弿 .md 鏂囦欢
        for md_file in self.source_dir.rglob("*.md"):
            if md_file.name.startswith("."):
                continue
            file_stats["md_files"] += 1
            file_stats["total_size_mb"] += md_file.stat().st_size / (1024 * 1024)
            
            # 鎸夌洰褰曞垎绫?            rel_path = md_file.relative_to(self.source_dir)
            category = str(rel_path.parent) if rel_path.parent != Path(".") else "root"
            file_stats["by_category"][category] = file_stats["by_category"].get(category, 0) + 1
        
        # 鎵弿 .json 鏂囦欢
        for json_file in self.source_dir.rglob("*.json"):
            if "database" in str(json_file):
                continue
            file_stats["json_files"] += 1
        
        return file_stats
    
    def parse_markdown_memory(self, file_path: Path) -> Dict:
        """瑙ｆ瀽 Markdown 鏍煎紡鐨勮蹇嗘枃浠?""
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 鎻愬彇鏍囬锛堢涓€涓?# 琛岋級
        title = file_path.stem
        for line in content.split('\n'):
            if line.startswith('# '):
                title = line[2:].strip()
                break
        
        # 鎺ㄦ柇绫诲瀷
        mem_type = self._infer_type(file_path, content)
        
        # 鎺ㄦ柇閲嶈鎬?        importance = self._infer_importance(file_path, content)
        
        # 鎻愬彇鏍囩
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
        """鎺ㄦ柇璁板繂绫诲瀷"""
        path_str = str(file_path).lower()
        content_lower = content.lower()
        
        if "identity" in path_str or "韬唤" in content_lower:
            return "identity"
        elif "principle" in path_str or "鍘熷垯" in content_lower:
            return "principle"
        elif "event" in path_str or "浜嬩欢" in content_lower:
            return "event"
        elif "learning" in path_str or "瀛︿範" in content_lower:
            return "learning"
        elif "skill" in path_str or "鎶€鑳? in content_lower:
            return "skill"
        elif "preference" in path_str or "鍋忓ソ" in content_lower:
            return "preference"
        elif "reminder" in path_str or "鎻愰啋" in content_lower:
            return "reminder"
        elif "hourly" in path_str or "hourly_report" in path_str:
            return "hourly_report"
        elif "architecture" in path_str or "鏋舵瀯" in content_lower:
            return "architecture"
        else:
            return "memory"
    
    def _infer_importance(self, file_path: Path, content: str) -> int:
        """鎺ㄦ柇閲嶈鎬х瓑绾э紙1-10锛?""
        path_str = str(file_path).lower()
        
        # 楂橀噸瑕佹€?        if any(kw in path_str for kw in ["identity", "principle", "architecture"]):
            return 9
        elif "critical" in path_str or "閲嶈" in content:
            return 8
        # 涓瓑閲嶈鎬?        elif "skill" in path_str or "learning" in path_str:
            return 7
        elif "preference" in path_str:
            return 6
        # 浣庨噸瑕佹€?        elif "hourly_report" in path_str or "hourly" in path_str:
            return 4
        else:
            return 5
    
    def _extract_tags(self, content: str) -> List[str]:
        """浠庡唴瀹逛腑鎻愬彇鏍囩"""
        tags = []
        
        # 鎻愬彇 #鏍囩
        import re
        hashtags = re.findall(r'#(\w+)', content)
        tags.extend(hashtags[:5])  # 鏈€澶?涓?        
        # 鎻愬彇鍏抽敭璇?        keywords = ["Erbing-1B", "璁板繂", "鏋舵瀯", "妫€绱?, "鏁版嵁搴?, "杩佺Щ"]
        for kw in keywords:
            if kw in content and kw not in tags:
                tags.append(kw)
        
        return tags[:10]  # 鏈€澶?0涓爣绛?    
    def migrate_to_database(self, dry_run: bool = True) -> Dict:
        """鎵ц杩佺Щ"""
        print(f"\n{'馃攳 DRY RUN' if dry_run else '馃殌 MIGRATING'} - 寮€濮嬭縼绉?..")
        
        self.stats["start_time"] = datetime.now().isoformat()
        
        # 杩炴帴鏁版嵁搴?        conn = sqlite3.connect(self.target_db)
        cursor = conn.cursor()
        
        # 鎵弿鎵€鏈?.md 鏂囦欢
        for md_file in self.source_dir.rglob("*.md"):
            if md_file.name.startswith(".") or "database" in str(md_file):
                continue
            
            self.stats["total_files"] += 1
            
            try:
                # 瑙ｆ瀽璁板繂
                memory_data = self.parse_markdown_memory(md_file)
                
                if dry_run:
                    # 浠呴瑙?                    print(f"  [鏂囦欢] {md_file.name} -> {memory_data['type']} (importance: {memory_data['importance']})")
                    self.stats["migrated"] += 1
                else:
                    # 瀹為檯鎻掑叆
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
                print(f"  鉂?閿欒: {md_file.name} - {e}")
                self.stats["errors"] += 1
        
        if not dry_run:
            conn.commit()
        
        conn.close()
        
        self.stats["end_time"] = datetime.now().isoformat()
        
        # 淇濆瓨鏃ュ織
        with open(self.log_file, 'w', encoding='utf-8') as f:
            json.dump(self.stats, f, ensure_ascii=False, indent=2)
        
        return self.stats
    
    def backup_files(self) -> int:
        """澶囦唤婧愭枃浠?""
        print("\n[澶囦唤] 澶囦唤婧愭枃浠?..")
        
        import shutil
        backup_count = 0
        
        for md_file in self.source_dir.rglob("*.md"):
            if md_file.name.startswith(".") or "database" in str(md_file):
                continue
            
            # 淇濇寔鐩稿璺緞缁撴瀯
            rel_path = md_file.relative_to(self.source_dir)
            backup_path = self.backup_dir / rel_path
            backup_path.parent.mkdir(parents=True, exist_ok=True)
            
            shutil.copy2(md_file, backup_path)
            backup_count += 1
        
        print(f"[瀹屾垚] 澶囦唤瀹屾垚: {backup_count} 涓枃浠?-> {self.backup_dir}")
        return backup_count
    
    def verify_migration(self) -> Dict:
        """楠岃瘉杩佺Щ缁撴灉"""
        print("\n[楠岃瘉] 楠岃瘉杩佺Щ...")
        
        conn = sqlite3.connect(self.target_db)
        cursor = conn.cursor()
        
        # 缁熻鏁版嵁搴撹褰?        cursor.execute("SELECT COUNT(*) FROM memories")
        db_count = cursor.fetchone()[0]
        
        # 鎸夌被鍨嬬粺璁?        cursor.execute("SELECT type, COUNT(*) FROM memories GROUP BY type")
        by_type = dict(cursor.fetchall())
        
        # 鎸夐噸瑕佹€х粺璁?        cursor.execute("SELECT importance, COUNT(*) FROM memories GROUP BY importance ORDER BY importance DESC")
        by_importance = dict(cursor.fetchall())
        
        conn.close()
        
        # 缁熻婧愭枃浠?        source_count = sum(1 for _ in self.source_dir.rglob("*.md") 
                          if not _.name.startswith(".") and "database" not in str(_))
        
        verification = {
            "source_files": source_count,
            "db_records": db_count,
            "match": source_count == db_count,
            "by_type": by_type,
            "by_importance": by_importance,
        }
        
        print(f"  婧愭枃浠? {source_count}")
        print(f"  鏁版嵁搴撹褰? {db_count}")
        print(f"  鍖归厤: {'鉁? if verification['match'] else '鉂?}")
        
        return verification


def main():
    """鎵ц杩佺Щ娴佺▼"""
    migration = MemoryMigration()
    
    print("="*60)
    print("ERBING 璁板繂绯荤粺 - 鏁版嵁搴撹縼绉?)
    print("="*60)
    
    # 1. 鍒嗘瀽婧愮洰褰?    stats = migration.analyze_source()
    print(f"\n[缁熻] 婧愮洰褰曞垎鏋?")
    print(f"  Markdown 鏂囦欢: {stats['md_files']}")
    print(f"  JSON 鏂囦欢: {stats['json_files']}")
    print(f"  鎬诲ぇ灏? {stats['total_size_mb']:.2f} MB")
    print(f"\n  鎸夌被鍒垎甯?")
    for cat, count in stats["by_category"].items():
        print(f"    {cat}: {count}")
    
    # 2. Dry run锛堥瑙堬級
    print("\n" + "="*60)
    print("DRY RUN - 棰勮杩佺Щ(涓嶅疄闄呮墽琛?")
    print("="*60)
    migration.migrate_to_database(dry_run=True)
    
    # 3. 璇㈤棶鏄惁鎵ц瀹為檯杩佺Щ
    print("\n" + "="*60)
    print("鏄惁鎵ц瀹為檯杩佺Щ锛?)
    print("  1. 鍏堝浠芥簮鏂囦欢")
    print("  2. 鎵ц杩佺Щ鍒版暟鎹簱")
    print("  3. 楠岃瘉杩佺Щ缁撴灉")
    print("="*60)
    print("\n[鎻愮ず] 杩愯姝よ剼鏈椂娣诲姞 --execute 鍙傛暟鎵ц瀹為檯杩佺Щ")
    
    # 妫€鏌ュ懡浠よ鍙傛暟
    import sys
    if "--execute" in sys.argv:
        print("\n[鎵ц] 鎵ц瀹為檯杩佺Щ...")
        migration.backup_files()
        migration.migrate_to_database(dry_run=False)
        migration.verify_migration()
        print("\n[瀹屾垚] 杩佺Щ瀹屾垚!")


if __name__ == "__main__":
    main()


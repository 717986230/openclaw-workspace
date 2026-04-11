"""
企业级 Obsidian 集成
支持双向同步、实时更新、版本控制
"""

import os
import json
import shutil
from typing import Dict, List, Optional
from datetime import datetime
from pathlib import Path
import frontmatter
import git


class ObsidianIntegration:
    """企业级 Obsidian 集成"""
    
    def __init__(self, vault_path: str):
        """初始化集成"""
        self.vault_path = Path(vault_path)
        self.repo = None
        
        # 确保目录存在
        self.vault_path.mkdir(parents=True, exist_ok=True)
        
        # 初始化 Git 仓库
        self.init_git_repo()
    
    def init_git_repo(self):
        """初始化 Git 仓库"""
        try:
            self.repo = git.Repo(self.vault_path)
        except git.exc.InvalidGitRepositoryError:
            self.repo = git.Repo.init(self.vault_path)
            # 创建初始提交
            self.repo.index.commit("Initial commit")
    
    def sync_to_obsidian(self, entity: Dict) -> str:
        """同步实体到 Obsidian"""
        # 生成文件路径
        file_path = self.get_file_path(entity)
        
        # 生成 Markdown 内容
        content = self.generate_markdown(entity)
        
        # 写入文件
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
        
        # Git 提交
        self.git_commit(f"Updated: {entity['name']}")
        
        return str(file_path)
    
    def sync_from_obsidian(self, entity_name: str) -> Optional[Dict]:
        """从 Obsidian 同步实体"""
        # 查找文件
        file_path = self.find_file(entity_name)
        
        if not file_path:
            return None
        
        # 读取文件
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
        
        # 解析 Front Matter
        post = frontmatter.loads(content)
        
        # 提取实体数据
        entity = {
            "name": post.get("title", entity_name),
            "type": post.get("type", "unknown"),
            "slug": post.get("slug", ""),
            "compiled_truth": post.get("compiled_truth", {}),
            "timeline": post.get("timeline", []),
            "importance": post.get("importance", 5),
            "tier": post.get("tier", 3),
            "updated_at": post.get("updated_at", ""),
            "created_at": post.get("created_at", ""),
            "content": post.content
        }
        
        return entity
    
    def generate_markdown(self, entity: Dict) -> str:
        """生成 Markdown 内容"""
        # Front Matter
        frontmatter_data = {
            "title": entity.get("title", ""),
            "type": entity.get("type", ""),
            "slug": entity.get("slug", ""),
            "importance": entity.get("importance", 5),
            "tier": entity.get("tier", 3),
            "created_at": entity.get("created_at", ""),
            "updated_at": entity.get("updated_at", ""),
            "version": entity.get("version", "v1.0"),
            "tags": self.generate_tags(entity)
        }
        
        # 生成 Markdown
        post = frontmatter.Post("", **frontmatter_data)
        
        # 添加内容
        content = post.content
        
        # 添加 Compiled Truth
        compiled_truth = entity.get("compiled_truth", {})
        content += "\n\n## Compiled Truth\n\n"
        
        for key, value in compiled_truth.items():
            if value:
                content += f"### {key.replace('_', ' ').title()}\n\n{value}\n\n"
        
        # 添加 Timeline
        timeline = entity.get("timeline", [])
        if timeline:
            content += "## Timeline\n\n"
            for event in timeline:
                content += f"- **{event.get('date', '')}** | {event.get('event', '')}\n"
                if event.get("source"):
                    content += f"  - Source: {event['source']}\n"
                content += "\n"
        
        # 添加反向链接
        content += "## Backlinks\n\n"
        content += f"[[{entity.get('slug', '')}]]\n\n"
        
        # 添加元数据
        content += "---\n\n"
        content += f"**Last Updated**: {entity.get('updated_at', '')}\n"
        content += f"**Version**: {entity.get('version', 'v1.0')}\n"
        content += f"**Tier**: {entity.get('tier', 3)}\n"
        
        post.content = content
        
        return frontmatter.dumps(post)
    
    def get_file_path(self, entity: Dict) -> Path:
        """获取文件路径"""
        entity_type = entity.get("type", "unknown")
        slug = entity.get("slug", entity.get("title", ""))
        
        # 根据类型组织目录
        type_dir = self.vault_path / entity_type
        type_dir.mkdir(exist_ok=True)
        
        # 生成文件名
        filename = f"{slug}.md"
        file_path = type_dir / filename
        
        return file_path
    
    def find_file(self, entity_name: str) -> Optional[Path]:
        """查找文件"""
        # 在所有类型目录中搜索
        for type_dir in self.vault_path.iterdir():
            if type_dir.is_dir():
                for file_path in type_dir.glob("*.md"):
                    if file_path.stem.lower() == entity_name.lower():
                        return file_path
        
        return None
    
    def generate_tags(self, entity: Dict) -> List[str]:
        """生成标签"""
        tags = []
        
        # 基于类型
        entity_type = entity.get("type", "")
        tags.append(f"type/{entity_type}")
        
        # 基于 Tier
        tier = entity.get("tier", 3)
        tags.append(f"tier/{tier}")
        
        # 基于重要性
        importance = entity.get("importance", 5)
        if importance >= 8:
            tags.append("importance/high")
        elif importance >= 5:
            tags.append("importance/medium")
        else:
            tags.append("importance/low")
        
        # 基于时间
        updated_at = entity.get("updated_at", "")
        if updated_at:
            date = datetime.fromisoformat(updated_at)
            tags.append(f"year/{date.year}")
            tags.append(f"month/{date.month}")
        
        return tags
    
    def git_commit(self, message: str):
        """Git 提交"""
        try:
            # 添加所有更改
            self.repo.index.add([str(self.vault_path)])
            
            # 提交
            self.repo.index.commit(message)
            
            # 推送到远程（如果配置了）
            if self.repo.remotes:
                origin = self.repo.remotes.origin
                origin.push()
        except Exception as e:
            print(f"Git commit failed: {e}")
    
    def sync_all_entities(self, entities: List[Dict]):
        """同步所有实体"""
        for entity in entities:
            self.sync_to_obsidian(entity)
    
    def get_all_entities(self) -> List[Dict]:
        """获取所有实体"""
        entities = []
        
        # 遍历所有类型目录
        for type_dir in self.vault_path.iterdir():
            if type_dir.is_dir():
                for file_path in type_dir.glob("*.md"):
                    entity = self.sync_from_obsidian(file_path.stem)
                    if entity:
                        entities.append(entity)
        
        return entities
    
    def delete_entity(self, entity_name: str):
        """删除实体"""
        file_path = self.find_file(entity_name)
        
        if file_path:
            # 删除文件
            file_path.unlink()
            
            # Git 提交
            self.git_commit(f"Deleted: {entity_name}")
    
    def search_entities(self, query: str) -> List[Dict]:
        """搜索实体"""
        results = []
        
        # 在所有文件中搜索
        for type_dir in self.vault_path.iterdir():
            if type_dir.is_dir():
                for file_path in type_dir.glob("*.md"):
                    with open(file_path, "r", encoding="utf-8") as f:
                        content = f.read()
                    
                    if query.lower() in content.lower():
                        entity = self.sync_from_obsidian(file_path.stem)
                        if entity:
                            results.append(entity)
        
        return results
    
    def get_entity_graph(self) -> Dict:
        """获取实体关系图"""
        graph = {
            "nodes": [],
            "edges": []
        }
        
        # 遍历所有实体
        for type_dir in self.vault_path.iterdir():
            if type_dir.is_dir():
                for file_path in type_dir.glob("*.md"):
                    entity = self.sync_from_obsidian(file_path.stem)
                    if entity:
                        # 添加节点
                        graph["nodes"].append({
                            "id": entity.get("slug", ""),
                            "label": entity.get("title", ""),
                            "type": entity.get("type", ""),
                            "tier": entity.get("tier", 3)
                        })
                        
                        # 添加边（从内容中提取链接）
                        content = entity.get("content", "")
                        links = self.extract_links(content)
                        for link in links:
                            graph["edges"].append({
                                "source": entity.get("slug", ""),
                                "target": link,
                                "type": "reference"
                            })
        
        return graph
    
    def extract_links(self, content: str) -> List[str]:
        """提取链接"""
        # 提取 [[wikilinks]]
        import re
        pattern = r'\[\[([^\]]+)\]\]'
        matches = re.findall(pattern, content)
        return matches


# 使用示例
if __name__ == "__main__":
    # 初始化
    obsidian = ObsidianIntegration("C:/Users/Administrator/.openclaw/workspace/brain/obsidian_vault")
    
    # 同步实体
    entity = {
        "title": "John Smith",
        "type": "person",
        "slug": "john-smith",
        "compiled_truth": {
            "executive_summary": "CEO of TechCorp",
            "what_they_believe": "AI will transform everything",
            "what_they_building": "AI-powered analytics platform"
        },
        "timeline": [
            {
                "date": "2026-04-11",
                "event": "Founded TechCorp",
                "source": "news"
            }
        ],
        "importance": 8,
        "tier": 1,
        "created_at": "2026-04-11T00:00:00",
        "updated_at": "2026-04-11T00:00:00",
        "version": "v1.0"
    }
    
    file_path = obsidian.sync_to_obsidian(entity)
    print(f"Synced to: {file_path}")
    
    # 从 Obsidian 读取
    entity_data = obsidian.sync_from_obsidian("john-smith")
    print(f"Read entity: {entity_data['title']}")

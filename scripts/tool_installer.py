#!/usr/bin/env python3
"""
工具安装器 - Tool Installer
将新发现的API包装成OpenClaw可用的工具/技能
"""
import json
import os
import time
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from enum import Enum

class ToolType(Enum):
    API_CLIENT = "api_client"      # REST API调用
    CLI_WRAPPER = "cli_wrapper"    # 命令行封装
    BROWSER_ACTION = "browser_action"  # 浏览器操作
    SKILL = "skill"                # OpenClaw Skill

@dataclass
class InstalledTool:
    name: str
    type: ToolType
    provider: str
    config: Dict  # API keys, endpoints, etc.
    skill_path: str  # 技能文件路径
    status: str  # installed, active, error, needs_config
    installed_at: str
    last_used: Optional[str] = None
    version: str = "1.0.0"
    description: str = ""

class ToolInstaller:
    """工具安装器 - 负责将新API安装为可用工具"""
    
    def __init__(self):
        self.tools_dir = "/Users/xinglong/openclaw-workspace/scripts"
        self.skills_dir = "/Users/xinglong/openclaw-workspace/skills"
        self.installed_tools = self._load_installed_tools()
        # 默认API key存储位置
        self.key_store_path = os.path.expanduser("~/.openclaw/api_keys.json")
        
    def _load_installed_tools(self) -> List[InstalledTool]:
        """加载已安装的工具列表"""
        registry_path = os.path.join(self.tools_dir, "tool_registry.json")
        try:
            if os.path.exists(registry_path):
                with open(registry_path, 'r') as f:
                    data = json.load(f)
                    return [InstalledTool(**t) for t in data]
        except Exception as e:
            print(f"加载工具注册表失败: {e}")
        return []
    
    def _save_installed_tools(self):
        """保存工具注册表"""
        registry_path = os.path.join(self.tools_dir, "tool_registry.json")
        try:
            with open(registry_path, 'w') as f:
                json.dump([asdict(t) for t in self.installed_tools], f, indent=2)
        except Exception as e:
            print(f"保存工具注册表失败: {e}")
    
    # ========== API Key 管理 ==========
    def store_api_key(self, provider: str, api_key: str) -> bool:
        """安全存储API密钥"""
        keys = {}
        if os.path.exists(self.key_store_path):
            try:
                with open(self.key_store_path, 'r') as f:
                    keys = json.load(f)
            except:
                pass
        
        keys[provider] = api_key
        os.makedirs(os.path.dirname(self.key_store_path), exist_ok=True)
        
        # 设置严格权限
        os.chmod(self.key_store_path, 0o600)
        
        try:
            with open(self.key_store_path, 'w') as f:
                json.dump(keys, f)
            os.chmod(self.key_store_path, 0o600)
            return True
        except Exception as e:
            print(f"存储API密钥失败: {e}")
            return False
    
    def get_api_key(self, provider: str) -> Optional[str]:
        """获取已存储的API密钥"""
        if not os.path.exists(self.key_store_path):
            return None
        try:
            with open(self.key_store_path, 'r') as f:
                keys = json.load(f)
                return keys.get(provider)
        except:
            return None
    
    def list_stored_keys(self) -> List[str]:
        """列出已存储的密钥"""
        if not os.path.exists(self.key_store_path):
            return []
        try:
            with open(self.key_store_path, 'r') as f:
                keys = json.load(f)
                return list(keys.keys())
        except:
            return []
    
    # ========== 技能生成 ==========
    def generate_api_client(self, api_config: Dict) -> str:
        """为API生成客户端代码"""
        provider = api_config["provider"]
        base_url = api_config.get("base_url", "")
        models = api_config.get("models", [])
        auth_type = api_config.get("auth_type", "api_key")
        
        template = f'''#!/usr/bin/env python3
"""
{provider.title()} API 客户端
自动生成 - 请勿手动修改
"""
import requests
import json
from typing import Dict, List, Optional, Any

class {provider.title()}Client:
    """{provider.title()} API 客户端"""
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key or self._load_key()
        self.base_url = "{base_url}"
        self.provider = "{provider}"
        
        if not self.api_key:
            raise ValueError("需要 API key 才能使用 {provider} API")
    
    def _load_key(self) -> Optional[str]:
        """从密钥存储加载key"""
        import os, json
        key_path = os.path.expanduser("~/.openclaw/api_keys.json")
        if os.path.exists(key_path):
            with open(key_path) as f:
                keys = json.load(f)
                return keys.get("{provider}")
        return None
    
    def _headers(self) -> Dict[str, str]:
        """生成请求头"""
        headers = {{"Content-Type": "application/json"}}
        if self.api_key:
            if "{auth_type}" == "api_key":
                headers["Authorization"] = f"Bearer {{self.api_key}}"
            else:
                headers["X-API-Key"] = self.api_key
        return headers
    
    def chat(self, prompt: str, model: str = None, **kwargs) -> Dict:
        """聊天请求"""
        if not model and {models}:
            model = "{models[0]}" if {models} else "default"
        
        payload = {{
            "model": model,
            "messages": [{{"role": "user", "content": prompt}}],
            **kwargs
        }}
        
        try:
            resp = requests.post(
                f"{{self.base_url}}/chat/completions",
                headers=self._headers(),
                json=payload,
                timeout=60
            )
            resp.raise_for_status()
            return resp.json()
        except requests.exceptions.RequestException as e:
            return {{"error": str(e), "provider": self.provider}}
    
    def list_models(self) -> List[Dict]:
        """列出可用模型"""
        try:
            resp = requests.get(
                f"{{self.base_url}}/models",
                headers=self._headers(),
                timeout=30
            )
            resp.raise_for_status()
            return resp.json().get("data", [])
        except Exception as e:
            return [{{"error": str(e)}}]
    
    def test_connection(self) -> Dict:
        """测试连接"""
        try:
            models = self.list_models()
            if models and "error" not in models[0]:
                return {{
                    "status": "connected",
                    "provider": self.provider,
                    "models_count": len(models)
                }}
            return {{"status": "error", "message": "无法获取模型列表"}}
        except Exception as e:
            return {{"status": "error", "message": str(e)}}

# 便捷函数
def chat(prompt: str, model: str = None, **kwargs):
    """快捷聊天"""
    client = {provider.title()}Client()
    return client.chat(prompt, model, **kwargs)

if __name__ == "__main__":
    print("测试 {provider} API 客户端...")
    client = {provider.title()}Client()
    result = client.test_connection()
    print(f"连接状态: {{result}}")
'''
        return template
    
    def generate_skill_md(self, api_config: Dict, client_path: str) -> str:
        """生成 SKILL.md 文档"""
        provider = api_config["provider"]
        name = api_config.get("name", provider)
        docs_url = api_config.get("documentation_url", "")
        models = api_config.get("models", [])
        pricing = api_config.get("pricing", {})
        
        skill_md = f'''---
name: {provider}-api
description: {name} - AI模型API集成
version: 1.0.0
tags:
  - ai
  - {provider}
  - api-client
  - auto-installed
---

# {name}

自动安装的 {name} API 客户端技能。

## 配置

API Key 已存储在 `~/.openclaw/api_keys.json`

## 使用方式

```python
from {provider}_client import {provider.title()}Client

client = {provider.title()}Client()

# 聊天
response = client.chat("你好", model="{models[0]}" if {models} else None)

# 列出模型
models = client.list_models()

# 测试连接
result = client.test_connection()
```

## 模型列表

{chr(10).join(f"- {m}" for m in models[:10]) if models else "- (动态获取)"}

## 价格 (per 1K tokens)

{chr(10).join(f"- {k}: ${v}" for k, v in pricing.items()) if pricing else "- 请查看官网"}

## 文档

{docs_url}

---
*自动生成 by Erbing Tool Installer at {time.strftime("%Y-%m-%d %H:%M:%S")}*
'''
        return skill_md
    
    # ========== 安装流程 ==========
    def install_api(self, api_config: Dict) -> Dict:
        """安装API为可用工具"""
        provider = api_config["provider"]
        name = api_config.get("name", provider)
        
        result = {
            "provider": provider,
            "name": name,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "status": "pending",
            "steps": [],
        }
        
        # Step 1: 生成客户端代码
        try:
            client_code = self.generate_api_client(api_config)
            client_filename = f"{provider}_client.py"
            client_path = os.path.join(self.tools_dir, client_filename)
            
            with open(client_path, 'w') as f:
                f.write(client_code)
            
            result["steps"].append({
                "step": "generate_client",
                "status": "ok",
                "path": client_path
            })
        except Exception as e:
            result["steps"].append({
                "step": "generate_client",
                "status": "error",
                "error": str(e)
            })
            result["status"] = "failed"
            return result
        
        # Step 2: 生成技能文档
        try:
            skill_md = self.generate_skill_md(api_config, client_path)
            skill_dir = os.path.join(self.skills_dir, f"{provider}-api")
            os.makedirs(skill_dir, exist_ok=True)
            skill_path = os.path.join(skill_dir, "SKILL.md")
            
            with open(skill_path, 'w') as f:
                f.write(skill_md)
            
            result["steps"].append({
                "step": "generate_skill",
                "status": "ok",
                "path": skill_path
            })
        except Exception as e:
            result["steps"].append({
                "step": "generate_skill",
                "status": "error",
                "error": str(e)
            })
            # 继续，可能只是文档缺失
        
        # Step 3: 注册到工具清单
        try:
            tool = InstalledTool(
                name=name,
                type=ToolType.API_CLIENT,
                provider=provider,
                config=api_config,
                skill_path=client_path,
                status="installed" if self.get_api_key(provider) else "needs_config",
                installed_at=time.strftime("%Y-%m-%d %H:%M:%S"),
                description=api_config.get("documentation_url", ""),
            )
            self.installed_tools.append(tool)
            self._save_installed_tools()
            
            result["steps"].append({
                "step": "register_tool",
                "status": "ok"
            })
        except Exception as e:
            result["steps"].append({
                "step": "register_tool",
                "status": "error",
                "error": str(e)
            })
        
        result["status"] = "completed"
        return result
    
    # ========== 工具管理 ==========
    def list_installed(self) -> List[Dict]:
        """列出已安装的工具"""
        return [
            {
                "name": t.name,
                "provider": t.provider,
                "type": t.type.value,
                "status": t.status,
                "installed_at": t.installed_at,
                "last_used": t.last_used,
                "version": t.version,
            }
            for t in self.installed_tools
        ]
    
    def get_tool(self, provider: str) -> Optional[InstalledTool]:
        """获取特定工具"""
        for tool in self.installed_tools:
            if tool.provider == provider:
                return tool
        return None
    
    def update_tool_status(self, provider: str, status: str):
        """更新工具状态"""
        for tool in self.installed_tools:
            if tool.provider == provider:
                tool.status = status
                tool.last_used = time.strftime("%Y-%m-%d %H:%M:%S")
        self._save_installed_tools()
    
    def uninstall_tool(self, provider: str) -> bool:
        """卸载工具"""
        tool = self.get_tool(provider)
        if not tool:
            return False
        
        # 删除文件
        try:
            if os.path.exists(tool.skill_path):
                os.remove(tool.skill_path)
            
            skill_dir = os.path.join(self.skills_dir, f"{provider}-api")
            if os.path.exists(skill_dir):
                import shutil
                shutil.rmtree(skill_dir)
        except Exception as e:
            print(f"删除文件失败: {e}")
        
        # 从注册表移除
        self.installed_tools = [t for t in self.installed_tools if t.provider != provider]
        self._save_installed_tools()
        return True
    
    # ========== 批量安装 ==========
    def auto_install_known_apis(self) -> Dict:
        """自动安装所有已知API（生成安装计划）"""
        from api_scout import get_api_scout
        
        scout = get_api_scout()
        results = {}
        
        for api in scout.known_apis:
            # 已经有key的才安装
            if self.get_api_key(api.provider):
                result = self.install_api({
                    "provider": api.provider,
                    "name": api.name,
                    "base_url": api.base_url,
                    "models": api.models,
                    "documentation_url": api.documentation_url,
                })
                results[api.provider] = result
        
        return {
            "total": len(scout.known_apis),
            "installed": len(results),
            "results": results
        }


# 全局实例
_tool_installer = None

def get_tool_installer() -> ToolInstaller:
    global _tool_installer
    if _tool_installer is None:
        _tool_installer = ToolInstaller()
    return _tool_installer


# 演示
if __name__ == "__main__":
    installer = get_tool_installer()
    
    print("="*60)
    print("工具安装器演示")
    print("="*60)
    
    print(f"\n已存储的 API Keys: {installer.list_stored_keys()}")
    
    print("\n已安装的工具:")
    for tool in installer.list_installed():
        status_emoji = "✅" if tool["status"] == "active" else "⚠️" if tool["status"] == "needs_config" else "❌"
        print(f"  {status_emoji} {tool['name']} ({tool['provider']}) - {tool['status']}")
    
    print("\n安装 NVIDIA API 工具 (示例):")
    result = installer.install_api({
        "provider": "nvidia",
        "name": "NVIDIA NIM API",
        "base_url": "https://integrate.api.nvidia.com/v1",
        "models": ["nemotron-3-super", "llama-3"],
        "documentation_url": "https://docs.nvidia.com/nim/",
    })
    print(f"  状态: {result['status']}")
    for step in result.get("steps", []):
        status = "✅" if step["status"] == "ok" else "❌"
        print(f"  {status} {step['step']}: {step.get('path', step.get('error', 'ok'))}")
#!/usr/bin/env python3
"""
注册工厂 - Registration Factory
自动注册开发者账号（NVIDIA/Gemini等）
"""
import json
import time
import random
import string
from typing import Dict, List, Optional, Any
from enum import Enum

class SiteType(Enum):
    AI_API = "ai_api"           # NVIDIA, OpenAI, etc.
    SOCIAL = "social"           # Twitter, GitHub, etc.
    CLOUD = "cloud"             # AWS, GCP, Azure
    DEV_TOOLS = "dev_tools"     # GitHub, GitLab, etc.

class RegistrationFactory:
    """注册工厂 - 自动注册各种平台账号"""
    
    def __init__(self):
        # 站点注册配置
        self.sites = self._load_site_configs()
        # 已完成的注册记录
        self.completed_registrations = {}
        
    def _load_site_configs(self) -> Dict[str, Dict]:
        """加载支持的站点注册配置"""
        return {
            "nvidia": {
                "name": "NVIDIA Developer",
                "type": SiteType.AI_API,
                "url": "https://developer.nvidia.com/",
                "signup_url": "https://build.nvidia.com/",
                "steps": [
                    {"action": "open", "url": "https://build.nvidia.com/"},
                    {"action": "snapshot", "desc": "检查是否已有登录状态"},
                    {"action": "click", "selector": "text=Sign In", "desc": "点击登录"},
                    {"action": "snapshot", "desc": "查看登录选项"},
                    {"action": "click", "selector": "text=Create Account, text=Sign Up", "desc": "点击注册"},
                    {"action": "wait_for", "selector": "input[type=email]", "desc": "等待邮箱输入框"},
                    {"action": "fill", "selector": "input[type=email]", "value": "{email}", "desc": "填写邮箱"},
                    {"action": "fill", "selector": "input[type=password]", "value": "{password}", "desc": "填写密码"},
                    {"action": "fill", "selector": "input[name*='name'], input[placeholder*='name']", "value": "{name}", "desc": "填写姓名"},
                    {"action": "click", "selector": "button[type=submit]", "desc": "提交注册"},
                    {"action": "wait_for", "selector": "text=Verify, text=Confirm", "desc": "等待验证"},
                ],
                "fields": {
                    "email": {"type": "email", "required": True, "generate": "temp_email"},
                    "password": {"type": "password", "required": True, "min_length": 8},
                    "name": {"type": "text", "required": True, "generate": "fake_name"},
                },
                "verification": "email",  # 需要邮箱验证
                "notes": "NVIDIA注册后需要等待几分钟API才能生效"
            },
            "google_gemini": {
                "name": "Google Gemini (MakerSuite)",
                "type": SiteType.AI_API,
                "url": "https://makersuite.google.com/",
                "signup_url": "https://makersuite.google.com/",
                "steps": [
                    {"action": "open", "url": "https://makersuite.google.com/"},
                    {"action": "snapshot", "desc": "检查登录状态"},
                    {"action": "click", "selector": "text=Sign In, button:has-text('Get Started')", "desc": "点击开始"},
                    {"action": "wait_for", "selector": "input[type=email], input[type=text]", "desc": "等待输入框"},
                    {"action": "fill", "selector": "input[type=email]", "value": "{email}", "desc": "填写邮箱"},
                    {"action": "click", "selector": "button[type=submit]", "desc": "下一步"},
                    {"action": "fill", "selector": "input[type=password]", "value": "{password}", "desc": "填写密码"},
                    {"action": "click", "selector": "button[type=submit]", "desc": "确认"},
                ],
                "fields": {
                    "email": {"type": "email", "required": True, "generate": "temp_email"},
                    "password": {"type": "password", "required": True, "min_length": 8},
                },
                "verification": "email",
                "notes": "使用Google账号直接登录即可"
            },
            "groq": {
                "name": "Groq API",
                "type": SiteType.AI_API,
                "url": "https://console.groq.com/",
                "signup_url": "https://console.groq.com/",
                "steps": [
                    {"action": "open", "url": "https://console.groq.com/"},
                    {"action": "snapshot", "desc": "检查登录状态"},
                    {"action": "click", "selector": "text=Sign In, text=Log In", "desc": "点击登录"},
                    {"action": "click", "selector": "text=Create Account, text=Sign Up", "desc": "点击注册"},
                    {"action": "wait_for", "selector": "input[type=email]", "desc": "等待邮箱输入框"},
                    {"action": "fill", "selector": "input[type=email]", "value": "{email}", "desc": "填写邮箱"},
                    {"action": "fill", "selector": "input[type=password]", "value": "{password}", "desc": "填写密码"},
                    {"action": "fill", "selector": "input[name*='name']", "value": "{name}", "desc": "填写姓名"},
                    {"action": "click", "button[type=submit]", "desc": "提交注册"},
                ],
                "fields": {
                    "email": {"type": "email", "required": True, "generate": "temp_email"},
                    "password": {"type": "password", "required": True, "min_length": 8},
                    "name": {"type": "text", "required": True, "generate": "fake_name"},
                },
                "verification": "email",
                "notes": "Groq有免费额度，注册相对简单"
            },
            "together_ai": {
                "name": "Together AI",
                "type": SiteType.AI_API,
                "url": "https://api.together.xyz/",
                "signup_url": "https://api.together.xyz/signup",
                "steps": [
                    {"action": "open", "url": "https://api.together.xyz/signup"},
                    {"action": "wait_for", "selector": "input[type=email]", "desc": "等待邮箱输入框"},
                    {"action": "fill", "selector": "input[type=email]", "value": "{email}"},
                    {"action": "fill", "selector": "input[type=password]", "value": "{password}"},
                    {"action": "click", "button[type=submit]", "desc": "提交"},
                ],
                "fields": {
                    "email": {"type": "email", "required": True, "generate": "temp_email"},
                    "password": {"type": "password", "required": True, "min_length": 8},
                },
                "verification": "email",
                "notes": "Together AI支持GitHub登录"
            },
            "github": {
                "name": "GitHub",
                "type": SiteType.DEV_TOOLS,
                "url": "https://github.com/",
                "signup_url": "https://github.com/signup",
                "steps": [
                    {"action": "open", "url": "https://github.com/signup"},
                    {"action": "wait_for", "selector": "input#email"},
                    {"action": "fill", "selector": "input#email", "value": "{email}"},
                    {"action": "fill", "selector": "input#password", "value": "{password}"},
                    {"action": "fill", "selector": "input#login", "value": "{username}"},
                    {"action": "click", "button[type=submit]"],
                ],
                "fields": {
                    "email": {"type": "email", "required": True, "generate": "temp_email"},
                    "password": {"type": "password", "required": True, "min_length": 8},
                    "username": {"type": "text", "required": True, "generate": "fake_username"},
                },
                "verification": "email",
                "notes": "GitHub用户名必须唯一且未被使用"
            },
        }
    
    # ========== 数据生成器 ==========
    def generate_email(self, prefix: str = "erbing") -> str:
        """生成随机邮箱"""
        # 实际应该使用临时邮箱服务API获取真实收件箱
        # 这里用随机字符串模拟
        random_suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
        domains = ["gmail.com", "outlook.com", "proton.me", "temp-mail.org"]
        domain = random.choice(domains)
        return f"{prefix}_{random_suffix}@{domain}"
    
    def generate_password(self, length: int = 16) -> str:
        """生成安全密码"""
        chars = string.ascii_letters + string.digits + "!@#$%^&*"
        return ''.join(random.choices(chars, k=length))
    
    def generate_fake_name(self) -> str:
        """生成假名"""
        first_names = ["Alex", "Jordan", "Taylor", "Morgan", "Casey", "Riley", "Quinn", "Avery"]
        last_names = ["Smith", "Johnson", "Brown", "Lee", "Chen", "Wang", "Garcia", "Miller"]
        return f"{random.choice(first_names)} {random.choice(last_names)}"
    
    def generate_username(self) -> str:
        """生成GitHub风格用户名"""
        adjectives = ["swift", "brave", "clever", "bright", "quick", "cool"]
        nouns = ["dev", "code", "byte", "node", "pixel", "cloud"]
        num = random.randint(100, 999)
        return f"{random.choice(adjectives)}_{random.choice(nouns)}_{num}"
    
    def generate_field_value(self, field_type: str) -> str:
        """根据字段类型生成值"""
        generators = {
            "email": self.generate_email,
            "password": self.generate_password,
            "fake_name": self.generate_fake_name,
            "fake_username": self.generate_username,
            "text": self.generate_fake_name,
        }
        gen = generators.get(field_type, lambda: "generated_value")
        return gen()
    
    # ========== 注册流程 ==========
    def get_registration_steps(self, site: str) -> Dict:
        """获取注册步骤"""
        if site not in self.sites:
            return {"error": f"Unknown site: {site}"}
        
        config = self.sites[site]
        return {
            "site": site,
            "name": config["name"],
            "type": config["type"].value,
            "url": config["url"],
            "signup_url": config["signup_url"],
            "steps": config["steps"],
            "fields": config["fields"],
            "verification": config.get("verification", "email"),
            "notes": config.get("notes", ""),
        }
    
    def prepare_registration_data(self, site: str) -> Dict[str, str]:
        """准备注册数据（填充占位符）"""
        config = self.sites[site]
        filled_data = {}
        
        for selector, field_config in config["fields"].items():
            field_type = field_config.get("generate", "text")
            filled_data[selector] = self.generate_field_value(field_type)
        
        return filled_data
    
    def execute_registration(self, site: str, dry_run: bool = True) -> Dict:
        """执行注册流程"""
        if site not in self.sites:
            return {"error": f"Unknown site: {site}"}
        
        config = self.sites[site]
        
        # 准备数据
        reg_data = self.prepare_registration_data(site)
        
        if dry_run:
            # 返回计划而不实际执行
            return {
                "site": site,
                "status": "planned",
                "registration_data": reg_data,
                "steps": len(config["steps"]),
                "verification_needed": config.get("verification"),
                "message": f"注册 {config['name']} 的步骤已计划好，待执行",
                "note": "设置 dry_run=False 实际执行注册（需要人工介入处理验证码等）"
            }
        
        # 实际执行（需要浏览器自动化）
        # 步骤将传递给 web_agent 执行
        return {
            "site": site,
            "status": "executing",
            "registration_data": reg_data,
            "execution_plan": [
                step.update({"data": reg_data}) if "{email}" in str(step) else step
                for step in config["steps"]
            ],
            "message": "注册执行中..."
        }
    
    # ========== 批量注册 ==========
    def register_all_ai_sites(self, dry_run: bool = True) -> Dict:
        """批量注册所有AI平台"""
        ai_sites = [k for k, v in self.sites.items() 
                   if v["type"] == SiteType.AI_API]
        
        results = {}
        for site in ai_sites:
            results[site] = self.execute_registration(site, dry_run=dry_run)
            # 避免请求过快
            time.sleep(random.uniform(0.5, 1.5))
        
        return {
            "total": len(ai_sites),
            "results": results,
            "dry_run": dry_run,
            "timestamp": time.time()
        }
    
    # ========== 状态查询 ==========
    def get_supported_sites(self) -> List[Dict]:
        """获取所有支持的站点"""
        return [
            {
                "id": site_id,
                "name": config["name"],
                "type": config["type"].value,
                "signup_url": config["signup_url"],
            }
            for site_id, config in self.sites.items()
        ]
    
    def get_registration_status(self, site: str) -> Dict:
        """获取注册状态"""
        if site in self.completed_registrations:
            return {
                "site": site,
                "status": "completed",
                "details": self.completed_registrations[site]
            }
        else:
            return {
                "site": site,
                "status": "not_started",
                "available": site in self.sites,
                "config": self.sites.get(site, {}).get("name", "Unknown")
            }


# 全局实例
_registration_factory = None

def get_registration_factory() -> RegistrationFactory:
    global _registration_factory
    if _registration_factory is None:
        _registration_factory = RegistrationFactory()
    return _registration_factory


# 演示
if __name__ == "__main__":
    factory = get_registration_factory()
    
    print("="*60)
    print("注册工厂演示")
    print("="*60)
    
    print("\n支持的站点:")
    for site in factory.get_supported_sites():
        print(f"  - {site['name']} ({site['type']})")
    
    print("\n注册 NVIDIA (dry-run):")
    result = factory.execute_registration("nvidia", dry_run=True)
    print(f"  状态: {result['status']}")
    print(f"  数据: {result.get('registration_data', {})}")
    
    print("\n批量AI平台注册 (dry-run):")
    batch = factory.register_all_ai_sites(dry_run=True)
    print(f"  总数: {batch['total']}")
    for site, res in batch["results"].items():
        print(f"  - {site}: {res['status']}")
"""
MetaGPT Roles - 角色定义模块

这个模块定义了软件开发过程中的各种角色。
"""

from .product_manager import ProductManager
from .architect import Architect
from .engineer import Engineer
from .qa_engineer import QaEngineer
from .project_manager import ProjectManager

__all__ = [
    "ProductManager",
    "Architect", 
    "Engineer",
    "QaEngineer",
    "ProjectManager",
]

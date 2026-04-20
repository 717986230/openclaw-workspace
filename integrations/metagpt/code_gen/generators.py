"""
代码生成器

核心代码生成功能实现。
"""

from typing import Any, Dict, List, Optional
from dataclasses import dataclass
import json


@dataclass
class GenerationConfig:
    """代码生成配置"""
    language: str = "python"
    style: str = "google"  # google, pep8, etc.
    max_line_length: int = 100
    use_type_hints: bool = True
    generate_docs: bool = True
    generate_tests: bool = True


class CodeGenerator:
    """
    代码生成器
    
    支持根据设计文档生成代码。
    """
    
    def __init__(self, config: Optional[GenerationConfig] = None):
        """
        初始化代码生成器
        
        Args:
            config: 生成配置
        """
        self.config = config or GenerationConfig()
        self.templates: Dict[str, str] = {}
        self._load_templates()
    
    def _load_templates(self) -> None:
        """加载代码模板"""
        self.templates = {
            "python_class": self._python_class_template(),
            "python_function": self._python_function_template(),
            "python_module": self._python_module_template(),
            "api_endpoint": self._api_endpoint_template(),
            "test_case": self._test_case_template()
        }
    
    async def generate(
        self,
        design: Dict[str, Any],
        output_format: str = "files"
    ) -> Dict[str, str]:
        """
        生成代码
        
        Args:
            design: 设计文档
            output_format: 输出格式 (files, single_file)
            
        Returns:
            生成的代码字典
        """
        generated_code = {}
        
        # 根据设计生成模块
        modules = design.get("modules", [])
        
        for module in modules:
            module_name = module.get("name", "unnamed")
            module_code = await self._generate_module(module)
            generated_code[f"{module_name}.py"] = module_code
        
        # 生成主入口文件
        if output_format == "files":
            generated_code["main.py"] = await self._generate_main(modules)
        
        return generated_code
    
    async def generate_from_template(
        self,
        template_name: str,
        params: Dict[str, Any]
    ) -> str:
        """
        从模板生成代码
        
        Args:
            template_name: 模板名称
            params: 模板参数
            
        Returns:
            生成的代码
        """
        template = self.templates.get(template_name)
        if not template:
            raise ValueError(f"Template {template_name} not found")
        
        # 替换参数
        code = template
        for key, value in params.items():
            code = code.replace(f"{{{key}}}", str(value))
        
        return code
    
    async def generate_class(
        self,
        class_name: str,
        attributes: List[Dict[str, str]],
        methods: List[Dict[str, Any]]
    ) -> str:
        """
        生成类代码
        
        Args:
            class_name: 类名
            attributes: 属性列表
            methods: 方法列表
            
        Returns:
            类代码
        """
        # 属性定义
        attrs_code = "\n    ".join(
            f"{attr['name']}: {attr.get('type', 'Any')}"
            for attr in attributes
        )
        
        # 方法定义
        methods_code = []
        for method in methods:
            methods_code.append(
                await self._generate_method(method)
            )
        
        methods_str = "\n\n    ".join(methods_code)
        
        code = f'''
class {class_name}:
    """{class_name} class."""
    
    {attrs_code}
    
    {methods_str}
'''
        return code
    
    async def generate_function(
        self,
        func_name: str,
        params: List[Dict[str, str]],
        return_type: str = "None",
        body: str = "pass"
    ) -> str:
        """
        生成函数代码
        
        Args:
            func_name: 函数名
            params: 参数列表
            return_type: 返回类型
            body: 函数体
            
        Returns:
            函数代码
        """
        # 参数定义
        params_str = ", ".join(
            f"{p['name']}: {p.get('type', 'Any')}"
            for p in params
        )
        
        code = f'''
def {func_name}({params_str}) -> {return_type}:
    """TODO: Add docstring."""
    {body}
'''
        return code
    
    async def generate_api_endpoint(
        self,
        endpoint: Dict[str, Any]
    ) -> str:
        """
        生成 API 端点代码
        
        Args:
            endpoint: 端点定义
            
        Returns:
            API 端点代码
        """
        path = endpoint.get("path", "/")
        method = endpoint.get("method", "GET").lower()
        handler = endpoint.get("handler", "handler")
        
        code = f'''
@app.{method}("{path}")
async def {handler}(request):
    """Handle {method.upper()} {path}."""
    # TODO: Implement handler logic
    return {{"status": "ok"}}
'''
        return code
    
    async def generate_test(
        self,
        target: str,
        test_type: str = "unit"
    ) -> str:
        """
        生成测试代码
        
        Args:
            target: 测试目标
            test_type: 测试类型
            
        Returns:
            测试代码
        """
        code = f'''
import pytest
from {target} import *


class Test{target.capitalize()}:
    """Test cases for {target}."""
    
    def test_basic(self):
        """Test basic functionality."""
        # TODO: Add test implementation
        assert True
    
    def test_edge_cases(self):
        """Test edge cases."""
        # TODO: Add edge case tests
        assert True
'''
        return code
    
    async def _generate_module(self, module: Dict[str, Any]) -> str:
        """
        生成模块代码
        
        Args:
            module: 模块定义
            
        Returns:
            模块代码
        """
        module_name = module.get("name", "module")
        classes = module.get("classes", [])
        functions = module.get("functions", [])
        
        code_parts = [
            f'"""{module_name} module."""',
            "",
            "from typing import Any, Dict, List",
            ""
        ]
        
        # 生成类
        for cls in classes:
            class_code = await self.generate_class(
                cls.get("name", "UnknownClass"),
                cls.get("attributes", []),
                cls.get("methods", [])
            )
            code_parts.append(class_code)
        
        # 生成函数
        for func in functions:
            func_code = await self.generate_function(
                func.get("name", "unknown_function"),
                func.get("params", []),
                func.get("return_type", "None"),
                func.get("body", "pass")
            )
            code_parts.append(func_code)
        
        return "\n".join(code_parts)
    
    async def _generate_main(self, modules: List[Dict[str, Any]]) -> str:
        """
        生成主入口文件
        
        Args:
            modules: 模块列表
            
        Returns:
            主文件代码
        """
        imports = "\n".join(
            f"from {m.get('name', 'module')} import *"
            for m in modules
        )
        
        code = f'''
"""Main entry point."""

{imports}


def main():
    """Main function."""
    print("Application started")
    # TODO: Add main logic


if __name__ == "__main__":
    main()
'''
        return code
    
    async def _generate_method(self, method: Dict[str, Any]) -> str:
        """
        生成方法代码
        
        Args:
            method: 方法定义
            
        Returns:
            方法代码
        """
        name = method.get("name", "unknown")
        params = method.get("params", [])
        return_type = method.get("return_type", "None")
        body = method.get("body", "pass")
        
        # 参数（包含 self）
        params_str = "self, " + ", ".join(
            f"{p['name']}: {p.get('type', 'Any')}"
            for p in params
        )
        
        code = f'''
def {name}({params_str}) -> {return_type}:
    """{name} method."""
    {body}
'''
        return code
    
    def _python_class_template(self) -> str:
        """Python 类模板"""
        return '''
class {class_name}:
    """{description}."""
    
    def __init__(self{init_params}):
        """Initialize {class_name}."""
        {init_body}
    
    {methods}
'''
    
    def _python_function_template(self) -> str:
        """Python 函数模板"""
        return '''
def {func_name}({params}) -> {return_type}:
    """{description}."""
    {body}
'''
    
    def _python_module_template(self) -> str:
        """Python 模块模板"""
        return '''
"""{module_name} module."""

from typing import Any, Dict, List


{content}
'''
    
    def _api_endpoint_template(self) -> str:
        """API 端点模板"""
        return '''
@app.{method}("{path}")
async def {handler}(request):
    """{description}."""
    {body}
'''
    
    def _test_case_template(self) -> str:
        """测试用例模板"""
        return '''
def test_{test_name}():
    """Test {description}."""
    # Arrange
    {arrange}
    
    # Act
    {act}
    
    # Assert
    {assert}
'''

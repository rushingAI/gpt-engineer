"""
模板管理器 - 负责加载和管理项目模板
"""

import json
import os
from pathlib import Path
from typing import Dict, Optional, List


class TemplateManager:
    """管理项目模板的加载和操作"""
    
    def __init__(self, templates_dir: str = None):
        """
        初始化模板管理器
        
        Args:
            templates_dir: 模板目录路径，默认为当前目录下的 templates
        """
        if templates_dir is None:
            templates_dir = Path(__file__).parent / "templates"
        
        self.templates_dir = Path(templates_dir)
        self.templates_cache: Dict[str, Dict] = {}
    
    def list_templates(self) -> List[Dict]:
        """
        列出所有可用的模板
        
        Returns:
            模板信息列表
        """
        templates = []
        
        if not self.templates_dir.exists():
            return templates
        
        for template_dir in self.templates_dir.iterdir():
            if template_dir.is_dir():
                template_json = template_dir / "template.json"
                if template_json.exists():
                    with open(template_json, 'r', encoding='utf-8') as f:
                        template_info = json.load(f)
                        template_info['id'] = template_dir.name
                        templates.append(template_info)
        
        return templates
    
    def get_template(self, template_name: str) -> Optional[Dict]:
        """
        获取指定的模板
        
        Args:
            template_name: 模板名称
            
        Returns:
            模板信息字典，包含 metadata 和 files
        """
        # 检查缓存
        if template_name in self.templates_cache:
            return self.templates_cache[template_name]
        
        template_dir = self.templates_dir / template_name
        if not template_dir.exists():
            return None
        
        # 加载模板元数据
        template_json = template_dir / "template.json"
        if not template_json.exists():
            return None
        
        with open(template_json, 'r', encoding='utf-8') as f:
            metadata = json.load(f)
        
        # 加载模板文件
        files_dir = template_dir / "files"
        template_files = {}
        
        if files_dir.exists():
            template_files = self._load_directory(files_dir)
        
        template = {
            'metadata': metadata,
            'files': template_files
        }
        
        # 缓存
        self.templates_cache[template_name] = template
        
        return template
    
    def _load_directory(self, directory: Path, base_path: Path = None) -> Dict[str, str]:
        """
        递归加载目录中的所有文件
        
        Args:
            directory: 要加载的目录
            base_path: 基础路径（用于计算相对路径）
            
        Returns:
            文件路径到文件内容的字典
        """
        if base_path is None:
            base_path = directory
        
        files = {}
        
        for item in directory.iterdir():
            if item.is_file():
                # 计算相对路径
                relative_path = str(item.relative_to(base_path))
                
                # 读取文件内容
                try:
                    with open(item, 'r', encoding='utf-8') as f:
                        files[relative_path] = f.read()
                except Exception as e:
                    print(f"警告: 无法读取文件 {item}: {e}")
            
            elif item.is_dir():
                # 递归加载子目录
                subdir_files = self._load_directory(item, base_path)
                files.update(subdir_files)
        
        return files
    
    def merge_files(self, template_files: Dict[str, str], generated_files: Dict[str, str]) -> Dict[str, str]:
        """
        合并模板文件和 AI 生成的文件
        
        策略:
        1. 保留模板的配置文件（package.json, vite.config.ts 等）
        2. 替换 src/ 目录下的页面和组件
        3. 保留 src/components/ui/ 和 src/lib/ 等基础设施
        
        Args:
            template_files: 模板文件字典
            generated_files: AI 生成的文件字典
            
        Returns:
            合并后的文件字典
        """
        result = dict(template_files)  # 复制模板文件
        
        # 需要保留的模板文件路径模式
        preserve_patterns = [
            'package.json',
            'vite.config',
            'tsconfig',
            'tailwind.config',
            'postcss.config',
            'index.html',
            'src/main.tsx',
            'src/App.tsx',
            'src/index.css',
            'src/components/ui/',
            'src/lib/',
        ]
        
        # 处理 AI 生成的文件
        for file_path, content in generated_files.items():
            # 检查是否应该保留模板文件
            should_preserve = any(
                pattern in file_path for pattern in preserve_patterns
            )
            
            if should_preserve:
                # 特殊处理：对于 src/App.tsx，可能需要合并路由
                if 'App.tsx' in file_path:
                    # 这里可以添加更智能的合并逻辑
                    # 暂时简单替换
                    pass
                else:
                    # 保留模板文件，不覆盖
                    continue
            
            # 添加或替换文件
            result[file_path] = content
        
        return result
    
    def detect_template_type(self, prompt: str) -> str:
        """
        根据用户提示词自动检测应该使用的模板类型
        
        Args:
            prompt: 用户输入的提示词
            
        Returns:
            模板名称
        """
        prompt_lower = prompt.lower()
        
        # Landing page 关键词
        landing_keywords = ['landing', 'homepage', 'marketing', '首页', '落地页', '着陆页']
        if any(keyword in prompt_lower for keyword in landing_keywords):
            return 'react-ts-shadcn'  # 使用 React 模板
        
        # Dashboard 关键词
        dashboard_keywords = ['dashboard', 'admin', 'panel', 'saas', '仪表盘', '管理后台']
        if any(keyword in prompt_lower for keyword in dashboard_keywords):
            return 'react-ts-shadcn'
        
        # 默认使用 React 模板
        return 'react-ts-shadcn'


# 全局模板管理器实例
template_manager = TemplateManager()

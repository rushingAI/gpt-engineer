"""
自定义 Preprompt 管理器 - 加载和组合自定义的系统提示词
"""

from pathlib import Path
from typing import Dict, Optional


class CustomPrepromptsManager:
    """管理自定义 Preprompts 的加载和组合"""
    
    def __init__(self, preprompts_dir: str = None):
        """
        初始化 Preprompt 管理器
        
        Args:
            preprompts_dir: 自定义 preprompts 目录路径
        """
        if preprompts_dir is None:
            preprompts_dir = Path(__file__).parent / "preprompts_custom"
        
        self.preprompts_dir = Path(preprompts_dir)
        self.preprompts_cache: Dict[str, str] = {}
    
    def clear_cache(self):
        """清除所有缓存的 preprompts"""
        self.preprompts_cache.clear()
        print("✅ Preprompt 缓存已清除")
    
    def load_preprompt(self, name: str, use_cache: bool = True) -> Optional[str]:
        """
        加载指定的 preprompt
        
        Args:
            name: preprompt 名称（不含扩展名）
            use_cache: 是否使用缓存（默认 True，设为 False 强制重新加载）
            
        Returns:
            preprompt 内容
        """
        # 检查缓存
        if use_cache and name in self.preprompts_cache:
            return self.preprompts_cache[name]
        
        preprompt_file = self.preprompts_dir / name
        
        if not preprompt_file.exists():
            print(f"警告: Preprompt 文件不存在: {preprompt_file}")
            return None
        
        try:
            with open(preprompt_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 缓存
            self.preprompts_cache[name] = content
            
            return content
        except Exception as e:
            print(f"错误: 无法加载 preprompt {name}: {e}")
            return None
    
    def build_system_prompt(self, app_type: str = "modern_web_app", style: str = "cyberpunk", use_cache: bool = False) -> str:
        """
        构建完整的系统提示词
        
        根据风格和应用类型组合相应的 preprompts
        
        Args:
            app_type: 应用类型 (modern_web_app, landing_page, dashboard)
            style: 视觉风格 (cyberpunk, aurora, glass, neo_brutal, minimal, retro_futurism)
            
        Returns:
            完整的系统提示词
        """
        # 1. 加载风格 preprompt（主要的设计系统指南）
        style_preprompt_name = f"style_{style}"
        style_preprompt = self.load_preprompt(style_preprompt_name, use_cache=use_cache)
            
        # 回退机制：如果风格 preprompt 不存在，尝试旧版名称
        if style_preprompt is None and style == "cyberpunk":
            print(f"警告: {style_preprompt_name} 不存在，尝试使用 cyberpunk_react")
            style_preprompt = self.load_preprompt("cyberpunk_react", use_cache=use_cache)
        
        if style_preprompt is None:
            print(f"警告: 风格 preprompt {style_preprompt_name} 不存在，回退到 modern_web_app")
            style_preprompt = self.load_preprompt("modern_web_app", use_cache=use_cache)
        
        if style_preprompt is None:
            return ""
        
        system_prompt = style_preprompt
        
        # 2. 可选：追加应用类型特定的指导（不包含风格约束）
        if app_type == "landing_page":
            landing_preprompt = self.load_preprompt("landing_page", use_cache=use_cache)
            if landing_preprompt:
                system_prompt += "\n\n" + "="*80 + "\n"
                system_prompt += "LANDING PAGE SPECIFIC GUIDELINES:\n"
                system_prompt += "="*80 + "\n\n"
                system_prompt += landing_preprompt
        
        elif app_type == "dashboard":
            dashboard_preprompt = self.load_preprompt("dashboard", use_cache=use_cache)
            if dashboard_preprompt:
                system_prompt += "\n\n" + "="*80 + "\n"
                system_prompt += "DASHBOARD SPECIFIC GUIDELINES:\n"
                system_prompt += "="*80 + "\n\n"
                system_prompt += dashboard_preprompt
        
        return system_prompt
    
    def detect_app_type(self, prompt: str) -> str:
        """
        根据用户提示词检测应用类型
        
        Args:
            prompt: 用户提示词
            
        Returns:
            应用类型
        """
        prompt_lower = prompt.lower()
        
        # Landing page 关键词
        landing_keywords = [
            'landing', 'homepage', 'marketing', 'website',
            '首页', '落地页', '着陆页', '营销页', '官网'
        ]
        if any(keyword in prompt_lower for keyword in landing_keywords):
            return 'landing_page'
        
        # Dashboard 关键词
        dashboard_keywords = [
            'dashboard', 'admin', 'panel', 'saas', 'backend',
            '仪表盘', '管理后台', '后台', '控制台', '管理系统'
        ]
        if any(keyword in prompt_lower for keyword in dashboard_keywords):
            return 'dashboard'
        
        # 默认返回通用 Web 应用
        return 'modern_web_app'


# 全局实例
custom_preprompts_manager = CustomPrepromptsManager()

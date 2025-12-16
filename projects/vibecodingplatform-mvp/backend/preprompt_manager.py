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
    
    def load_preprompt(self, name: str) -> Optional[str]:
        """
        加载指定的 preprompt
        
        Args:
            name: preprompt 名称（不含扩展名）
            
        Returns:
            preprompt 内容
        """
        # 检查缓存
        if name in self.preprompts_cache:
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
    
    def build_system_prompt(self, app_type: str = "cyberpunk_react", use_cyberpunk: bool = True) -> str:
        """
        构建完整的系统提示词
        
        根据应用类型组合相应的 preprompts
        
        Args:
            app_type: 应用类型 (cyberpunk_react, modern_web_app, landing_page, dashboard)
            use_cyberpunk: 是否使用 Cyberpunk 设计系统（默认 True）
            
        Returns:
            完整的系统提示词
        """
        # 默认使用 Cyberpunk React 预设
        if use_cyberpunk:
            base_preprompt = self.load_preprompt("cyberpunk_react")
            
            if base_preprompt is None:
                print("警告: cyberpunk_react preprompt 不存在，回退到 modern_web_app")
                base_preprompt = self.load_preprompt("modern_web_app")
        else:
            # 兼容旧版：使用 modern_web_app
            base_preprompt = self.load_preprompt("modern_web_app")
        
        if base_preprompt is None:
            return ""
        
        system_prompt = base_preprompt
        
        # 可选：根据应用类型添加特定指导（但 Cyberpunk 已经很完整了）
        # 这里保留以便未来扩展
        if not use_cyberpunk:
            if app_type == "landing_page":
                landing_preprompt = self.load_preprompt("landing_page")
                if landing_preprompt:
                    system_prompt += "\n\n" + "="*80 + "\n"
                    system_prompt += "LANDING PAGE SPECIFIC GUIDELINES:\n"
                    system_prompt += "="*80 + "\n\n"
                    system_prompt += landing_preprompt
            
            elif app_type == "dashboard":
                dashboard_preprompt = self.load_preprompt("dashboard")
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

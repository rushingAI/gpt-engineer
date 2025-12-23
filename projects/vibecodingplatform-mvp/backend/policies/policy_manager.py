"""
平台策略管理器
加载和提供 generation_policy.json 中的策略配置
"""
import json
from pathlib import Path
from typing import Dict, List, Any, Optional
import fnmatch

class PolicyManager:
    """管理平台代码生成策略"""
    
    def __init__(self, policy_file: Optional[Path] = None):
        """
        初始化策略管理器
        
        Args:
            policy_file: 策略文件路径，默认为当前目录下的 generation_policy.json
        """
        if policy_file is None:
            policy_file = Path(__file__).parent / "generation_policy.json"
        
        self.policy_file = policy_file
        self._policy = self._load_policy()
    
    def _load_policy(self) -> Dict[str, Any]:
        """加载策略配置文件"""
        try:
            with open(self.policy_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"⚠️ 加载策略配置失败: {e}")
            # 返回默认策略
            return self._get_default_policy()
    
    def _get_default_policy(self) -> Dict[str, Any]:
        """返回默认策略（作为降级方案）"""
        return {
            "file_policy": {
                "allowlist_patterns": ["src/pages/**"],
                "denylist_patterns": ["package.json"]
            },
            "quality_gates": {"enabled": False},
            "self_heal": {"enabled": False, "max_iterations": 0}
        }
    
    # ===== 文件策略相关方法 =====
    
    def is_path_allowed(self, file_path: str) -> bool:
        """
        检查文件路径是否在允许写入范围内
        
        Args:
            file_path: 文件路径（相对路径，例如 'src/pages/Index.tsx'）
            
        Returns:
            是否允许写入
        """
        # 标准化路径（移除开头的 /）
        clean_path = file_path.lstrip('/')
        
        # 检查黑名单（优先级更高）
        denylist = self._policy.get("file_policy", {}).get("denylist_patterns", [])
        for pattern in denylist:
            if fnmatch.fnmatch(clean_path, pattern):
                return False
        
        # 检查白名单
        allowlist = self._policy.get("file_policy", {}).get("allowlist_patterns", [])
        for pattern in allowlist:
            if fnmatch.fnmatch(clean_path, pattern):
                return True
        
        return False
    
    def is_path_protected(self, file_path: str, template_files: Dict[str, str]) -> bool:
        """
        检查文件路径是否属于受保护的模板文件（不可被 AI 覆盖）
        
        Args:
            file_path: 文件路径
            template_files: 模板文件字典
            
        Returns:
            是否受保护
        """
        clean_path = file_path.lstrip('/')
        
        # 如果文件在模板中存在，检查是否在受保护目录下
        if clean_path in template_files:
            protected_dirs = self._policy.get("file_policy", {}).get(
                "protected_directories", {}
            ).get("paths", [])
            
            for protected_dir in protected_dirs:
                if clean_path.startswith(protected_dir):
                    # 如果是 generated 子目录，则不保护
                    if '/generated/' in clean_path:
                        return False
                    return True
        
        return False
    
    def get_allowed_patterns(self) -> List[str]:
        """获取允许写入的文件路径模式列表"""
        return self._policy.get("file_policy", {}).get("allowlist_patterns", [])
    
    def get_denied_patterns(self) -> List[str]:
        """获取禁止写入的文件路径模式列表"""
        return self._policy.get("file_policy", {}).get("denylist_patterns", [])
    
    # ===== 质量门禁相关方法 =====
    
    def is_quality_gates_enabled(self) -> bool:
        """质量门禁是否启用"""
        return self._policy.get("quality_gates", {}).get("enabled", False)
    
    def get_enabled_gate_levels(self) -> List[str]:
        """获取启用的门禁级别列表（按优先级排序）"""
        gates = self._policy.get("quality_gates", {}).get("levels", {})
        enabled_gates = []
        
        for level_name, config in gates.items():
            if config.get("enabled", False):
                enabled_gates.append({
                    "name": level_name,
                    "priority": config.get("priority", 99),
                    "config": config
                })
        
        # 按优先级排序
        enabled_gates.sort(key=lambda x: x["priority"])
        return [g["name"] for g in enabled_gates]
    
    def get_gate_config(self, level_name: str) -> Optional[Dict[str, Any]]:
        """获取指定门禁级别的配置"""
        return self._policy.get("quality_gates", {}).get("levels", {}).get(level_name)
    
    def get_static_gate_rules(self) -> List[Dict[str, Any]]:
        """获取静态闸门（L0）的规则列表"""
        l0_config = self.get_gate_config("L0_static")
        if l0_config:
            return l0_config.get("rules", [])
        return []
    
    # ===== shadcn/ui 组件白名单相关方法 =====
    
    def get_allowed_shadcn_components(self) -> List[str]:
        """获取允许的 shadcn/ui 组件列表"""
        return self._policy.get('shadcn_ui_components', {}).get('allowed_components', [])
    
    # ===== 自愈循环相关方法 =====
    
    def is_self_heal_enabled(self) -> bool:
        """自愈循环是否启用"""
        return self._policy.get("self_heal", {}).get("enabled", False)
    
    def get_max_heal_iterations(self) -> int:
        """获取自愈最大迭代次数"""
        return self._policy.get("self_heal", {}).get("max_iterations", 3)
    
    def get_max_files_per_iteration(self) -> int:
        """获取每轮迭代最大修改文件数"""
        return self._policy.get("self_heal", {}).get("max_files_per_iteration", 8)
    
    def should_reuse_node_modules(self) -> bool:
        """是否复用 node_modules（避免重复安装）"""
        return self._policy.get("self_heal", {}).get("reuse_node_modules", True)
    
    def get_heal_allowed_patterns(self) -> List[str]:
        """获取自愈循环允许修改的文件模式"""
        return self._policy.get("self_heal", {}).get("allowed_modification_patterns", [])
    
    # ===== 预览模式相关方法 =====
    
    def get_preview_fallback_reason(self, reason_code: str, lang: str = "zh") -> str:
        """
        获取预览不可用的原因文案
        
        Args:
            reason_code: 原因码（例如 'MOBILE_NOT_SUPPORTED'）
            lang: 语言代码（'en' 或 'zh'）
            
        Returns:
            本地化的原因文案
        """
        reasons = self._policy.get("preview_modes", {}).get("fallback_reasons", {})
        reason_obj = reasons.get(reason_code, {})
        return reason_obj.get(lang, reason_obj.get("en", "Preview not available"))
    
    # ===== Spec-first 相关方法 =====
    
    def is_spec_first_enabled(self) -> bool:
        """Spec-first 生成策略是否启用"""
        return self._policy.get("spec_first", {}).get("enabled", False)
    
    def get_spec_location(self) -> str:
        """获取 InteractionSpec 的存放路径"""
        return self._policy.get("spec_first", {}).get(
            "spec_location", 
            "src/lib/generated/interactionSpec.json"
        )
    
    def is_strict_json_required(self) -> bool:
        """是否要求严格 JSON 格式"""
        return self._policy.get("spec_first", {}).get("strict_json", True)
    
    def should_auto_repair_json(self) -> bool:
        """是否自动修复 JSON 格式错误"""
        return self._policy.get("spec_first", {}).get("auto_repair_json", True)
    
    def get_max_json_repair_attempts(self) -> int:
        """获取 JSON 修复最大尝试次数"""
        return self._policy.get("spec_first", {}).get("max_repair_attempts", 1)
    
    def get_required_spec_sections(self) -> List[str]:
        """获取 Spec 必需的章节"""
        return self._policy.get("spec_first", {}).get(
            "required_sections", 
            ["state", "events", "constraints", "acceptance"]
        )
    
    def get_acceptance_test_range(self) -> tuple:
        """获取 acceptance 测试数量范围 (min, max)"""
        min_tests = self._policy.get("spec_first", {}).get("min_acceptance_tests", 2)
        max_tests = self._policy.get("spec_first", {}).get("max_acceptance_tests", 5)
        return (min_tests, max_tests)
    
    # ===== 回归测试相关方法 =====
    
    def get_regression_suites(self) -> List[Dict[str, Any]]:
        """获取回归测试套件列表"""
        return self._policy.get("regression_suites", {}).get("suites", [])
    
    def get_p0_regression_suite(self) -> Optional[Dict[str, Any]]:
        """获取 P0 优先级的回归测试套件"""
        suites = self.get_regression_suites()
        for suite in suites:
            if suite.get("priority") == "P0" and suite.get("enabled", True):
                return suite
        return None


# 全局策略管理器实例
policy_manager = PolicyManager()


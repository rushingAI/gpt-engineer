"""
Style Selector - 根据用户 prompt 自动选择视觉风格
支持 deterministic 选择（同样的 prompt 总是得到同样的 style）
"""

import hashlib
import re
from typing import Tuple, Optional, List


# 可用的风格列表
AVAILABLE_STYLES = [
    "cyberpunk",
    "aurora",
    "glass",
    "neo_brutal",
    "minimal",
    "retro_futurism"
]

# 风格到模板的映射
STYLE_TO_TEMPLATE = {
    "cyberpunk": "react-ts-shadcn-cyberpunk",
    "aurora": "react-ts-shadcn-aurora",
    "glass": "react-ts-shadcn-glass",
    "neo_brutal": "react-ts-shadcn-neo-brutal",
    "minimal": "react-ts-shadcn-minimal",
    "retro_futurism": "react-ts-shadcn-retro-futurism"
}

# 暖色系风格子集
WARM_STYLES = ["retro_futurism", "neo_brutal", "minimal"]

# 冷色系风格子集
COOL_STYLES = ["aurora", "glass", "cyberpunk"]

# 风格关键词匹配（用于在色温匹配后进一步细化）
# 注意：关键词应该是风格特有的，避免冲突
STYLE_KEYWORDS = {
    "aurora": ["梦幻", "极光", "流动", "柔和", "ethereal", "dreamy", "aurora", "flowing"],
    "glass": ["玻璃", "透明", "清透", "glass", "transparent", "clear", "frosted"],
    "cyberpunk": ["赛博", "霓虹", "科技", "cyber", "neon", "tech", "tech-noir"],
    "neo_brutal": ["粗野", "大胆", "强烈", "brutal", "bold", "strong"],
    "minimal": ["极简", "简约", "克制", "minimal", "simple", "refined"],
    "retro_futurism": ["复古", "怀旧", "80s", "90s", "retro", "vintage", "nostalgia", "复古未来"]
}

# 颜色关键词到色温的映射
COLOR_KEYWORDS = {
    # 暖色系
    "warm": {"暖色", "温暖", "暖调"},
    "orange": {"橙色", "橙", "orange", "橘色", "橘"},
    "red": {"红色", "红", "red", "crimson", "scarlet"},
    "yellow": {"黄色", "黄", "yellow", "金色", "gold"},
    "brown": {"棕色", "棕", "brown", "咖啡色"},
    
    # 冷色系
    "cool": {"冷色", "冷调", "清冷"},
    "blue": {"蓝色", "蓝", "blue", "azure", "navy"},
    "cyan": {"青色", "青", "cyan", "teal", "turquoise"},
    "purple": {"紫色", "紫", "purple", "violet", "indigo"},
    "green": {"绿色", "绿", "green", "emerald"}
}

# Hex 颜色到色温的判断（简化版）
def get_hex_temperature(hex_color: str) -> Optional[str]:
    """根据 hex 颜色判断色温（warm/cool）"""
    hex_color = hex_color.lstrip('#')
    if len(hex_color) != 6:
        return None
    
    try:
        r = int(hex_color[0:2], 16)
        g = int(hex_color[2:4], 16)
        b = int(hex_color[4:6], 16)
        
        # 简单启发式：红>蓝 => 暖色，蓝>红 => 冷色
        if r > b + 30:
            return "warm"
        elif b > r + 30:
            return "cool"
        else:
            return None
    except ValueError:
        return None


def detect_color_preference(prompt: str) -> Tuple[Optional[str], Optional[str]]:
    """
    检测用户 prompt 中的颜色偏好
    
    Returns:
        (temperature, detected_keyword): 
        - temperature: "warm" or "cool" or None
        - detected_keyword: 检测到的颜色关键词（用于 meta）
    """
    prompt_lower = prompt.lower()
    
    # 1. 检测 hex 颜色
    hex_pattern = r'#?[0-9a-fA-F]{6}'
    hex_matches = re.findall(hex_pattern, prompt)
    if hex_matches:
        for hex_color in hex_matches:
            temp = get_hex_temperature(hex_color)
            if temp:
                return temp, f"hex:{hex_color}"
    
    # 2. 检测颜色关键词
    warm_score = 0
    cool_score = 0
    detected_keywords = []
    first_temperature = None
    
    for color_type, keywords in COLOR_KEYWORDS.items():
        for keyword in keywords:
            if keyword in prompt_lower:
                detected_keywords.append(keyword)
                # 根据颜色类型打分
                if color_type in ["warm", "orange", "red", "yellow", "brown"]:
                    warm_score += 1
                    if first_temperature is None:
                        first_temperature = "warm"
                elif color_type in ["cool", "blue", "cyan", "purple", "green"]:
                    cool_score += 1
                    if first_temperature is None:
                        first_temperature = "cool"
    
    if not detected_keywords:
        return None, None
    
    detected_keyword = ", ".join(detected_keywords[:3])  # 最多显示3个
    
    # 如果有明显的色温倾向，使用它
    if warm_score > cool_score:
        return "warm", detected_keyword
    elif cool_score > warm_score:
        return "cool", detected_keyword
    # 如果分数相等，使用第一个检测到的颜色的色温
    elif first_temperature:
        return first_temperature, detected_keyword
    
    return None, None


def select_style_deterministic(prompt: str, style: str = "auto") -> Tuple[str, str, dict]:
    """
    Deterministic 地选择风格
    
    Args:
        prompt: 用户输入的提示词
        style: 用户指定的风格（"auto" 或具体风格名）
        
    Returns:
        (selected_style, style_source, metadata):
        - selected_style: 最终选择的风格
        - style_source: 选择来源 ("explicit" / "color_match" / "keyword_match" / "hash_auto")
        - metadata: 额外元数据（detected_colors, seed 等）
    """
    metadata = {}
    
    # 1. 如果用户显式指定了风格
    if style != "auto" and style in AVAILABLE_STYLES:
        return style, "explicit", metadata
    
    # 2. 检测颜色偏好
    temperature, detected_keyword = detect_color_preference(prompt)
    if temperature:
        metadata["detected_color"] = detected_keyword
        metadata["temperature"] = temperature
        
        # 从对应色温的风格子集中选择
        style_pool = WARM_STYLES if temperature == "warm" else COOL_STYLES
        
        # 2.1 先尝试风格关键词匹配（在色温子集内）
        prompt_lower = prompt.lower()
        for candidate_style in style_pool:
            if candidate_style in STYLE_KEYWORDS:
                for keyword in STYLE_KEYWORDS[candidate_style]:
                    if keyword in prompt_lower:
                        metadata["matched_keyword"] = keyword
                        return candidate_style, "keyword_match", metadata
        
        # 2.2 如果没有匹配的关键词，使用 hash 从子集中确定性选择
        prompt_normalized = prompt.strip().lower()
        hash_obj = hashlib.sha256(prompt_normalized.encode('utf-8'))
        seed = int(hash_obj.hexdigest(), 16)
        metadata["seed"] = seed % 1000000  # 截断以便可读
        
        selected_style = style_pool[seed % len(style_pool)]
        return selected_style, "color_match", metadata
    
    # 3. 没有颜色偏好：检查是否有风格关键词
    prompt_lower = prompt.lower()
    for candidate_style in AVAILABLE_STYLES:
        if candidate_style in STYLE_KEYWORDS:
            for keyword in STYLE_KEYWORDS[candidate_style]:
                if keyword in prompt_lower:
                    metadata["matched_keyword"] = keyword
                    return candidate_style, "keyword_match", metadata
    
    # 4. 最后：使用 hash 从全部风格中确定性选择
    prompt_normalized = prompt.strip().lower()
    hash_obj = hashlib.sha256(prompt_normalized.encode('utf-8'))
    seed = int(hash_obj.hexdigest(), 16)
    metadata["seed"] = seed % 1000000
    
    selected_style = AVAILABLE_STYLES[seed % len(AVAILABLE_STYLES)]
    return selected_style, "hash_auto", metadata


def get_template_for_style(style: str) -> str:
    """根据风格获取对应的模板名"""
    return STYLE_TO_TEMPLATE.get(style, "react-ts-shadcn")


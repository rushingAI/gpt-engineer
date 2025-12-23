"""
InteractionSpec 生成器 - Spec-first 交互式应用生成的核心
"""
import json
from typing import Dict, Any, Optional, Tuple
from policies import policy_manager
from langchain_core.messages import HumanMessage


def generate_interaction_spec_prompt(user_request: str, app_type: str) -> str:
    """
    构建生成 InteractionSpec 的 prompt
    
    Args:
        user_request: 用户需求描述
        app_type: 应用类型
        
    Returns:
        用于生成 Spec 的 prompt
    """
    min_acceptance, max_acceptance = policy_manager.get_acceptance_test_range()
    required_sections = policy_manager.get_required_spec_sections()
    
    return f"""You are an expert in designing interactive web applications. Your task is to create an InteractionSpec (JSON) that defines HOW the application should be interactive.

USER REQUEST:
{user_request}

APPLICATION TYPE: {app_type}

OUTPUT A STRICT JSON (no markdown, no comments, no extra text) with these sections:
{json.dumps(required_sections)}

InteractionSpec Structure:
{{
  "state": [
    {{
      "name": "stateName",
      "type": "string | number | boolean | object | array",
      "init": "how to initialize (e.g., 'empty array', 'null', '0')",
      "description": "what this state represents"
    }}
  ],
  "events": [
    {{
      "trigger": "click | input | keydown | submit | change | custom",
      "target": "which element (e.g., 'grid cell', 'submit button')",
      "handler": "what happens (e.g., 'update selectedCell state')",
      "state_updates": ["list of state names that get updated"]
    }}
  ],
  "constraints": [
    {{
      "rule": "describe the constraint (e.g., 'original cells cannot be edited')",
      "enforcement": "how to enforce (e.g., 'readOnly={{originalBoard[row][col] !== null}}')",
      "state_dependency": "which state is used to enforce this"
    }}
  ],
  "acceptance": [
    "User can click an empty cell to select it",
    "User can input a number (1-9) via keyboard or number pad",
    "Original cells are locked and cannot be edited",
    ...{max_acceptance - 2} more testable criteria...
  ]
}}

CRITICAL RULES:
1. Output ONLY valid JSON (no markdown, no code blocks, no ```json)
2. acceptance MUST have {min_acceptance}-{max_acceptance} items
3. All state MUST have corresponding events that update them
4. All constraints MUST reference state from the state section
5. Focus on INTERACTIVITY, not static UI

EXAMPLE for a Todo List:
{{
  "state": [
    {{"name": "todos", "type": "array", "init": "empty array", "description": "list of todo items"}},
    {{"name": "inputValue", "type": "string", "init": "empty string", "description": "current input text"}}
  ],
  "events": [
    {{"trigger": "input", "target": "text input", "handler": "update inputValue state", "state_updates": ["inputValue"]}},
    {{"trigger": "submit", "target": "add button", "handler": "append inputValue to todos, clear inputValue", "state_updates": ["todos", "inputValue"]}},
    {{"trigger": "click", "target": "delete button", "handler": "remove item from todos", "state_updates": ["todos"]}}
  ],
  "constraints": [
    {{"rule": "cannot submit empty todo", "enforcement": "button disabled when inputValue.trim() === ''", "state_dependency": "inputValue"}}
  ],
  "acceptance": [
    "User can type text into the input field",
    "User can click 'Add' to append a new todo",
    "User can click 'Delete' to remove a todo",
    "Submit button is disabled when input is empty"
  ]
}}

Now generate the InteractionSpec for the user's request. Output ONLY the JSON:"""


def repair_interaction_spec_json(broken_json_text: str, error_message: str) -> str:
    """
    构建修复 JSON 格式错误的 prompt
    
    Args:
        broken_json_text: 格式错误的 JSON 文本
        error_message: JSON 解析错误信息
        
    Returns:
        用于修复 JSON 的 prompt
    """
    return f"""The following JSON has syntax errors. Fix it and return ONLY the corrected JSON (no markdown, no explanation):

ERROR:
{error_message}

BROKEN JSON:
{broken_json_text}

OUTPUT THE CORRECTED JSON (no ```json, just the raw JSON):"""


def parse_interaction_spec(spec_text: str) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
    """
    解析 InteractionSpec JSON
    
    Args:
        spec_text: 待解析的 JSON 文本
        
    Returns:
        (spec_dict, error_message)
        成功时返回 (dict, None)
        失败时返回 (None, error_message)
    """
    # 尝试提取 JSON（防止模型输出了 markdown 代码块）
    spec_text = spec_text.strip()
    
    # 移除可能的 markdown 代码块标记
    if spec_text.startswith('```json'):
        spec_text = spec_text[7:]
    elif spec_text.startswith('```'):
        spec_text = spec_text[3:]
    
    if spec_text.endswith('```'):
        spec_text = spec_text[:-3]
    
    spec_text = spec_text.strip()
    
    try:
        spec_dict = json.loads(spec_text)
        
        # 验证必需的章节
        required_sections = policy_manager.get_required_spec_sections()
        missing_sections = [s for s in required_sections if s not in spec_dict]
        
        if missing_sections:
            return None, f"Missing required sections: {', '.join(missing_sections)}"
        
        # 验证 acceptance 数量
        min_acceptance, max_acceptance = policy_manager.get_acceptance_test_range()
        acceptance_count = len(spec_dict.get('acceptance', []))
        
        if acceptance_count < min_acceptance or acceptance_count > max_acceptance:
            return None, f"acceptance must have {min_acceptance}-{max_acceptance} items, got {acceptance_count}"
        
        return spec_dict, None
        
    except json.JSONDecodeError as e:
        return None, f"JSON parse error: {str(e)}"
    except Exception as e:
        return None, f"Validation error: {str(e)}"


def validate_and_repair_spec(ai, initial_spec_text: str) -> Tuple[Optional[Dict[str, Any]], str]:
    """
    验证并修复 InteractionSpec
    
    Args:
        ai: AI 实例
        initial_spec_text: 初始生成的 Spec 文本
        
    Returns:
        (spec_dict, status_message)
        成功时返回 (dict, "success" 或 "repaired")
        失败时返回 (None, error_message)
    """
    # 第一次尝试解析
    spec_dict, error = parse_interaction_spec(initial_spec_text)
    
    if spec_dict is not None:
        print("   ✓ InteractionSpec 解析成功")
        return spec_dict, "success"
    
    # 解析失败，尝试修复（如果策略允许）
    if not policy_manager.should_auto_repair_json():
        print(f"   ✗ InteractionSpec 解析失败: {error}")
        return None, f"JSON parse failed: {error}"
    
    max_attempts = policy_manager.get_max_json_repair_attempts()
    print(f"   ⚠️  InteractionSpec 解析失败，尝试修复（最多 {max_attempts} 次）...")
    print(f"   错误: {error}")
    
    for attempt in range(max_attempts):
        repair_prompt = repair_interaction_spec_json(initial_spec_text, error)
        
        # 调用 AI 修复
        messages = ai.next(
            messages=[HumanMessage(content=repair_prompt)],
            step_name=f"repair_spec_attempt_{attempt + 1}"
        )
        
        # 获取 AI 的响应
        repaired_spec_text = messages[-1].content
        
        # 尝试解析修复后的结果
        spec_dict, error = parse_interaction_spec(repaired_spec_text)
        
        if spec_dict is not None:
            print(f"   ✓ InteractionSpec 修复成功（第 {attempt + 1} 次尝试）")
            return spec_dict, "repaired"
        
        print(f"   ✗ 修复尝试 {attempt + 1} 失败: {error}")
        initial_spec_text = repaired_spec_text  # 用修复后的文本继续下一轮
    
    print(f"   ✗ InteractionSpec 修复失败，已达到最大尝试次数")
    return None, f"Failed to repair after {max_attempts} attempts"


def create_spec_summary(spec_dict: Dict[str, Any]) -> Dict[str, Any]:
    """
    创建 Spec 的摘要（用于写入 vibe.meta.json）
    
    Args:
        spec_dict: InteractionSpec 字典
        
    Returns:
        摘要字典
    """
    return {
        "state_count": len(spec_dict.get("state", [])),
        "events_count": len(spec_dict.get("events", [])),
        "constraints_count": len(spec_dict.get("constraints", [])),
        "acceptance_count": len(spec_dict.get("acceptance", [])),
        "state_names": [s.get("name") for s in spec_dict.get("state", [])],
        "event_triggers": list(set([e.get("trigger") for e in spec_dict.get("events", [])])),
    }


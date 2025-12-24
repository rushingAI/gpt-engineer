"""
自愈循环 - 自动修复质量门禁失败的代码
"""
import json
import fnmatch
from typing import Dict, Any, Tuple, List
from policies import policy_manager
from quality_gates import run_quality_gates, format_gate_results_for_heal, GateResult
from langchain_core.messages import HumanMessage
from prompt_fragments import (
    build_base_rules,
    build_dynamic_rules,
    format_spec_payload,
    get_policy_version,
    log_prompt_telemetry,
    compute_prompt_hash
)
from dependency_detector import detect_dependencies_in_files
from dependency_arbiter import DependencyArbiter


def count_errors(gate_results: Dict[str, GateResult]) -> int:
    """
    只统计 L0_static 的 error，不计 warning
    与门禁 passed 语义保持一致
    """
    if "L0_static" in gate_results:
        result = gate_results["L0_static"]
        return len([i for i in result.issues if i.get('severity') == 'error'])
    
    # 退化：全量统计
    return sum(
        len([i for i in r.issues if i.get('severity') == 'error'])
        for r in gate_results.values()
    )


def count_total_issues(gate_results: Dict[str, GateResult]) -> int:
    """统计所有 issues（用于 warning 爆炸保护）"""
    return sum(len(r.issues) for r in gate_results.values())


def should_accept_debt(gate_results: Dict[str, GateResult]) -> Tuple[bool, str]:
    """
    当仅剩 data_contract 问题且 TypeCheck 通过时，允许接受债务结束
    """
    errors = [
        i for r in gate_results.values() 
        for i in r.issues 
        if i.get('severity') == 'error'
    ]
    
    if not errors:
        return True, "no_errors"
    
    non_data_contract_errors = [
        e for e in errors 
        if e.get('rule_id') != 'data_contract_violation'
    ]
    
    # 仅剩 data_contract 且 TypeCheck 通过
    typecheck_passed = gate_results.get("L1_typecheck", GateResult('L1_typecheck', True)).passed
    if not non_data_contract_errors and typecheck_passed:
        return True, "data_contract_debt_accepted"
    
    return False, ""


def build_heal_prompt(
    gate_results: Dict[str, GateResult],
    interaction_spec: Dict[str, Any],
    current_files: Dict[str, str],
    iteration: int
) -> tuple[str, List[str]]:
    """
    构建自愈修复的 prompt（固定 5 段模板）
    
    Args:
        gate_results: 门禁结果
        interaction_spec: InteractionSpec
        current_files: 当前文件
        iteration: 当前迭代次数
        
    Returns:
        (修复 prompt, 激活的动态规则 IDs)
    """
    # === 第 1 段: Goal ===
    goal_section = f"""GOAL: Fix quality gate failures and keep application runnable.
Iteration {iteration + 1}/{policy_manager.get_max_heal_iterations()}"""
    
    # === 第 2 段: FailedGates（短列表）===
    failed_gates = []
    for gate_name, result in gate_results.items():
        if not result.passed:
            issue_count = len(result.issues)
            failed_gates.append(f"  - {gate_name}: {issue_count} issues")
    
    failed_gates_section = "FAILED GATES:\n" + "\n".join(failed_gates)
    
    # === 第 3 段: Evidence（门禁证据，优化后不需要截断）===
    gate_errors = format_gate_results_for_heal(
        gate_results, 
        max_issues=8,  # 限制为8个最重要的问题
        group_by_file=True  # 按文件分组
    )
    
    # 移除旧的截断逻辑（新方法已内置智能限制）
    # if len(gate_errors) > 2000:
    #     gate_errors = gate_errors[:2000] + "\n... (truncated)"
    
    evidence_section = f"EVIDENCE:\n{gate_errors}"
    
    # === 第 4 段: AllowedLocked（glob/patterns）===
    allowed_patterns = policy_manager.get_heal_allowed_patterns()
    allowed_paths_str = ", ".join(allowed_patterns) if allowed_patterns else "src/pages/**, src/components/generated/**, src/lib/generated/**"
    
    locked_paths = [
        'package.json', 'vite.config.*', 'src/main.tsx', 
        'src/index.css', 'src/components/ui/*'
    ]
    locked_paths_str = ", ".join(locked_paths)
    
    allowed_locked_section = f"""ALLOWED/LOCKED:
- You MAY ONLY modify files matching: {allowed_paths_str}
- You MUST NOT modify: {locked_paths_str}
- You MUST NOT introduce new dependencies/libraries. Fix ONLY with existing pre-installed libraries (react, date-fns, lucide-react, framer-motion, recharts, etc.). If a chart library is needed, use pure CSS/SVG or the existing implementation.

CRITICAL - Do NOT refactor or restructure code:
- Fix ONLY the specific issues listed in EVIDENCE
- Do NOT rename exports/imports unless fixing a mismatch
- Do NOT change function signatures
- Do NOT reorganize file structure
- Do NOT add new features or abstractions
- MINIMIZE the scope of changes to only what's necessary to pass the gates"""
    
    # === 第 5 段: OutputContract ===
    output_contract_section = """OUTPUT CONTRACT:
- Output COMPLETE files only (not partial diffs)
- Use this format:
  filename.tsx
  ```
  // ALL imports
  // ALL code
  // ALL styles
  ```
- You must follow BaseRules (see below)"""
    
    # === 引用 BaseRules（不复制粘贴）===
    base_rules_ref = build_base_rules(mode='heal')
    
    # === 动态规则（基于门禁失败注入）===
    dynamic_context = {
        'gate_results': gate_results,
        'files': current_files,
        'prompt_text': '',
        'interaction_spec': interaction_spec
    }
    dynamic_rules, activated_rule_ids = build_dynamic_rules(dynamic_context)
    
    # === Spec 载荷（紧凑模式，只在需要时）===
    spec_section, spec_mode = format_spec_payload(
        interaction_spec, 
        gate_results=gate_results,
        prefer_summary=True
    )
    
    # === 拼接最终 prompt（固定 5 段 + BaseRules + DynamicRules）===
    prompt = f"""You are an expert code fixer.

{goal_section}

{failed_gates_section}

{evidence_section}

{allowed_locked_section}

{output_contract_section}

================================================================================
{base_rules_ref}

{dynamic_rules}

{spec_section}

Fix the issues now (output COMPLETE modified files):"""
    
    return prompt, activated_rule_ids


def should_trigger_self_heal(gate_results: Dict[str, GateResult]) -> bool:
    """
    判断是否应该触发自愈循环
    
    Args:
        gate_results: 门禁结果
        
    Returns:
        是否应该触发自愈
    """
    if not policy_manager.is_self_heal_enabled():
        return False
    
    # 如果有任何门禁失败，触发自愈
    return any(not result.passed for result in gate_results.values())


def self_heal_loop(
    ai,
    initial_files: Dict[str, str],
    gate_results: Dict[str, GateResult],
    interaction_spec: Dict[str, Any] = None
) -> Tuple[Dict[str, str], bool, int]:
    """
    执行自愈循环
    
    Args:
        ai: AI 实例
        initial_files: 初始文件
        gate_results: 初始门禁结果
        interaction_spec: InteractionSpec
        
    Returns:
        (final_files, success, iteration_count)
    """
    from datetime import datetime
    
    max_iterations = policy_manager.get_max_heal_iterations()
    
    current_files = dict(initial_files)
    current_gate_results = gate_results
    
    # 🆕 初始化 best snapshot 机制
    best_snapshot = {
        "files": current_files.copy(),
        "gate_results": current_gate_results,
        "error_count": count_errors(current_gate_results),
        "total_count": count_total_issues(current_gate_results),
        "iteration": 0
    }
    
    # 🆕 初始化治愈历史记录
    healing_history = []
    
    # 动态调整 max_files
    initial_max_files = policy_manager.get_max_files_per_iteration()
    max_files_this_iteration = initial_max_files
    regression_count = 0
    WARNING_EXPLOSION_THRESHOLD = 10
    
    for iteration in range(max_iterations):
        # 检查接受债务
        can_accept, reason = should_accept_debt(current_gate_results)
        if can_accept:
            print(f"   ✅ 接受债务结束：{reason}")
            return current_files, True, iteration
        
        if not should_trigger_self_heal(current_gate_results):
            print(f"   ✓ 迭代 {iteration}: 所有门禁通过，自愈成功")
            return current_files, True, iteration
        
        # 保存 previous 状态
        previous_files = current_files.copy()
        previous_error_count = count_errors(current_gate_results)
        previous_total_count = count_total_issues(current_gate_results)
        
        print(f"   🔧 迭代 {iteration + 1}/{max_iterations}: 开始修复...")
        
        # 构建修复 prompt
        heal_prompt, activated_rule_ids = build_heal_prompt(
            current_gate_results,
            interaction_spec,
            current_files,
            iteration
        )
        
        # 记录 telemetry
        log_prompt_telemetry(
            prompt=heal_prompt,
            mode='heal',
            activated_fragments=activated_rule_ids,
            spec_mode='auto',
            context={
                'policy_version': get_policy_version(),
                'iteration': iteration + 1,
                'max_iterations': max_iterations
            }
        )
        
        # 调用 AI 修复
        try:
            messages = ai.next(
                messages=[HumanMessage(content=heal_prompt)],
                step_name=f"self_heal_iteration_{iteration + 1}"
            )
            
            # 获取 AI 的响应
            fixed_code = messages[-1].content
            
            # 解析修复后的文件
            # 使用与 gen_code 相同的解析逻辑
            from gpt_engineer.core.chat_to_files import chat_to_files_dict
            
            fixed_files_dict = chat_to_files_dict(fixed_code)
            
            print(f"     📝 AI 返回了 {len(fixed_files_dict)} 个文件")
            
            if not fixed_files_dict:
                print(f"     ⚠️  迭代 {iteration + 1}: AI 未返回有效文件，跳过")
                continue
            
            # 检查修改的文件数量（使用动态限制）
            if len(fixed_files_dict) > max_files_this_iteration:
                print(
                    f"     ⚠️  迭代 {iteration + 1}: AI 修改了 {len(fixed_files_dict)} 个文件，"
                    f"超过限制 {max_files_this_iteration}，截断"
                )
                # 只保留前 N 个文件
                fixed_files_dict = dict(list(fixed_files_dict.items())[:max_files_this_iteration])
            
            # 合并修复后的文件（带路径过滤）
            # 🆕 收集治愈行为信息
            allowed_patterns = policy_manager.get_heal_allowed_patterns()
            filtered_count = 0
            filtered_paths = []
            files_modified = []
            
            for filename, content in fixed_files_dict.items():
                # 检查文件是否在允许修改的范围内
                is_allowed = False
                if allowed_patterns:
                    for pattern in allowed_patterns:
                        if fnmatch.fnmatch(filename, pattern):
                            is_allowed = True
                            break
                else:
                    # 如果没有配置 allowed_patterns，使用默认规则
                    is_allowed = any(filename.startswith(prefix) for prefix in [
                        'src/pages/', 'src/components/generated/', 'src/lib/generated/'
                    ])
                
                if is_allowed:
                    old_content = current_files.get(filename, "")
                    current_files[filename] = content
                    
                    # 🆕 记录文件修改详情
                    is_new = filename not in initial_files and old_content == ""
                    is_changed = old_content != content
                    
                    file_change_record = {
                        "path": filename,
                        "action": "created" if is_new else ("modified" if is_changed else "unchanged"),
                        "size_before": len(old_content),
                        "size_after": len(content),
                        "lines_before": old_content.count('\n') + 1 if old_content else 0,
                        "lines_after": content.count('\n') + 1 if content else 0
                    }
                    files_modified.append(file_change_record)
                    
                    # 添加调试信息：显示文件是否真正被修改
                    if is_changed:
                        print(f"     ✓ 修复了: {filename} (内容已更新, {len(content)} 字符)")
                    else:
                        print(f"     ⚠️  修复了: {filename} (内容未变化)")
                else:
                    filtered_count += 1
                    filtered_paths.append(filename)
                    print(f"     ✗ 跳过（超出允许范围）: {filename}")
            
            if filtered_count > 0:
                print(f"     ⚠️  过滤了 {filtered_count} 个超出允许范围的文件修改")
            
            # === 依赖检测与仲裁（防止自愈引入未授权依赖）===
            try:
                detected_deps = detect_dependencies_in_files(current_files)
                if detected_deps:
                    arbiter = DependencyArbiter()
                    dep_report = arbiter.arbitrate(detected_deps)
                    
                    # 更新 vibe.meta.json
                    if 'vibe.meta.json' in current_files:
                        try:
                            vibe_meta = json.loads(current_files['vibe.meta.json'])
                            vibe_meta['dependencies'] = dep_report
                            current_files['vibe.meta.json'] = json.dumps(vibe_meta, indent=2)
                            print(f"     📦 更新依赖报告: {len(dep_report.get('approved', []))} 个批准")
                        except json.JSONDecodeError:
                            pass
            except Exception as dep_err:
                print(f"     ⚠️  依赖检测跳过: {dep_err}")
            
            # 重新运行门禁（只运行 L0，不重装依赖）
            print(f"   🚦 迭代 {iteration + 1}: 重新运行门禁...")
            new_gate_results = run_quality_gates(current_files)
            current_gate_results = new_gate_results  # 同步更新
            
            # 🆕 统计 error 和 total issues
            current_error_count = count_errors(current_gate_results)
            current_total_count = count_total_issues(current_gate_results)
            
            # 更新 best snapshot（error 最少 → total 最少）
            is_better = (
                current_error_count < best_snapshot["error_count"] or
                (current_error_count == best_snapshot["error_count"] and 
                 current_total_count < best_snapshot["total_count"])
            )
            if is_better:
                best_snapshot = {
                    "files": current_files.copy(),
                    "gate_results": current_gate_results,
                    "error_count": current_error_count,
                    "total_count": current_total_count,
                    "iteration": iteration + 1
                }
                print(f"     📌 更新 best_snapshot: {current_error_count} errors, {current_total_count} total")
            
            # 判断 regression
            is_hard_regression = current_error_count > previous_error_count
            is_soft_regression = (
                current_error_count <= previous_error_count and
                current_total_count > previous_total_count + WARNING_EXPLOSION_THRESHOLD
            )
            is_regression = is_hard_regression or is_soft_regression
            
            iteration_record = {
                "iteration": iteration + 1,
                "timestamp": datetime.now().isoformat(),
                "error_count": current_error_count,
                "total_count": current_total_count,
                "regression": is_regression,
                "regression_type": "hard" if is_hard_regression else ("soft" if is_soft_regression else "none"),
                # 🆕 治愈行为记录（记录AI修改了哪些文件）
                "healing_actions": {
                    "ai_returned_files": len(fixed_files_dict),
                    "files_applied": len(files_modified),
                    "files_filtered": filtered_count,
                    "filtered_paths": filtered_paths,
                    "max_files_limit": max_files_this_iteration,
                    "changes": files_modified  # 每个文件的修改详情
                },
                "gates": {
                    gate_name: {
                        "passed": result.passed,
                        "issues_count": len(result.issues),
                        "issues": [
                            {
                                "rule_id": issue.get('rule_id'),
                                "severity": issue.get('severity'),
                                "file": issue.get('file'),
                                "message": issue.get('message')
                            }
                            for issue in result.issues  # 🔧 移除截断限制，记录所有问题
                        ]
                    }
                    for gate_name, result in current_gate_results.items()
                }
            }
            healing_history.append(iteration_record)
            
            # 更新 vibe.meta.json 的 quality_gates 字段
            if 'vibe.meta.json' in current_files:
                try:
                    vibe_meta = json.loads(current_files['vibe.meta.json'])
                    if 'quality_gates' not in vibe_meta:
                        vibe_meta['quality_gates'] = {}
                    
                    vibe_meta['quality_gates']['healing_history'] = healing_history
                    vibe_meta['quality_gates']['final'] = {
                        gate_name: result.to_dict()
                        for gate_name, result in current_gate_results.items()
                    }
                    current_files['vibe.meta.json'] = json.dumps(vibe_meta, indent=2)
                    print(f"     📊 更新质量门历史: 迭代 {iteration + 1}, {current_total_count} 个问题" + (" [回归⚠️]" if is_regression else ""))
                except json.JSONDecodeError:
                    print(f"     ⚠️  无法更新 vibe.meta.json: JSON 解析失败")
            
            # 检查是否需要回滚
            if is_regression:
                regression_type = "hard" if is_hard_regression else "soft(warning爆炸)"
                print(f"     ⚠️  {regression_type} regression: {previous_error_count} → {current_error_count} errors")
                current_files = previous_files
                current_gate_results = run_quality_gates(current_files)  # 同步
                regression_count += 1
                
                if regression_count >= 2:
                    print(f"     ❌ 连续 regression，输出 best_snapshot (iteration {best_snapshot['iteration']})")
                    current_files = best_snapshot["files"]
                    current_gate_results = best_snapshot["gate_results"]
                    break
                
                # 回滚后收紧策略
                max_files_this_iteration = 1
                print(f"     ↓ max_files 收紧到 {max_files_this_iteration}")
                continue
            
            # 成功后逐步恢复 max_files
            if max_files_this_iteration < initial_max_files:
                max_files_this_iteration = min(max_files_this_iteration + 2, initial_max_files)
                print(f"     ↑ max_files 恢复到 {max_files_this_iteration}")
            regression_count = 0  # 重置连续 regression 计数
            
            # 检查是否通过
            failed_count = sum(1 for r in current_gate_results.values() if not r.passed)
            if failed_count == 0:
                print(f"   ✓ 迭代 {iteration + 1}: 所有门禁通过！")
                return current_files, True, iteration + 1
            else:
                print(f"   ⚠️  迭代 {iteration + 1}: 仍有 {failed_count} 个门禁失败")
        
        except Exception as e:
            print(f"   ✗ 迭代 {iteration + 1}: 修复失败 - {str(e)}")
            continue
    
    # 达到最大迭代次数，仍未通过
    print(f"   ✗ 自愈失败：已达到最大迭代次数 {max_iterations}")
    
    # 最终输出 best（如果当前不是 best）
    final_error_count = count_errors(current_gate_results)
    if final_error_count > best_snapshot["error_count"]:
        print(f"   📌 输出 best_snapshot (iteration {best_snapshot['iteration']}): {best_snapshot['error_count']} errors")
        current_files = best_snapshot["files"]
        current_gate_results = best_snapshot["gate_results"]
    
    # 🆕 确保最终状态被记录到 vibe.meta.json
    if 'vibe.meta.json' in current_files and healing_history:
        try:
            vibe_meta = json.loads(current_files['vibe.meta.json'])
            if 'quality_gates' not in vibe_meta:
                vibe_meta['quality_gates'] = {}
            
            vibe_meta['quality_gates']['healing_history'] = healing_history
            vibe_meta['quality_gates']['final'] = {
                gate_name: result.to_dict()
                for gate_name, result in current_gate_results.items()
            }
            current_files['vibe.meta.json'] = json.dumps(vibe_meta, indent=2)
        except json.JSONDecodeError:
            pass
    
    return current_files, False, max_iterations


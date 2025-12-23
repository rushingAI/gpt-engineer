# 导入导出一致性修复文档

## 问题描述

用户报告了两个关键问题：

### 问题 1: 依赖检测误判（层面1）
```bash
代码中使用了未批准的依赖: @vitejs/plugin-react
代码中使用了未批准的依赖: path
代码中使用了未批准的依赖: url
```

**根因分析**：
- `dependency_detector.py` 没有区分运行时依赖和开发依赖
- 没有过滤 Node.js 内置模块（如 `path`, `url`, `fs`）
- 配置文件（`vite.config.ts`）中的导入也被检测

### 问题 2: 导出名称不一致（层面2）
```bash
Uncaught SyntaxError: The requested module '/src/lib/generated/dashboard-orders.ts' 
does not provide an export named 'computeOrderStats' (at Index.tsx:8:3)
```

**根因分析**：
- AI 在自愈时修改了 `dashboard-orders.ts` 的导出名称（`getOrderStats`）
- 但没有同步更新 `Index.tsx` 中的导入（`computeOrderStats`）
- 缺少静态检查来捕获这类不匹配

---

## 解决方案

### 层面1: 完善依赖检测过滤逻辑

#### 修改文件: `dependency_detector.py`

**1. 新增过滤集合**

```python
# Node.js 内置模块（不需要安装）
NODEJS_BUILTIN_MODULES = {
    'assert', 'buffer', 'child_process', 'cluster', 'console', 'constants',
    'crypto', 'dgram', 'dns', 'domain', 'events', 'fs', 'http', 'http2',
    'https', 'inspector', 'module', 'net', 'os', 'path', 'perf_hooks',
    'process', 'punycode', 'querystring', 'readline', 'repl', 'stream',
    'string_decoder', 'timers', 'tls', 'trace_events', 'tty', 'url',
    'util', 'v8', 'vm', 'wasi', 'worker_threads', 'zlib'
}  # 共 39 个

# 开发依赖（构建时依赖，运行时不需要）
DEV_DEPENDENCIES = {
    'vite',
    '@vitejs/plugin-react',
    '@vitejs/plugin-react-swc',
    'typescript',
    'eslint',
    'eslint-plugin-react',
    'eslint-plugin-react-hooks',
    'eslint-plugin-react-refresh',
    'prettier',
    'autoprefixer',
    'postcss',
    'tailwindcss',
    'tailwindcss-animate',
    '@types/node',
    '@types/react',
    '@types/react-dom',
    'vite-plugin-pwa',
}  # 共 17 个
```

**2. 更新检测逻辑**

```python
def detect_dependencies_in_files(files: Dict[str, str]) -> Dict[str, str]:
    all_imports = set()
    
    # 配置文件列表（不检测这些文件中的导入）
    config_file_patterns = ['vite.config', 'tailwind.config', 'postcss.config', 'eslint.config']
    
    for filename, content in files.items():
        # 跳过配置文件
        if any(pattern in filename for pattern in config_file_patterns):
            continue
            
        if filename.endswith(('.tsx', '.ts', '.jsx', '.js')):
            imports = detect_imports_in_code(content)
            all_imports.update(imports)
    
    # 三层过滤
    third_party_imports = all_imports - PRESET_PACKAGES
    third_party_imports = third_party_imports - NODEJS_BUILTIN_MODULES
    third_party_imports = third_party_imports - DEV_DEPENDENCIES
    
    # 映射到白名单中的依赖
    missing_deps = {}
    for package in third_party_imports:
        if package in KNOWN_PACKAGES:
            missing_deps[package] = KNOWN_PACKAGES[package]
    
    return missing_deps
```

---

### 层面2: 导入导出一致性检测

#### 修改文件: `quality_gates.py`

**新增检查方法: `_check_import_export_consistency`**

该方法实现以下逻辑：

1. **解析所有文件的导出**：使用正则提取 `export function/const/type` 等
2. **解析 Index.tsx 的导入**：提取所有从 `@/` 开头的内部导入
3. **匹配检查**：验证导入的名称是否在对应文件中导出
4. **智能建议**：如果发现相似的导出名（如 `getOrderStats` vs `computeOrderStats`），提供修复建议

**关键功能**：

```python
def _check_import_export_consistency(self, files: Dict[str, str]) -> List[Dict[str, Any]]:
    """检查导入和导出的一致性"""
    
    # 1. 提取所有导出
    exports_map = {}
    for filename, content in files.items():
        if filename.endswith(('.tsx', '.ts', '.jsx', '.js')):
            exports = self._extract_exports(content)  # 解析 export 语句
            if exports:
                exports_map[filename] = exports
    
    # 2. 检查 Index.tsx 的导入
    index_file = 'src/pages/Index.tsx'
    if index_file not in files:
        return []
    
    imports = self._extract_named_imports_with_source(files[index_file])
    
    # 3. 验证每个导入
    for imported_name, source_path in imports:
        if not source_path.startswith('@/'):
            continue
        
        actual_path = self._resolve_import_path(source_path)  # @/lib/xxx -> src/lib/xxx.ts
        
        if actual_path and actual_path in exports_map:
            exported_names = exports_map[actual_path]
            
            if imported_name not in exported_names:
                # 查找相似的导出（智能建议）
                similar = self._find_similar_export(imported_name, exported_names)
                
                if similar:
                    suggestion = f"导出的是 '{similar}'，请改名或添加别名：export {{ {similar} as {imported_name} }}"
                else:
                    suggestion = f"没有导出 '{imported_name}'，请检查导出名称"
                
                issues.append({
                    'rule_id': 'import_export_mismatch',
                    'severity': 'error',
                    'file': index_file,
                    'message': f"导入的 '{imported_name}' 在 '{actual_path}' 中不存在",
                    'suggestion': suggestion
                })
    
    return issues
```

**相似导出匹配算法**：

```python
def _find_similar_export(self, imported_name: str, exported_names: set) -> str:
    """查找相似的导出名（可能只是命名差异）"""
    
    best_match = None
    best_score = 0
    
    for exported in exported_names:
        score = 0
        
        # 子串匹配
        if imported_name.lower() in exported.lower():
            score = len(imported_name) * 2
        
        # 关键词匹配（如 compute, Order, Stats）
        imported_words = set(re.findall(r'[A-Z][a-z]+|[a-z]+', imported_name))
        exported_words = set(re.findall(r'[A-Z][a-z]+|[a-z]+', exported))
        common_words = imported_words & exported_words
        
        if len(common_words) >= 2:  # 至少2个相同的词
            score += len(common_words) * 10
        
        if score > best_score:
            best_score = score
            best_match = exported
    
    # 只返回足够相似的匹配（score > 15）
    return best_match if best_score > 15 else None
```

#### 修改文件: `prompt_fragments.py`

**新增 BASE RULE**：

```python
"MUST keep export names consistent: if Index.tsx imports 'computeOrderStats', 
export 'computeOrderStats', NOT 'getOrderStats'. Keep naming consistent across all files"
```

**新增动态规则**：

```python
(
    "import_export_consistency",
    {
        "gate_codes": ["import_export_mismatch"],
    },
    "CRITICAL: Export names in src/lib/generated/ MUST match Index.tsx imports. 
    If error shows 'computeOrderStats not exported', check what Index.tsx imports 
    and export exactly that name. DO NOT rename exports without updating ALL imports."
)
```

---

## 修复效果

### ✅ 层面1: 依赖过滤优化

| 类型 | 数量 | 效果 |
|------|------|------|
| Node.js 内置模块 | 39 个 | 不再误报为第三方依赖 |
| 开发依赖 | 17 个 | 不再触发运行时检查 |
| 配置文件 | 4 类 | 跳过导入检测 |

**示例**：
- `import path from 'path'` → ✅ 不再报错
- `import { defineConfig } from 'vite'` (in vite.config.ts) → ✅ 跳过检测
- `import axios from 'axios'` → ⚠️ 仍需仲裁（正确行为）

### ✅ 层面2: 导入导出一致性

| 场景 | 检测能力 | 修复建议 |
|------|---------|---------|
| 完全不匹配 | ✅ | 提示缺少导出 |
| 相似名称不匹配 | ✅ | 建议改名或添加别名 |
| 类型导入 | ✅ | 自动跳过（不检查类型） |
| 正确的导入导出 | ✅ | 不误报 |

**示例**：

```typescript
// Index.tsx
import { computeOrderStats } from '@/lib/generated/orders';

// orders.ts
export function getOrderStats() { ... }  // ❌ 名称不匹配

// 门禁报错：
// 导入的 'computeOrderStats' 在 'src/lib/generated/orders.ts' 中不存在
// 建议: 导出的是 'getOrderStats'，请改名或添加别名：
//       export { getOrderStats as computeOrderStats }
```

---

## 测试验证

### 测试文件: `test_import_export_consistency.py`

包含 6 个测试用例：

1. ✅ **test_nodejs_builtin_filtering**: Node.js 内置模块过滤
2. ✅ **test_dev_dependencies_filtering**: 开发依赖过滤
3. ✅ **test_config_file_skipping**: 配置文件跳过
4. ✅ **test_import_export_mismatch_detection**: 导入导出不匹配检测
5. ✅ **test_similar_export_suggestion**: 相似导出建议
6. ✅ **test_correct_import_export**: 正确的导入导出（不误报）

**运行测试**：

```bash
cd backend
python3 test_import_export_consistency.py
```

**测试结果**：

```
🎉 所有测试通过！两层面修复都工作正常。

💡 修复效果:
  ✓ 层面1: Node.js 内置模块 (39 个) 和开发依赖 (17 个) 正确过滤
  ✓ 层面2: 导入导出不匹配能正确检测并提供修复建议
```

---

## 设计思想

### 1. 分层防御策略

```
┌─────────────────────────────────────────┐
│ 层面1: 检测阶段（dependency_detector）   │
│ - 过滤 Node.js 内置模块                 │
│ - 过滤开发依赖                          │
│ - 跳过配置文件                          │
│ 目标: 减少噪音，只检测真正的运行时依赖    │
└─────────────────────────────────────────┘
                 ↓
┌─────────────────────────────────────────┐
│ 层面2: 质量门禁（quality_gates）         │
│ - 方案A: 静态检查（import/export 匹配）  │
│ - 方案C: Prompt 规则（生成阶段约束）     │
│ 目标: 确保代码生成时就保持一致性         │
└─────────────────────────────────────────┘
                 ↓
┌─────────────────────────────────────────┐
│ 层面3: 自愈修复（self_heal）             │
│ - 动态规则注入（import_export_consistency）│
│ - 智能建议（相似导出匹配）               │
│ 目标: 失败时提供精准修复指导             │
└─────────────────────────────────────────┘
```

### 2. 泛化设计原则

| 原则 | 实现方式 |
|------|---------|
| **可扩展性** | 集合配置（NODEJS_BUILTIN_MODULES, DEV_DEPENDENCIES）易于维护 |
| **智能匹配** | 基于词法分析的相似度算法，不仅限于精确匹配 |
| **渐进式检查** | 先过滤噪音（层面1），再精确检测（层面2），最后自愈（层面3） |
| **零误报** | 类型导入自动跳过，正确的代码不会触发告警 |

### 3. 与现有系统集成

- ✅ 复用 `PRESET_DEPENDENCIES` 优化（已有 30+ 预设依赖）
- ✅ 兼容 `DEPENDENCY_WHITELIST`（shadcn/Radix UI 已支持）
- ✅ 集成到现有的自愈流程（`self_heal.py`）
- ✅ 支持动态规则注入（`prompt_fragments.py`）

---

## 相关文档

- [API_USAGE_GUIDE_SYSTEM.md](./API_USAGE_GUIDE_SYSTEM.md) - API 使用指导系统
- [PRESET_DEPENDENCIES_OPTIMIZATION.md](./PRESET_DEPENDENCIES_OPTIMIZATION.md) - 预设依赖优化
- [SHADCN_DEPENDENCIES_WHITELIST.md](./SHADCN_DEPENDENCIES_WHITELIST.md) - Shadcn 依赖白名单
- [VIBE_META_FIX.md](./VIBE_META_FIX.md) - vibe.meta.json 时序修复

---

## 变更摘要

### 修改的文件

1. **`dependency_detector.py`**
   - 新增 `NODEJS_BUILTIN_MODULES` (39 个)
   - 新增 `DEV_DEPENDENCIES` (17 个)
   - 更新 `detect_dependencies_in_files()` 逻辑
   - 新增配置文件跳过功能

2. **`quality_gates.py`**
   - **依赖检测部分**: 更新 `_check_dependency_consistency()` 导入过滤逻辑，同步使用三层过滤
   - **导入导出检测**: 新增 `_check_import_export_consistency()` 方法
   - **辅助函数**: 
     - `_extract_exports()` - 解析导出
     - `_extract_named_imports_with_source()` - 解析导入
     - `_resolve_import_path()` - 路径解析
     - `_find_similar_export()` - 智能匹配算法
     - `_find_import_line()` - 行号定位

3. **`prompt_fragments.py`**
   - BASE RULES 新增导出一致性规则
   - 动态规则新增 `import_export_consistency` 触发器

4. **测试文件** (新建)
   - `test_import_export_consistency.py` - 6 个综合测试用例
   - `test_dependency_gate.py` - 依赖门禁专项测试
   - `test_real_case.py` - 真实用户案例验证

---

## 后续优化建议

1. **扩展检测范围**: 目前只检查 `Index.tsx`，未来可扩展到所有文件间的导入导出
2. **性能优化**: 对于大型项目，可以缓存导出映射
3. **更精确的匹配**: 引入编辑距离算法（Levenshtein）提升相似度计算
4. **IDE 集成**: 考虑生成 `.d.ts` 类型声明，让 IDE 也能提前发现问题

---

**创建时间**: 2025-12-22  
**版本**: v1.0  
**状态**: ✅ 已完成并测试通过


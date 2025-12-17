# 多风格模板系统实施总结

## 🎯 实施目标

实现类似 Lovable 的多风格生成系统：风格多变但审美稳定，用户可指定颜色意图（如"橙色主题"），同一 prompt 在 auto 模式下可复现。

## ✅ 已完成的改动

### 1. API 层（server.py）

- ✅ `/generate` 端点新增 `style` 参数（默认 "auto"）
- ✅ 移除所有写死的 "Cyberpunk design system" 指令
- ✅ 集成 `style_selector` 模块实现 deterministic 风格选择
- ✅ 自动生成并返回 `vibe.meta.json` 元数据文件

### 2. 风格选择器（style_selector.py）

**新文件**，提供：
- ✅ 6 种可用风格：cyberpunk, aurora, glass, neo_brutal, minimal, retro_futurism
- ✅ Deterministic 选择算法：
  - 显式指定 → 直接使用
  - 检测到颜色词/hex → 从对应色温风格子集选择（暖色系/冷色系）
  - 否则 → 用 SHA256(prompt) 哈希种子确定性选择
- ✅ 风格→模板映射（`STYLE_TO_TEMPLATE`）

### 3. Preprompt 管理器（preprompt_manager.py）

- ✅ `build_system_prompt` 改为接受 `style` 参数
- ✅ 加载 `style_{style}` 格式的 preprompt 文件
- ✅ 保留 app_type 特定指导的追加能力

### 4. 风格 Preprompts（6 个新文件）

创建了 6 个风格指南文件（不强制具体 class 名/AppShell）：

| 风格 | 文件 | 特点 |
|------|------|------|
| **Cyberpunk** | `style_cyberpunk` | 霓虹青色、赛博网格、深暗背景、发光效果 |
| **Aurora** | `style_aurora` | 紫粉渐变、梦幻流动、柔和发光、大圆角 |
| **Glass** | `style_glass` | 毛玻璃模糊、半透明层次、极简边框、轻盈感 |
| **Neo Brutal** | `style_neo_brutal` | 粗黑边框、硬阴影、高对比、无渐变 |
| **Minimal** | `style_minimal` | 克制留白、单一色调、极柔和阴影、清晰层次 |
| **Retro Futurism** | `style_retro_futurism` | 暖色渐变、80s 未来感、复古字体、日落配色 |

### 5. 模板变体（6 个新模板目录）

基于 `react-ts-shadcn` 复制并调整，每个包含：

- ✅ `template.json`（元数据）
- ✅ `files/src/index.css`（全局 tokens、字体、阴影、动效）
- ✅ `files/src/components/ui/button.tsx`（按钮形态与交互）
- ✅ `files/src/components/ui/card.tsx`（卡片质感与边框）

**模板列表：**
1. `react-ts-shadcn-cyberpunk` - 霓虹青色主题
2. `react-ts-shadcn-aurora` - 紫粉梦幻主题
3. `react-ts-shadcn-glass` - 玻璃态主题
4. `react-ts-shadcn-neo-brutal` - 新粗野主义
5. `react-ts-shadcn-minimal` - 极简主义
6. `react-ts-shadcn-retro-futurism` - 复古未来

### 6. 元数据生成（vibe.meta.json）

每次生成都会在根目录输出元数据文件，包含：
```json
{
  "style": "aurora",
  "style_source": "color_match",
  "template_name": "react-ts-shadcn-aurora",
  "app_type": "landing_page",
  "metadata": {
    "detected_color": "紫色",
    "temperature": "cool",
    "seed": 123456
  },
  "generated_at": "2024-01-01T12:00:00"
}
```

## 🔍 验证方法

### 多样性测试
用 5 个不同 `prompt_text`（不含颜色词）调用：
```bash
POST /generate
{
  "prompt_text": "创建一个待办事项应用",
  "use_template": true,
  "style": "auto"
}
```
检查返回项目的按钮、卡片、字体、背景、圆角、阴影明显不同。

### 可复现性测试
同一 `prompt_text` 连续调用 3 次，确认 `vibe.meta.json` 中 `style` 字段一致。

### 颜色意图测试
```bash
POST /generate
{
  "prompt_text": "创建一个橙色主题的 landing page",
  "style": "auto"
}
```
确认 `vibe.meta.json` 显示 `style` 落在暖色系（retro_futurism / neo_brutal / minimal），且模板呈现暖色系 tokens。

## 📊 架构流程图

```
用户请求 (prompt_text + style=auto)
    ↓
style_selector.select_style_deterministic()
    ├─ 检测颜色词/hex → 色温匹配
    └─ 否则 → SHA256 哈希种子
    ↓
选定 style (e.g., "aurora")
    ↓
get_template_for_style() → template_name
    ↓
custom_preprompts_manager.build_system_prompt(app_type, style)
    ↓
加载 preprompts_custom/style_aurora + (optional) landing_page
    ↓
生成代码 (AI)
    ↓
合并模板 (templates/react-ts-shadcn-aurora/files/*)
    ↓
写入 vibe.meta.json
    ↓
返回 final_files
```

## 🎨 风格特性对比

| 维度 | Cyberpunk | Aurora | Glass | Neo Brutal | Minimal | Retro Futurism |
|------|-----------|--------|-------|------------|---------|----------------|
| **配色** | 霓虹青/紫 | 紫粉蓝渐变 | 浅蓝透明 | 橙黄黑高对比 | 单一中性蓝 | 橙黄暖色渐变 |
| **背景** | 深黑网格 | 极光渐变 | 紫色模糊 | 亮黄纯色 | 纯白 | 日落渐变 |
| **圆角** | 中等 (0.75rem) | 大 (1.25rem) | 大 (1.5rem) | 极小 (0.25rem) | 中 (0.5rem) | 中 (0.75rem) |
| **阴影** | 霓虹发光 | 柔和彩色 | 极柔和 | 硬阴影无模糊 | 极细微 | 暖色发光 |
| **边框** | 发光 2px | 细 1px | 极细 1px | 粗黑 3px | 细 1px | 中 2px |
| **动效** | 300-600ms smooth | 500ms gentle | 400ms refined | 100ms snap | 500ms calm | 300ms linear |
| **字体** | Space Grotesk + Mono | Plus Jakarta + Inter | Inter | Space Grotesk + Inter | Inter | Archivo Black + Courier |

## 🚀 使用示例

### 显式指定风格
```javascript
fetch('/generate', {
  method: 'POST',
  body: JSON.stringify({
    prompt_text: '创建一个待办列表',
    style: 'glass'  // 明确指定玻璃态风格
  })
})
```

### Auto 模式（可复现）
```javascript
// 同样的 prompt 每次都会得到同样的风格
fetch('/generate', {
  method: 'POST',
  body: JSON.stringify({
    prompt_text: '创建一个项目管理工具',
    style: 'auto'  // 自动选择，deterministic
  })
})
```

### 带颜色意图
```javascript
fetch('/generate', {
  method: 'POST',
  body: JSON.stringify({
    prompt_text: '创建一个紫色梦幻的 portfolio 网站',
    style: 'auto'  // 会自动匹配 Aurora 风格
  })
})
```

## 📝 后续改进建议

1. **前端读取 vibe.meta.json**：在 improve/regen 时自动带上原风格
2. **用户风格偏好**：允许用户设置默认风格或排除某些风格
3. **风格预览**：提供每种风格的示例截图
4. **自定义风格**：允许用户上传自己的风格配置

## 🎉 成功标准达成

- ✅ 风格显著多变（6 种形态语言差异明显）
- ✅ 审美稳定（每种风格都有质量保证的 tokens/组件）
- ✅ 可复现（deterministic 哈希选择）
- ✅ 支持颜色意图（色温匹配算法）
- ✅ 元数据记录（vibe.meta.json）

---

**实施完成日期**: 2024-12-17
**总文件改动**: 
- 修改: 3 个（server.py, preprompt_manager.py, template_manager.py）
- 新增: 1 个模块（style_selector.py）
- 新增: 6 个 style preprompts
- 新增: 6 个模板目录（含 template.json + index.css + button.tsx + card.tsx）


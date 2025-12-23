// API 调用封装

const API_URL = 'http://localhost:8000'

/**
 * 生成应用
 * 
 * @param {string} prompt - 用户输入的提示词
 * @param {boolean} useTemplate - 是否使用模板模式（默认 true）
 */
export async function generateApp(prompt, useTemplate = true) {
  // 根据模式决定是否增强 prompt
  const finalPrompt = useTemplate ? prompt : buildEnhancedPrompt(prompt)
  
  const response = await fetch(`${API_URL}/generate`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ 
      prompt_text: finalPrompt,
      use_template: useTemplate
    }),
  })
  
  if (!response.ok) {
    const errorData = await response.json()
    throw new Error(errorData.detail || '生成失败')
  }
  
  const generatedFiles = await response.json()
  
  // 根据模式处理文件
  if (useTemplate) {
    return processReactFiles(generatedFiles)
  } else {
    return processFiles(generatedFiles)
  }
}

/**
 * 流式生成应用 (SSE)
 * 
 * @param {string} prompt - 用户输入的提示词
 * @param {function} onEvent - 事件回调函数，接收 {type, ...} 事件对象
 * @param {boolean} useTemplate - 是否使用模板模式（默认 true）
 * @returns {Promise<object>} - 最终生成的文件
 */
export async function generateAppStreaming(prompt, onEvent, useTemplate = true) {
  const finalPrompt = useTemplate ? prompt : buildEnhancedPrompt(prompt)
  
  const response = await fetch(`${API_URL}/generate-stream`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ 
      prompt_text: finalPrompt,
      use_template: useTemplate
    })
  })

  if (!response.ok) {
    throw new Error(`HTTP ${response.status}: ${response.statusText}`)
  }

  const reader = response.body.getReader()
  const decoder = new TextDecoder()
  let buffer = ''
  let finalFiles = null

  try {
    while (true) {
      const { done, value } = await reader.read()
      
      if (done) break

      buffer += decoder.decode(value, { stream: true })
      const lines = buffer.split('\n\n')
      buffer = lines.pop() || '' // 保留不完整的行

      for (const line of lines) {
        if (line.startsWith('data: ')) {
          try {
            const data = JSON.parse(line.slice(6))
            onEvent(data)
            
            if (data.type === 'complete') {
              finalFiles = useTemplate 
                ? processReactFiles(data.files)
                : processFiles(data.files)
            }
          } catch (err) {
            console.error('解析 SSE 数据失败:', err, line)
          }
        }
      }
    }
  } finally {
    reader.releaseLock()
  }

  return finalFiles
}

/**
 * 流式改进应用 (SSE)
 * 
 * @param {string} prompt - 改进要求
 * @param {object} currentFiles - 当前文件
 * @param {function} onEvent - 事件回调函数
 * @returns {Promise<object>} - 改进后的文件
 */
export async function improveAppStreaming(prompt, currentFiles, onEvent) {
  const response = await fetch(`${API_URL}/improve-stream`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      files: currentFiles,
      improvement_request: prompt
    })
  })

  if (!response.ok) {
    throw new Error(`HTTP ${response.status}: ${response.statusText}`)
  }

  const reader = response.body.getReader()
  const decoder = new TextDecoder()
  let buffer = ''
  let finalFiles = null

  try {
    while (true) {
      const { done, value } = await reader.read()
      
      if (done) break

      buffer += decoder.decode(value, { stream: true })
      const lines = buffer.split('\n\n')
      buffer = lines.pop() || ''

      for (const line of lines) {
        if (line.startsWith('data: ')) {
          try {
            const data = JSON.parse(line.slice(6))
            onEvent(data)
            
            if (data.type === 'complete') {
              finalFiles = processReactFiles(data.files)
            }
          } catch (err) {
            console.error('解析 SSE 数据失败:', err, line)
          }
        }
      }
    }
  } finally {
    reader.releaseLock()
  }

  return finalFiles
}

/**
 * 改进应用（非流式，兼容旧代码）
 */
export async function improveApp(prompt, currentFiles) {
  const response = await fetch(`${API_URL}/improve`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      files: currentFiles,
      improvement_request: prompt
    }),
  })
  
  if (!response.ok) {
    const errorData = await response.json()
    throw new Error(errorData.detail || '改进失败')
  }
  
  const improvedFiles = await response.json()
  return processFiles(improvedFiles)
}

/**
 * 构建增强的 prompt
 */
function buildEnhancedPrompt(prompt) {
  return `请创建一个现代化的单文件 HTML Web 应用，使用 Tailwind CSS CDN。

技术要求：
- 创建一个 index.html 文件
- 在 <head> 中通过 CDN 引入 Tailwind CSS：
  <script src="https://cdn.tailwindcss.com"></script>
- 使用原生 JavaScript（不使用构建工具）
- 如果需要图标，使用 Heroicons 或 Unicode 符号
- 如果需要数据持久化，使用 localStorage
- 所有代码（HTML + CSS + JS）都写在一个 index.html 文件中

重要限制（必须遵守）：
- ❌ 不要生成 package.json、tailwind.config.js、postcss.config.js 等配置文件（环境已配置）
- ❌ 不要生成 index.js、index.css 等入口文件（已存在）
- ✅ 只生成 index.html 文件
- ✅ Tailwind 类名直接写在 HTML 元素的 class 属性中

localStorage 使用要求（重要！）：
1. **初始化时加载**：页面加载时从 localStorage 读取数据
   let data = JSON.parse(localStorage.getItem('key')) || [];
   
2. **修改时保存**：每次增删改操作后立即保存
   localStorage.setItem('key', JSON.stringify(data));
   
3. **计算时使用全部数据**：统计数字时遍历**完整数组**，不要只统计显示的部分
   // ✅ 正确：统计所有数据
   data.forEach(item => total += item.amount);
   // ❌ 错误：只统计最后 10 条
   data.slice(-10).forEach(item => total += item.amount);
   
4. **显示时可以限制数量**：UI 上可以只显示最近 N 条
   data.slice(-10).forEach(item => renderItem(item));

设计要求（严格遵守！）：
1. **外层容器**：必须使用渐变背景
   class="min-h-screen bg-gradient-to-br from-blue-500 via-purple-500 to-pink-500 p-8"
   
2. **卡片样式**（用于所有内容块）：
   class="bg-white rounded-2xl shadow-2xl p-6 hover:shadow-3xl hover:scale-105 transition-all duration-300"
   
3. **按钮样式**：
   class="bg-blue-600 hover:bg-blue-700 text-white px-6 py-3 rounded-xl shadow-lg transition-all"
   
4. **标题**：
   class="text-4xl md:text-5xl font-bold text-white mb-8"
   
5. **数据展示**：
   - 数字使用超大字号：text-5xl font-bold
   - 标签使用中等字号：text-lg text-gray-600
   
6. **布局**：
   - 使用 grid 或 flex 布局
   - 间距统一使用 gap-6 或 space-y-6
   - 响应式：grid-cols-1 md:grid-cols-2 lg:grid-cols-4

7. **配色**：
   - 蓝色系：blue-500, blue-600, blue-700
   - 紫色系：purple-500, purple-600
   - 绿色系：green-500, emerald-600
   - 橙色系：orange-500, amber-600

参考这个示例风格（必须使用类似的丰富样式）：
<div class="min-h-screen bg-gradient-to-br from-indigo-600 via-purple-600 to-pink-500 p-8">
  <div class="max-w-7xl mx-auto">
    <h1 class="text-5xl font-bold text-white mb-8">Dashboard</h1>
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
      <div class="bg-white rounded-2xl shadow-2xl p-6 hover:scale-105 transition-all">
        <!-- 内容 -->
      </div>
    </div>
  </div>
</div>

用户需求：${prompt}

请只生成 index.html 文件，包含完整的 HTML、CSS 和 JavaScript 代码！确保使用上述所有设计元素！`
}

/**
 * 处理 React 项目文件（模板模式）
 */
function processReactFiles(generatedFiles) {
  const sandpackFiles = {}
  
  console.log('处理 React 项目文件...')
  console.log('接收到的文件:', Object.keys(generatedFiles))
  
  for (const [filename, content] of Object.entries(generatedFiles)) {
    // 为 Sandpack 格式化文件路径
    let cleanFilename = filename
    
    // 确保以 / 开头
    if (!cleanFilename.startsWith('/')) {
      cleanFilename = `/${cleanFilename}`
    }
    
    sandpackFiles[cleanFilename] = content
  }
  
  console.log('处理后的文件:', Object.keys(sandpackFiles))
  console.log('文件数量:', Object.keys(sandpackFiles).length)
  
  return sandpackFiles
}

/**
 * 处理传统单文件 HTML（传统模式）
 */
function processFiles(generatedFiles) {
  const sandpackFiles = {}
  
  for (const [filename, content] of Object.entries(generatedFiles)) {
    // 跳过非代码文件和配置文件
    const skipFiles = [
      '.txt', '.md', '.py',
      'package.json', 'package-lock.json',
      'tailwind.config.js', 'postcss.config.js',
      'index.css', 'styles.css',
      'vite.config.js', 'tsconfig.json',
    ]
    
    if (skipFiles.some(skip => filename.endsWith(skip) || filename.includes(skip))) {
      console.log(`跳过配置文件: ${filename}`)
      continue
    }
    
    // 移除 src/ 目录前缀
    let cleanFilename = filename.replace(/^src\//, '/')
    
    // 确保文件名以 / 开头
    if (!cleanFilename.startsWith('/')) {
      cleanFilename = `/${cleanFilename}`
    }
    
    // 跳过 index.js/index.jsx
    if (cleanFilename === '/index.js' || cleanFilename === '/index.jsx') {
      console.log(`跳过入口文件: ${filename}`)
      continue
    }
    
    sandpackFiles[cleanFilename] = content
  }
  
  // 确保有 index.html
  if (!sandpackFiles['/index.html']) {
    const possibleHtmlFiles = Object.keys(sandpackFiles).filter(f => f.endsWith('.html'))
    if (possibleHtmlFiles.length > 0) {
      console.log(`重命名 ${possibleHtmlFiles[0]} -> /index.html`)
      sandpackFiles['/index.html'] = sandpackFiles[possibleHtmlFiles[0]]
      if (possibleHtmlFiles[0] !== '/index.html') {
        delete sandpackFiles[possibleHtmlFiles[0]]
      }
    }
  }
  
  // 验证 Tailwind CDN
  if (sandpackFiles['/index.html']) {
    if (sandpackFiles['/index.html'].includes('cdn.tailwindcss.com')) {
      console.log('✓ 检测到 Tailwind CDN')
    } else {
      console.warn('⚠️ 未检测到 Tailwind CDN')
    }
  }
  
  return sandpackFiles
}


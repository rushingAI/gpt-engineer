import { useState, useEffect } from 'react'
import { Sandpack } from '@codesandbox/sandpack-react'
import './App.css'

const API_URL = 'http://localhost:8000'
const STORAGE_KEY = 'vibecodingplatform_current_app'
const HISTORY_KEY = 'vibecodingplatform_history'
const MAX_HISTORY = 10

function App() {
  const [prompt, setPrompt] = useState('')
  const [loading, setLoading] = useState(false)
  const [files, setFiles] = useState(null)
  const [error, setError] = useState(null)
  const [showImprove, setShowImprove] = useState(false)
  const [improveRequest, setImproveRequest] = useState('')
  const [savedApp, setSavedApp] = useState(null)
  const [history, setHistory] = useState([])
  const [showHistory, setShowHistory] = useState(false)
  const [editingNameId, setEditingNameId] = useState(null)
  const [editingName, setEditingName] = useState('')

  // 页面加载时恢复上次生成的应用和历史记录
  useEffect(() => {
    // 恢复当前应用
    const saved = localStorage.getItem(STORAGE_KEY)
    if (saved) {
      try {
        const { files: savedFiles, prompt: savedPrompt, timestamp } = JSON.parse(saved)
        setFiles(savedFiles)
        setPrompt(savedPrompt)
        setSavedApp({ timestamp })
        console.log('✓ 已恢复上次生成的应用:', savedPrompt)
      } catch (e) {
        console.error('恢复应用失败:', e)
        localStorage.removeItem(STORAGE_KEY)
      }
    }

    // 加载历史记录
    const savedHistory = localStorage.getItem(HISTORY_KEY)
    if (savedHistory) {
      try {
        const historyData = JSON.parse(savedHistory)
        setHistory(historyData)
        console.log('✓ 已加载历史记录:', historyData.length, '个应用')
      } catch (e) {
        console.error('加载历史记录失败:', e)
        localStorage.removeItem(HISTORY_KEY)
      }
    }
  }, [])

  const handleGenerate = async () => {
    if (!prompt.trim()) {
      alert('请输入提示词')
      return
    }

    setLoading(true)
    setError(null)

    try {
      console.log('发送生成请求:', prompt)
      
      // 重要：引导 AI 生成带内联样式的 HTML + Tailwind CDN
      const enhancedPrompt = `请创建一个现代化的单文件 HTML Web 应用，使用 Tailwind CSS CDN。

技术要求：
- 创建一个 index.html 文件
- 在 <head> 中通过 CDN 引入 Tailwind CSS：
  <script src="https://cdn.tailwindcss.com"></script>
- 使用原生 JavaScript（不使用构建工具）
- 如果需要图标，使用 Heroicons 或 Unicode 符号
- 如果需要数据持久化，使用 localStorage
- 所有代码（HTML + CSS + JS）都写在一个 index.html 文件中

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
   
2. **卡片样式**：
   class="bg-white rounded-2xl shadow-2xl p-6 hover:shadow-3xl hover:scale-105 transition-all duration-300"
   
3. **按钮样式**：
   class="bg-blue-600 hover:bg-blue-700 text-white px-6 py-3 rounded-xl shadow-lg transition-all"
   
4. **标题**：
   class="text-4xl md:text-5xl font-bold text-white mb-8"
   
5. **数据展示**：
   - 数字使用超大字号：text-5xl font-bold
   - 标签使用中等字号：text-lg text-gray-600
   
6. **布局**：使用 grid布局，响应式断点

参考示例：
<!DOCTYPE html>
<html>
<head>
  <script src="https://cdn.tailwindcss.com"></script>
</head>
<body>
  <div class="min-h-screen bg-gradient-to-br from-indigo-600 via-purple-600 to-pink-500 p-8">
    <div class="max-w-7xl mx-auto">
      <h1 class="text-5xl font-bold text-white mb-8">标题</h1>
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <div class="bg-white rounded-2xl shadow-2xl p-6 hover:scale-105 transition-all">
          <!-- 内容 -->
        </div>
      </div>
    </div>
  </div>
</body>
</html>

用户需求：${prompt}

请只生成 index.html 文件，包含完整的 HTML、CSS 和 JavaScript 代码！`
      
      const response = await fetch(`${API_URL}/generate`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ prompt_text: enhancedPrompt }),
      })

      if (!response.ok) {
        const errorData = await response.json()
        throw new Error(errorData.detail || '生成失败')
      }

      const generatedFiles = await response.json()
      console.log('生成的文件:', Object.keys(generatedFiles))
      console.log('文件内容预览:', generatedFiles)
      
      // 转换文件格式以适配 Sandpack React 模板
      const sandpackFiles = {}
      for (const [filename, content] of Object.entries(generatedFiles)) {
        // 跳过非代码文件和配置文件（Sandpack 不需要这些）
        const skipFiles = [
          '.txt', '.md', '.py',  // 非代码文件
          'package.json', 'package-lock.json',  // Sandpack 有自己的依赖管理
          'tailwind.config.js', 'postcss.config.js',  // Sandpack 预配置了 Tailwind
          'index.css', 'styles.css',  // @tailwind 指令在 Sandpack 中不工作
          'vite.config.js', 'tsconfig.json',  // 构建配置
        ]
        
        if (skipFiles.some(skip => filename.endsWith(skip) || filename.includes(skip))) {
          console.log(`跳过配置文件: ${filename}`)
          continue
        }
        
        // 移除 src/ 目录前缀，Sandpack 不需要
        let cleanFilename = filename.replace(/^src\//, '/')
        
        // 确保文件名以 / 开头
        if (!cleanFilename.startsWith('/')) {
          cleanFilename = `/${cleanFilename}`
        }
        
        // 跳过 index.js/index.jsx（Sandpack 的 React 模板已经有了）
        if (cleanFilename === '/index.js' || cleanFilename === '/index.jsx') {
          console.log(`跳过入口文件: ${filename}（Sandpack 已内置）`)
          continue
        }
        
        sandpackFiles[cleanFilename] = content
      }
      
      console.log('转换后的文件:', Object.keys(sandpackFiles))
      console.log('文件详情:', sandpackFiles) // 查看完整文件内容
      
      // 检查是否有有效的文件
      if (Object.keys(sandpackFiles).length === 0) {
        throw new Error('AI 生成的代码不包含可预览的 Web 文件')
      }
      
      // 调试：检查 App.jsx 的内容
      if (sandpackFiles['/App.jsx']) {
        console.log('App.jsx 内容长度:', sandpackFiles['/App.jsx'].length)
        console.log('App.jsx 前100字符:', sandpackFiles['/App.jsx'].substring(0, 100))
      }
      
      // Static 模板需要 index.html 作为入口
      // 如果 AI 生成了其他名称，重命名为 index.html
      if (!sandpackFiles['/index.html']) {
        // 查找可能的主HTML文件
        const possibleHtmlFiles = Object.keys(sandpackFiles).filter(f => f.endsWith('.html'))
        if (possibleHtmlFiles.length > 0) {
          console.log(`重命名 ${possibleHtmlFiles[0]} -> /index.html`)
          sandpackFiles['/index.html'] = sandpackFiles[possibleHtmlFiles[0]]
          if (possibleHtmlFiles[0] !== '/index.html') {
            delete sandpackFiles[possibleHtmlFiles[0]]
          }
        }
      }
      
      // 最后确认
      console.log('最终传递给 Sandpack 的文件:', Object.keys(sandpackFiles))
      if (sandpackFiles['/index.html']) {
        console.log('✓ 找到 index.html，内容长度:', sandpackFiles['/index.html'].length)
        // 检查是否包含 Tailwind CDN
        if (sandpackFiles['/index.html'].includes('cdn.tailwindcss.com')) {
          console.log('✓ 检测到 Tailwind CDN，样式应该能正常显示')
        } else {
          console.warn('⚠️ 警告：未检测到 Tailwind CDN！')
        }
      } else {
        console.warn('⚠️ 警告：没有找到 index.html！')
        console.warn('可用的文件:', Object.keys(sandpackFiles))
      }
      
      console.log('传递给 Sandpack 的最终文件列表:', Object.keys(sandpackFiles))
      setFiles(sandpackFiles)
      
      // 保存到当前应用和历史记录
      const appData = {
        id: Date.now().toString(),
        files: sandpackFiles,
        prompt: prompt,
        name: extractAppName(prompt),
        timestamp: new Date().toISOString()
      }
      
      // 保存当前应用
      localStorage.setItem(STORAGE_KEY, JSON.stringify(appData))
      setSavedApp({ timestamp: appData.timestamp })
      
      // 添加到历史记录
      addToHistory(appData)
      console.log('✓ 应用已保存到 localStorage 和历史记录')
    } catch (err) {
      console.error('生成错误:', err)
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleGenerate()
    }
  }

  // 从 prompt 提取应用名称（前20个字符）
  const extractAppName = (prompt) => {
    const cleanPrompt = prompt.replace(/^(创建|生成|做|制作)(一个)?/g, '').trim()
    return cleanPrompt.substring(0, 20) + (cleanPrompt.length > 20 ? '...' : '')
  }

  // 添加到历史记录（最多保存10个）
  const addToHistory = (appData) => {
    const savedHistory = localStorage.getItem(HISTORY_KEY)
    let historyList = savedHistory ? JSON.parse(savedHistory) : []
    
    // 添加新应用到开头
    historyList.unshift(appData)
    
    // 只保留最近10个
    if (historyList.length > MAX_HISTORY) {
      historyList = historyList.slice(0, MAX_HISTORY)
    }
    
    localStorage.setItem(HISTORY_KEY, JSON.stringify(historyList))
    setHistory(historyList)
  }

  // 从历史记录加载应用
  const loadFromHistory = (item) => {
    setFiles(item.files)
    setPrompt(item.prompt)
    setSavedApp({ timestamp: item.timestamp })
    
    // 更新当前应用
    localStorage.setItem(STORAGE_KEY, JSON.stringify(item))
    
    setShowHistory(false)
    console.log('✓ 已从历史记录恢复应用:', item.name)
  }

  // 删除历史记录
  const deleteHistoryItem = (id, e) => {
    e.stopPropagation()
    if (confirm('确定要删除这个历史记录吗？')) {
      const newHistory = history.filter(item => item.id !== id)
      localStorage.setItem(HISTORY_KEY, JSON.stringify(newHistory))
      setHistory(newHistory)
      console.log('✓ 已删除历史记录')
    }
  }

  // 重命名应用
  const renameHistoryItem = (id, newName) => {
    const newHistory = history.map(item => 
      item.id === id ? { ...item, name: newName } : item
    )
    localStorage.setItem(HISTORY_KEY, JSON.stringify(newHistory))
    setHistory(newHistory)
    setEditingNameId(null)
    console.log('✓ 已重命名应用')
  }

  const handleClear = () => {
    if (confirm('确定要清除当前应用并开始新建吗？')) {
      setFiles(null)
      setPrompt('')
      setError(null)
      setSavedApp(null)
      setShowImprove(false)
      setImproveRequest('')
      localStorage.removeItem(STORAGE_KEY)
      console.log('✓ 已清除当前应用')
    }
  }

  const handleImprove = async () => {
    if (!improveRequest.trim()) {
      alert('请输入改进要求')
      return
    }

    setLoading(true)
    setError(null)

    try {
      console.log('发送改进请求:', improveRequest)
      
      const response = await fetch(`${API_URL}/improve`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          files: files,
          improvement_request: improveRequest
        }),
      })

      if (!response.ok) {
        const errorData = await response.json()
        throw new Error(errorData.detail || '改进失败')
      }

      const improvedFiles = await response.json()
      console.log('改进后的文件:', Object.keys(improvedFiles))
      
      // 使用相同的处理逻辑
      const sandpackFiles = {}
      for (const [filename, content] of Object.entries(improvedFiles)) {
        if (filename.endsWith('.txt') || filename.endsWith('.md') || filename === 'README') {
          continue
        }
        const normalizedFilename = filename.startsWith('/') ? filename : `/${filename}`
        sandpackFiles[normalizedFilename] = content
      }
      
      if (!sandpackFiles['/index.html']) {
        const firstHtmlFile = Object.keys(sandpackFiles).find(f => f.endsWith('.html'))
        if (firstHtmlFile) {
          sandpackFiles['/index.html'] = sandpackFiles[firstHtmlFile]
          delete sandpackFiles[firstHtmlFile]
        }
      }
      
      setFiles(sandpackFiles)
      setShowImprove(false)
      setImproveRequest('')
      
      // 保存到当前应用和历史记录
      const improvedPrompt = `${prompt} (改进: ${improveRequest})`
      const appData = {
        id: Date.now().toString(),
        files: sandpackFiles,
        prompt: improvedPrompt,
        name: extractAppName(prompt),
        timestamp: new Date().toISOString()
      }
      
      localStorage.setItem(STORAGE_KEY, JSON.stringify(appData))
      setSavedApp({ timestamp: appData.timestamp })
      setPrompt(improvedPrompt)
      
      // 添加到历史记录
      addToHistory(appData)
      console.log('✓ 改进后的应用已保存到 localStorage 和历史记录')
      
    } catch (err) {
      console.error('改进错误:', err)
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="app-container" style={{ display: 'flex', flexDirection: 'row' }}>
      {/* 历史记录侧边栏 */}
      {showHistory && (
        <div style={{
          width: '320px',
          backgroundColor: '#f8fafc',
          borderRight: '1px solid #e2e8f0',
          height: '100vh',
          overflowY: 'auto',
          padding: '20px',
          boxSizing: 'border-box'
        }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
            <h2 style={{ margin: 0, fontSize: '18px', fontWeight: 'bold' }}>📚 历史记录</h2>
            <button onClick={() => setShowHistory(false)} style={{
              background: 'none',
              border: 'none',
              fontSize: '20px',
              cursor: 'pointer',
              padding: '4px'
            }}>✕</button>
          </div>
          
          {history.length === 0 ? (
            <div style={{ textAlign: 'center', color: '#94a3b8', padding: '40px 20px' }}>
              暂无历史记录<br/>生成应用后会自动保存
            </div>
          ) : (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
              {history.map((item, index) => (
                <div
                  key={item.id}
                  onClick={() => loadFromHistory(item)}
                  style={{
                    backgroundColor: 'white',
                    padding: '12px',
                    borderRadius: '8px',
                    border: '1px solid #e2e8f0',
                    cursor: 'pointer',
                    transition: 'all 0.2s',
                    position: 'relative'
                  }}
                  onMouseEnter={(e) => e.currentTarget.style.boxShadow = '0 4px 12px rgba(0,0,0,0.1)'}
                  onMouseLeave={(e) => e.currentTarget.style.boxShadow = 'none'}
                >
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                    <div style={{ flex: 1, marginRight: '8px' }}>
                      {editingNameId === item.id ? (
                        <input
                          type="text"
                          value={editingName}
                          onChange={(e) => setEditingName(e.target.value)}
                          onBlur={() => renameHistoryItem(item.id, editingName)}
                          onKeyPress={(e) => {
                            if (e.key === 'Enter') {
                              renameHistoryItem(item.id, editingName)
                            }
                          }}
                          onClick={(e) => e.stopPropagation()}
                          autoFocus
                          style={{
                            width: '100%',
                            padding: '4px',
                            border: '1px solid #3b82f6',
                            borderRadius: '4px',
                            fontSize: '14px'
                          }}
                        />
                      ) : (
                        <div style={{ display: 'flex', alignItems: 'center', gap: '6px', marginBottom: '6px' }}>
                          <div
                            style={{
                              fontWeight: '600',
                              fontSize: '14px',
                              color: '#1e293b',
                              flex: 1
                            }}
                          >
                            {item.name}
                          </div>
                          <button
                            onClick={(e) => {
                              e.stopPropagation()
                              setEditingNameId(item.id)
                              setEditingName(item.name)
                            }}
                            style={{
                              background: 'none',
                              border: 'none',
                              color: '#3b82f6',
                              cursor: 'pointer',
                              fontSize: '16px',
                              padding: '2px',
                              lineHeight: 1,
                              display: 'flex',
                              alignItems: 'center'
                            }}
                            title="重命名"
                          >
                            ✏️
                          </button>
                        </div>
                      )}
                      <div style={{ fontSize: '12px', color: '#64748b' }}>
                        {new Date(item.timestamp).toLocaleString('zh-CN', {
                          month: 'numeric',
                          day: 'numeric',
                          hour: '2-digit',
                          minute: '2-digit'
                        })}
                      </div>
                    </div>
                    <button
                      onClick={(e) => deleteHistoryItem(item.id, e)}
                      style={{
                        background: 'none',
                        border: 'none',
                        color: '#ef4444',
                        cursor: 'pointer',
                        fontSize: '18px',
                        padding: '4px',
                        lineHeight: 1
                      }}
                      title="删除"
                    >
                      🗑️
                    </button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* 主内容区域 */}
      <div style={{ flex: 1, display: 'flex', flexDirection: 'column', minHeight: '100vh' }}>
        <header className="app-header">
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <div>
              <h1>🎨 Vibecoding Platform</h1>
              <p>用自然语言描述，AI 生成可运行的应用</p>
            </div>
            <button
              onClick={() => setShowHistory(!showHistory)}
              style={{
                padding: '10px 20px',
                backgroundColor: showHistory ? '#3b82f6' : '#6366f1',
                color: 'white',
                border: 'none',
                borderRadius: '8px',
                cursor: 'pointer',
                fontSize: '14px',
                display: 'flex',
                alignItems: 'center',
                gap: '6px'
              }}
            >
              📚 历史记录 ({history.length})
            </button>
          </div>
        </header>

      <div className="input-section">
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '8px' }}>
          {savedApp && (
            <div style={{ 
              fontSize: '14px', 
              color: '#10b981', 
              display: 'flex', 
              alignItems: 'center',
              gap: '6px'
            }}>
              <span>💾</span>
              <span>已保存 {new Date(savedApp.timestamp).toLocaleString('zh-CN')}</span>
            </div>
          )}
          {files && (
            <button 
              onClick={handleClear}
              disabled={loading}
              style={{
                marginLeft: 'auto',
                padding: '8px 16px',
                background: '#ef4444',
                color: 'white',
                border: 'none',
                borderRadius: '8px',
                cursor: loading ? 'not-allowed' : 'pointer',
                fontSize: '14px',
                opacity: loading ? 0.5 : 1
              }}
            >
              🗑️ 清除应用
            </button>
          )}
        </div>
        <textarea
          value={prompt}
          onChange={(e) => setPrompt(e.target.value)}
          onKeyPress={handleKeyPress}
          placeholder="描述你想要创建的应用... 例如：创建一个待办事项列表应用"
          disabled={loading}
          rows={3}
        />
        <button 
          onClick={handleGenerate} 
          disabled={loading || !prompt.trim()}
          className="generate-button"
        >
          {loading ? (
            <>
              <span className="spinner"></span>
              生成中...
            </>
          ) : (
            '✨ 生成应用'
          )}
        </button>
      </div>

      {error && (
        <div className="error-message">
          ❌ 错误: {error}
          <button onClick={() => setError(null)}>✕</button>
        </div>
      )}

      {loading && (
        <div className="loading-indicator">
          <div className="loading-content">
            <div className="loading-spinner"></div>
            <p>AI 正在为你编写代码...</p>
          </div>
        </div>
      )}

      {files && !loading && (
        <div className="preview-section">
          <div className="preview-header">
            <h2>📦 生成结果</h2>
            <div className="preview-actions">
              <div className="file-count">
                {Object.keys(files).length} 个文件
              </div>
              <button 
                className="improve-button"
                onClick={() => setShowImprove(!showImprove)}
              >
                {showImprove ? '✕ 取消' : '🔧 改进代码'}
              </button>
            </div>
          </div>
          
          {showImprove && (
            <div className="improve-section">
              <textarea
                value={improveRequest}
                onChange={(e) => setImproveRequest(e.target.value)}
                placeholder="描述你想要的改进，例如：修复游戏开始就 Game Over 的 bug"
                rows={2}
              />
              <button 
                onClick={handleImprove}
                disabled={loading || !improveRequest.trim()}
                className="generate-button"
                style={{ marginTop: '0.5rem' }}
              >
                {loading ? '改进中...' : '✨ 应用改进'}
              </button>
            </div>
          )}
          
          <Sandpack
            key={JSON.stringify(files)} // 使用完整文件内容作为 key
            template="static"
            files={files}
            options={{
              showNavigator: true,
              showTabs: true,
              showLineNumbers: true,
              showInlineErrors: true,
              wrapContent: true,
              editorHeight: '60vh',
              layout: 'preview',
              activeFile: '/index.html',
              autorun: true,
              autoReload: true,
            }}
            theme="auto"
          />
        </div>
      )}

      {!files && !loading && (
        <div className="empty-state">
          <div className="empty-state-content">
            <span className="empty-state-icon">💡</span>
            <h3>开始创造</h3>
            <p>在上方输入你的想法，让 AI 为你生成应用</p>
            <div className="examples">
              <h4>试试这些：</h4>
              <button onClick={() => setPrompt('创建一个简单的计时器')}>
                ⏱️ 计时器
              </button>
              <button onClick={() => setPrompt('创建一个待办事项列表')}>
                ✅ 待办列表
              </button>
              <button onClick={() => setPrompt('创建一个贪吃蛇游戏')}>
                🎮 贪吃蛇游戏
              </button>
            </div>
          </div>
        </div>
      )}
      </div>
    </div>
  )
}

export default App

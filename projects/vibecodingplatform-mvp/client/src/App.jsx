import { useState } from 'react'
import { Sandpack } from '@codesandbox/sandpack-react'
import './App.css'

const API_URL = 'http://localhost:8000'

function App() {
  const [prompt, setPrompt] = useState('')
  const [loading, setLoading] = useState(false)
  const [files, setFiles] = useState(null)
  const [error, setError] = useState(null)
  const [showImprove, setShowImprove] = useState(false)
  const [improveRequest, setImproveRequest] = useState('')

  const handleGenerate = async () => {
    if (!prompt.trim()) {
      alert('请输入提示词')
      return
    }

    setLoading(true)
    setError(null)

    try {
      console.log('发送生成请求:', prompt)
      
      // 重要：引导 AI 生成 Web 应用代码而不是后端代码
      const enhancedPrompt = `请使用 HTML、CSS 和 JavaScript 创建一个可以在浏览器中直接运行的 Web 应用。要求：
- 所有代码必须是前端代码（HTML/CSS/JS）
- 主文件命名为 index.html
- 样式可以内联在 HTML 中，或者创建单独的 style.css 文件
- JavaScript 代码可以内联在 HTML 中，或者创建单独的 script.js 文件
- 不要使用任何需要后端服务器的功能
- 不要使用 Node.js、Python 或其他后端语言

用户需求：${prompt}`
      
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
      
      // 转换文件格式以适配 Sandpack
      // Sandpack 需要 { "/filename": "content" } 格式
      const sandpackFiles = {}
      for (const [filename, content] of Object.entries(generatedFiles)) {
        // 跳过非代码文件（如 requirements.txt, README.md 等）
        if (filename.endsWith('.txt') || filename.endsWith('.md') || filename === 'README') {
          continue
        }
        
        // 确保文件名以 / 开头
        const normalizedFilename = filename.startsWith('/') ? filename : `/${filename}`
        sandpackFiles[normalizedFilename] = content
      }
      
      console.log('转换后的文件:', Object.keys(sandpackFiles))
      
      // 检查是否有有效的文件
      if (Object.keys(sandpackFiles).length === 0) {
        throw new Error('AI 生成的代码不包含可预览的 Web 文件，请尝试更明确的描述，例如："创建一个网页版的计时器"')
      }
      
      // 如果没有 index.html，尝试创建一个
      if (!sandpackFiles['/index.html']) {
        const firstHtmlFile = Object.keys(sandpackFiles).find(f => f.endsWith('.html'))
        if (firstHtmlFile) {
          // 如果有其他 HTML 文件，重命名为 index.html
          sandpackFiles['/index.html'] = sandpackFiles[firstHtmlFile]
          delete sandpackFiles[firstHtmlFile]
        } else {
          // 如果没有任何 HTML 文件，创建一个包装所有内容的 HTML
          const jsFiles = Object.keys(sandpackFiles).filter(f => f.endsWith('.js'))
          const cssFiles = Object.keys(sandpackFiles).filter(f => f.endsWith('.css'))
          
          sandpackFiles['/index.html'] = `<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>生成的应用</title>
  ${cssFiles.map(f => `<link rel="stylesheet" href="${f}">`).join('\n  ')}
</head>
<body>
  <div id="app"></div>
  ${jsFiles.map(f => `<script src="${f}"></script>`).join('\n  ')}
</body>
</html>`
        }
      }
      
      setFiles(sandpackFiles)
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
      
    } catch (err) {
      console.error('改进错误:', err)
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="app-container">
      <header className="app-header">
        <h1>🎨 Vibecoding Platform</h1>
        <p>用自然语言描述，AI 生成可运行的应用</p>
      </header>

      <div className="input-section">
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
              activeFile: files['/index.html'] ? '/index.html' : Object.keys(files)[0],
            }}
            theme="auto"
            customSetup={{
              entry: '/index.html'
            }}
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
  )
}

export default App

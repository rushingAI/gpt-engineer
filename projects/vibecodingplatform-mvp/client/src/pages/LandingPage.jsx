import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { generateApp } from '../utils/api'
import { saveCurrentProject, addToHistory, extractAppName } from '../utils/storage'
import '../styles/LandingPage.css'

function LandingPage() {
  const [prompt, setPrompt] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const navigate = useNavigate()

  const examples = [
    '创建一个计数器应用，有增加和减少按钮',
    '创建一个待办事项列表，支持添加、删除、标记完成',
    '创建一个贪吃蛇游戏',
    '创建一个数据仪表盘，显示4个统计卡片'
  ]

  async function handleGenerate() {
    if (!prompt.trim()) {
      alert('请输入提示词')
      return
    }

    setLoading(true)
    setError(null)

    try {
      console.log('开始生成应用:', prompt)
      
      // 调用 API 生成应用
      const files = await generateApp(prompt)
      
      // 创建项目对象
      const projectId = Date.now().toString()
      const project = {
        id: projectId,
        name: extractAppName(prompt),
        files,
        prompt,
        messages: [
          {
            role: 'user',
            content: prompt,
            timestamp: new Date().toISOString()
          },
          {
            role: 'assistant',
            content: `✅ 已生成应用\n📂 生成了 ${Object.keys(files).length} 个文件`,
            timestamp: new Date().toISOString(),
            filesCount: Object.keys(files).length
          }
        ],
        timestamp: new Date().toISOString()
      }
      
      // 保存到 localStorage
      saveCurrentProject(project)
      addToHistory(project)
      
      console.log('✓ 项目已创建:', projectId)
      
      // 跳转到项目页
      navigate(`/project/${projectId}`)
      
    } catch (err) {
      console.error('生成失败:', err)
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey && !loading) {
      e.preventDefault()
      handleGenerate()
    }
  }

  return (
    <div className="landing-page">
      <div className="landing-content">
        <h1 className="landing-title">🎨 Vibecoding Platform</h1>
        <p className="landing-subtitle">
          用自然语言描述，AI 生成可运行的应用
        </p>
        
        <div className="input-container">
          <textarea
            value={prompt}
            onChange={(e) => setPrompt(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="描述你想要创建的应用... 例如：创建一个待办事项列表"
            disabled={loading}
            rows={4}
            className="landing-textarea"
          />
          
          <button
            onClick={handleGenerate}
            disabled={loading || !prompt.trim()}
            className="landing-button"
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
          <div className="error-box">
            ❌ {error}
          </div>
        )}

        <div className="examples-section">
          <h3>💡 示例提示词</h3>
          <div className="examples-grid">
            {examples.map((example, index) => (
              <button
                key={index}
                onClick={() => setPrompt(example)}
                className="example-button"
                disabled={loading}
              >
                {example}
              </button>
            ))}
          </div>
        </div>

        <button
          onClick={() => navigate('/history')}
          className="history-link"
          disabled={loading}
        >
          📚 查看历史项目
        </button>
      </div>
    </div>
  )
}

export default LandingPage


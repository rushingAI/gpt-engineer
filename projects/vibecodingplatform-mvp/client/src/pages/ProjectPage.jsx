import { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import ChatPanel from '../components/chat/ChatPanel'
import PreviewPanel from '../components/preview/PreviewPanel'
import { getProject, saveCurrentProject, addToHistory } from '../utils/storage'
import { generateApp, improveApp } from '../utils/api'
import { shouldUseImprove, buildFullPrompt } from '../utils/promptAnalyzer'
import '../styles/ProjectPage.css'

function ProjectPage() {
  const { id } = useParams()
  const navigate = useNavigate()
  const [project, setProject] = useState(null)
  const [loading, setLoading] = useState(false)
  const [showHistory, setShowHistory] = useState(false)

  // 加载项目
  useEffect(() => {
    const savedProject = getProject(id)
    if (savedProject) {
      setProject(savedProject)
      console.log('✓ 已加载项目:', savedProject.name)
    } else {
      console.error('项目不存在:', id)
      navigate('/')
    }
  }, [id, navigate])

  // 处理发送消息
  async function handleSendMessage(userMessage) {
    if (!project || loading) return

    setLoading(true)

    // 添加用户消息
    const userMsg = {
      role: 'user',
      content: userMessage,
      timestamp: new Date().toISOString()
    }

    const updatedMessages = [...project.messages, userMsg]
    setProject({ ...project, messages: updatedMessages })

    try {
      // 智能判断使用 improve 还是 generate
      const useImprove = shouldUseImprove(userMessage)
      let newFiles

      if (useImprove) {
        // 小改动：使用 improve_fn
        console.log('📝 使用 improve_fn 优化代码')
        newFiles = await improveApp(userMessage, project.files)
      } else {
        // 大改动：重新生成
        console.log('🆕 使用 gen_code 重新生成')
        const fullPrompt = buildFullPrompt(project.messages, userMessage)
        newFiles = await generateApp(fullPrompt)
      }

      // 添加 AI 消息
      const aiMsg = {
        role: 'assistant',
        content: `✅ 已${useImprove ? '优化' : '生成'}应用\n📂 更新了 ${Object.keys(newFiles).length} 个文件`,
        timestamp: new Date().toISOString(),
        filesCount: Object.keys(newFiles).length
      }

      // 更新项目
      const updatedProject = {
        ...project,
        files: newFiles,
        messages: [...updatedMessages, aiMsg],
        timestamp: new Date().toISOString()
      }

      setProject(updatedProject)
      saveCurrentProject(updatedProject)
      addToHistory(updatedProject)

      console.log('✓ 项目已更新')
    } catch (error) {
      console.error('处理消息失败:', error)

      // 添加错误消息
      const errorMsg = {
        role: 'assistant',
        content: `❌ 处理失败：${error.message}`,
        timestamp: new Date().toISOString()
      }

      setProject({
        ...project,
        messages: [...updatedMessages, errorMsg]
      })
    } finally {
      setLoading(false)
    }
  }

  if (!project) {
    return (
      <div className="project-page">
        <div className="loading-screen">
          <div className="spinner-large"></div>
          <p>加载项目中...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="project-page">
      <header className="project-header">
        <div className="header-left">
          <button onClick={() => navigate('/')} className="back-button">
            ← 返回首页
          </button>
          <h1 className="project-title">{project.name}</h1>
        </div>
        <div className="header-right">
          <span className="saved-indicator">
            💾 已保存
          </span>
        </div>
      </header>

      <div className="project-content">
        <ChatPanel
          messages={project.messages}
          onSendMessage={handleSendMessage}
          loading={loading}
          onShowHistory={() => setShowHistory(!showHistory)}
        />
        <PreviewPanel files={project.files} />
      </div>

      {showHistory && (
        <div className="history-overlay" onClick={() => setShowHistory(false)}>
          <div className="history-modal" onClick={(e) => e.stopPropagation()}>
            <div className="history-header">
              <h2>📚 历史项目</h2>
              <button onClick={() => setShowHistory(false)}>✕</button>
            </div>
            <div className="history-content">
              <p>历史记录功能待实现...</p>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default ProjectPage


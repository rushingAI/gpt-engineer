import { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { ArrowLeft, Save, Loader2 } from 'lucide-react'
import ChatPanel from '../components/chat/ChatPanel'
import PreviewPanel from '../components/preview/PreviewPanel'
import CodeView from '../components/preview/CodeView'
import { getProject, saveCurrentProject, addToHistory } from '../utils/storage'
import { generateApp, improveApp } from '../utils/api'
import { shouldUseImprove, buildFullPrompt } from '../utils/promptAnalyzer'
import { ensureProjectTheme, applyTheme, getProjectTheme, getProjectThemeOverrides } from '../utils/theme'
import { extractColorIntent, selectThemeByIntent } from '../utils/colorIntent'

function ProjectPage() {
  const { id } = useParams()
  const navigate = useNavigate()
  const [project, setProject] = useState(null)
  const [loading, setLoading] = useState(false)
  const [showHistory, setShowHistory] = useState(false)
  const [activeTab, setActiveTab] = useState('preview')

  // 加载项目
  useEffect(() => {
    let savedProject = getProject(id)
    if (savedProject) {
      // 🎨 确保旧项目有主题（自动补齐）
      savedProject = ensureProjectTheme(savedProject, savedProject.prompt || '')
      
      // 🎨 应用主题到当前页面
      const themeName = getProjectTheme(savedProject)
      const themeOverrides = getProjectThemeOverrides(savedProject)
      applyTheme(themeName, themeOverrides)
      
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
        content: `已${useImprove ? '优化' : '生成'}应用\n更新了 ${Object.keys(newFiles).length} 个文件`,
        timestamp: new Date().toISOString(),
        filesCount: Object.keys(newFiles).length
      }

      // 🎨 检查用户消息中是否有颜色意图（支持在改进阶段更新主题）
      const colorIntent = extractColorIntent(userMessage)
      let updatedProject = {
        ...project,
        files: newFiles,
        messages: [...updatedMessages, aiMsg],
        timestamp: new Date().toISOString()
      }

      if (colorIntent.colorName || colorIntent.hex) {
        const newTheme = selectThemeByIntent(colorIntent)
        if (newTheme) {
          console.log(`🎨 检测到颜色意图，更新主题为: ${newTheme}`)
          if (!updatedProject.metadata) {
            updatedProject.metadata = {}
          }
          updatedProject.metadata.themeName = newTheme
          
          // 立即应用新主题到当前页面
          applyTheme(newTheme, updatedProject.metadata.themeOverrides || {})
        }
      }

      setProject(updatedProject)
      saveCurrentProject(updatedProject)
      addToHistory(updatedProject)

      console.log('✓ 项目已更新')
    } catch (error) {
      console.error('处理消息失败:', error)

      // 添加错误消息
      const errorMessage = error.message || error.toString() || '未知错误'
      const errorMsg = {
        role: 'assistant',
        content: `处理失败：${errorMessage}`,
        timestamp: new Date().toISOString()
      }

      const failedProject = {
        ...project,
        messages: [...updatedMessages, errorMsg]
      }
      
      setProject(failedProject)
      saveCurrentProject(failedProject)
    } finally {
      setLoading(false)
    }
  }

  if (!project) {
    return (
      <div className="project-page min-h-screen flex items-center justify-center">
        <div className="text-center space-y-4 relative z-10">
          <Loader2 className="h-12 w-12 animate-spin mx-auto" style={{ color: 'var(--project-accent)' }} />
          <p style={{ color: 'var(--project-text-secondary)' }}>加载项目中...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="project-page h-screen flex flex-col">
      {/* 顶部导航栏 - Lovable 风格：更矮，全宽 */}
      <header className="relative z-10 backdrop-blur-md border-b" style={{ 
        background: 'rgba(255, 255, 255, 0.7)',
        borderColor: 'var(--project-border)'
      }}>
        <div className="h-12 px-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <button
              onClick={() => navigate('/')}
              className="flex items-center gap-2 px-2 py-1.5 rounded-md transition-all hover:bg-black/5"
              style={{ color: 'var(--project-text-secondary)' }}
            >
              <ArrowLeft className="h-3.5 w-3.5" />
              <span className="text-xs font-medium">返回首页</span>
            </button>
            <div className="w-px h-4 bg-black/10"></div>
            <h1 className="text-sm font-semibold" style={{ color: 'var(--project-text-primary)' }}>
              {project.name}
            </h1>
          </div>
          
          <div className="flex items-center gap-3">
            {/* Preview/Code 切换按钮 */}
            <div className="project-tab-group">
              <button
                onClick={() => setActiveTab('preview')}
                className={`project-tab-btn ${activeTab === 'preview' ? 'active' : ''}`}
              >
                Preview
              </button>
              <button
                onClick={() => setActiveTab('code')}
                className={`project-tab-btn ${activeTab === 'code' ? 'active' : ''}`}
              >
                Code
              </button>
            </div>
            
            {/* 保存状态 */}
            <div className="flex items-center gap-1.5 text-xs" style={{ color: 'var(--project-text-muted)' }}>
              <Save className="h-3.5 w-3.5" />
              <span>已保存</span>
            </div>
          </div>
        </div>
      </header>

      {/* 主内容区域 - 完全铺满，无padding */}
      <div className="flex-1 flex overflow-hidden relative">
        <ChatPanel
          messages={project.messages}
          onSendMessage={handleSendMessage}
          loading={loading}
          onShowHistory={() => setShowHistory(!showHistory)}
        />
        
        {/* 右侧主工作区 - 完全铺满 */}
        <div className="flex-1 overflow-hidden">
          {activeTab === 'preview' ? (
            <PreviewPanel 
              files={project.files} 
              activeTab={activeTab}
              project={project}
            />
          ) : (
            <CodeView files={project.files} />
          )}
        </div>
      </div>

      {/* 历史记录模态框 */}
      {showHistory && (
        <div
          className="fixed inset-0 bg-black/50 flex items-center justify-center z-50"
          onClick={() => setShowHistory(false)}
        >
          <div
            className="project-content-card w-full max-w-2xl max-h-[80vh] overflow-hidden"
            onClick={(e) => e.stopPropagation()}
          >
            <div className="p-6 border-b flex items-center justify-between" style={{ borderColor: 'var(--project-border)' }}>
              <h2 className="text-xl font-semibold" style={{ color: 'var(--project-text-primary)' }}>
                📚 历史项目
              </h2>
              <button
                onClick={() => setShowHistory(false)}
                className="w-8 h-8 rounded-lg flex items-center justify-center hover:bg-black/5 transition-colors"
                style={{ color: 'var(--project-text-secondary)' }}
              >
                ✕
              </button>
            </div>
            <div className="p-6">
              <p style={{ color: 'var(--project-text-muted)' }}>历史记录功能待实现...</p>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default ProjectPage


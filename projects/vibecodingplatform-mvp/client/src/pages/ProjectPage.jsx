import { useState, useEffect, useRef } from 'react'
import { useParams, useNavigate, useSearchParams } from 'react-router-dom'
import { ArrowLeft, Save, Loader2 } from 'lucide-react'
import ChatPanel from '../components/chat/ChatPanel'
import PreviewPanel from '../components/preview/PreviewPanel'
import CodeView from '../components/preview/CodeView'
import { getProject, saveCurrentProject, addToHistory } from '../utils/storage'
import { generateApp, improveApp, generateAppStreaming, improveAppStreaming } from '../utils/api'
import { buildFullPrompt } from '../utils/promptAnalyzer'
import { ensureProjectTheme, applyTheme, getProjectTheme, getProjectThemeOverrides } from '../utils/theme'
import { extractColorIntent, selectThemeByIntent } from '../utils/colorIntent'

function ProjectPage() {
  const { id } = useParams()
  const navigate = useNavigate()
  const [searchParams] = useSearchParams()
  const [project, setProject] = useState(null)
  const [loading, setLoading] = useState(false)
  const [showHistory, setShowHistory] = useState(false)
  const [activeTab, setActiveTab] = useState('preview')
  const [containerStepCallback, setContainerStepCallback] = useState(null)
  const autoGenerateTriggered = useRef(false)

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
  
  // 自动开始生成（如果URL包含 ?generate=true）
  useEffect(() => {
    const shouldGenerate = searchParams.get('generate') === 'true'
    if (shouldGenerate && !autoGenerateTriggered.current && project && project.prompt) {
      autoGenerateTriggered.current = true
      console.log('🚀 自动开始流式生成...')
      // 使用 setTimeout 确保组件完全挂载后再触发
      setTimeout(() => {
        // 检查是否已经有文件（避免重复生成）
        if (!project.files || Object.keys(project.files).length === 0) {
          // 直接开始生成，不添加新的用户消息（因为已经在 LandingPage 添加过了）
          handleAutoGenerate(project.prompt)
        }
      }, 100)
    }
  }, [project, searchParams])
  
  // 自动生成函数（不重复添加用户消息）
  async function handleAutoGenerate(userMessage) {
    if (!project || loading) return

    setLoading(true)

    // 获取已存在的消息列表和 AI 消息
    const updatedMessages = [...project.messages]
    const aiMsg = updatedMessages[updatedMessages.length - 1] // 最后一条应该是 AI 消息
    
    // 确保 AI 消息有正确的结构
    if (!aiMsg.steps) {
      aiMsg.steps = []
    }

    try {
      // 判断是否使用 generate（重新生成）还是 improve（改进）
      // 规则：从首页跳转（?generate=true）→ generate
      //      项目页中对话 → 默认improve，但检测强关键词时用generate
      const isFromLandingPage = searchParams.get('generate') === 'true'
      
      let useGenerate = false
      let reason = ''
      
      if (isFromLandingPage) {
        // 从首页创建新应用
        useGenerate = true
        reason = '首次生成'
      } else {
        // 项目页中继续对话：检测"重新创建"等强关键词
        const strongGenKeywords = /重新创建|重新生成|completely new|rebuild|recreate|start over|from scratch/i
        if (strongGenKeywords.test(userMessage)) {
          useGenerate = true
          reason = '重新生成'
        } else {
          useGenerate = false
          reason = '改进代码'
        }
      }
      
      let newFiles

      // 开始流式生成
      if (useGenerate) {
        console.log(`🆕 使用流式 generate (${reason})`)
        const fullPrompt = buildFullPrompt(project.messages, userMessage)
        newFiles = await generateAppStreaming(
          fullPrompt,
          (event) => handleStreamEvent(event, aiMsg, updatedMessages),
          true // useTemplate
        )
      } else {
        console.log(`📝 使用流式 improve (${reason})`)
        newFiles = await improveAppStreaming(
          userMessage, 
          project.files,
          (event) => handleStreamEvent(event, aiMsg, updatedMessages)
        )
      }

      if (!newFiles) {
        throw new Error('生成失败：未收到文件数据')
      }

      // 🎨 检查用户消息中是否有颜色意图（支持在改进阶段更新主题）
      const colorIntent = extractColorIntent(userMessage)
      let updatedProject = {
        ...project,
        files: newFiles,
        messages: updatedMessages,
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

  // 处理流式事件
  function handleStreamEvent(event, aiMsg, messages) {
    if (event.type === 'status') {
      // 添加或更新状态步骤
      const existingStepIndex = aiMsg.steps.findIndex(s => s.status === 'running')
      
      if (existingStepIndex !== -1) {
        // 标记上一步完成
        aiMsg.steps[existingStepIndex].status = 'completed'
        aiMsg.steps[existingStepIndex].icon = 'CheckCircle2'
      }
      
      // 添加新步骤
      aiMsg.steps.push({
        id: `step-${Date.now()}`,
        label: event.content,
        status: 'running',
        icon: 'Loader2'
      })
    } else if (event.type === 'file') {
      // 文件生成完成，更新标签
      const runningStepIndex = aiMsg.steps.findIndex(s => s.status === 'running')
      if (runningStepIndex !== -1) {
        aiMsg.steps[runningStepIndex].status = 'completed'
        aiMsg.steps[runningStepIndex].icon = 'CheckCircle2'
      }
      
      aiMsg.steps.push({
        id: `file-${event.filename}`,
        label: `已生成 ${event.filename}`,
        status: 'completed',
        icon: 'CheckCircle2'
      })
    } else if (event.type === 'complete') {
      // 生成完成
      const runningStepIndex = aiMsg.steps.findIndex(s => s.status === 'running')
      if (runningStepIndex !== -1) {
        aiMsg.steps[runningStepIndex].status = 'completed'
        aiMsg.steps[runningStepIndex].icon = 'CheckCircle2'
      }
      
      // 添加完成步骤
      aiMsg.steps.push({
        id: 'complete',
        label: `✓ 代码生成完成 (${event.filesCount} 个文件)`,
        status: 'completed',
        icon: 'CheckCircle2'
      })
      
      // 添加环境准备步骤（等待状态）
      addContainerSteps(aiMsg)
    } else if (event.type === 'error') {
      // 错误处理
      const runningStepIndex = aiMsg.steps.findIndex(s => s.status === 'running')
      if (runningStepIndex !== -1) {
        aiMsg.steps[runningStepIndex].status = 'failed'
        aiMsg.steps[runningStepIndex].icon = 'AlertTriangle'
      }
      
      aiMsg.steps.push({
        id: 'error',
        label: `✗ ${event.message}`,
        status: 'failed',
        icon: 'AlertTriangle'
      })
    }
    
    // 触发重新渲染
    setProject({ ...project, messages: [...messages] })
  }

  // 添加环境准备步骤
  function addContainerSteps(aiMsg) {
    const containerSteps = [
      { id: 'boot', label: '正在启动容器', duration: '2-5秒' },
      { id: 'mount', label: '挂载文件系统', duration: '1秒' },
      { id: 'install', label: '安装依赖', duration: '5-10秒' },
      { id: 'dev', label: '启动开发服务器', duration: '2-3秒' },
    ]
    
    containerSteps.forEach(step => {
      aiMsg.steps.push({
        ...step,
        status: 'waiting',
        icon: 'Clock'
      })
    })
  }

  // WebContainer 步骤更新回调
  function handleContainerStepUpdate(stepId, status) {
    setProject(prevProject => {
      if (!prevProject || !prevProject.messages.length) return prevProject
      
      const messages = [...prevProject.messages]
      const lastMessage = messages[messages.length - 1]
      
      if (lastMessage.role === 'assistant' && lastMessage.steps) {
        const stepIndex = lastMessage.steps.findIndex(s => s.id === stepId)
        if (stepIndex !== -1) {
          lastMessage.steps[stepIndex].status = status
          lastMessage.steps[stepIndex].icon = status === 'completed' 
            ? 'CheckCircle2' 
            : status === 'running'
            ? 'Loader2'
            : status === 'failed'
            ? 'AlertTriangle'
            : 'Clock'
        }
        
        // 如果所有步骤完成，标记流式结束
        const allCompleted = lastMessage.steps.every(
          s => s.status === 'completed' || s.status === 'failed'
        )
        if (allCompleted) {
          lastMessage.streaming = false
        }
      }
      
      return { ...prevProject, messages }
    })
  }

  // 处理发送消息（流式生成）
  async function handleSendMessage(userMessage) {
    if (!project || loading) return

    setLoading(true)

    // 1. 添加用户消息
    const userMsg = {
      role: 'user',
      content: userMessage,
      timestamp: new Date().toISOString()
    }
    
    // 2. 创建初始 AI 消息（带流式状态）
    const aiMsg = {
      role: 'assistant',
      content: '',
      timestamp: new Date().toISOString(),
      streaming: true,
      steps: []
    }

    let updatedMessages = [...project.messages, userMsg, aiMsg]
    setProject({ ...project, messages: updatedMessages })

    try {
      // 判断是否使用 generate（重新生成）还是 improve（改进）
      // 规则：项目页中对话 → 默认improve，但检测强关键词时用generate
      const strongGenKeywords = /重新创建|重新生成|completely new|rebuild|recreate|start over|from scratch/i
      const useGenerate = strongGenKeywords.test(userMessage)
      
      let newFiles

      // 3. 开始流式生成
      if (useGenerate) {
        console.log('🆕 使用流式 generate (重新生成)')
        const fullPrompt = buildFullPrompt(project.messages, userMessage)
        newFiles = await generateAppStreaming(
          fullPrompt,
          (event) => handleStreamEvent(event, aiMsg, updatedMessages),
          true // useTemplate
        )
      } else {
        console.log('📝 使用流式 improve (改进代码)')
        newFiles = await improveAppStreaming(
          userMessage, 
          project.files,
          (event) => handleStreamEvent(event, aiMsg, updatedMessages)
        )
      }

      if (!newFiles) {
        throw new Error('生成失败：未收到文件数据')
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
              onStepUpdate={handleContainerStepUpdate}
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


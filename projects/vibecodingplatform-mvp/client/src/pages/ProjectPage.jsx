import { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { ArrowLeft, Save, Eye, Code2, Loader2 } from 'lucide-react'
import ChatPanel from '../components/chat/ChatPanel'
import PreviewPanel from '../components/preview/PreviewPanel'
import { getProject, saveCurrentProject, addToHistory } from '../utils/storage'
import { generateApp, improveApp } from '../utils/api'
import { shouldUseImprove, buildFullPrompt } from '../utils/promptAnalyzer'
import { Button } from '@/components/ui/button'
import { Separator } from '@/components/ui/separator'

function ProjectPage() {
  const { id } = useParams()
  const navigate = useNavigate()
  const [project, setProject] = useState(null)
  const [loading, setLoading] = useState(false)
  const [showHistory, setShowHistory] = useState(false)
  const [activeTab, setActiveTab] = useState('sandbox')

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
      const errorMessage = error.message || error.toString() || '未知错误'
      const errorMsg = {
        role: 'assistant',
        content: `❌ 处理失败：${errorMessage}`,
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
      <div className="min-h-screen bg-lovable-gray-50 flex items-center justify-center">
        <div className="text-center space-y-4">
          <Loader2 className="h-12 w-12 animate-spin text-lovable-orange mx-auto" />
          <p className="text-gray-600">加载项目中...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="h-screen bg-lovable-gray-50 flex flex-col">
      {/* 顶部导航栏 */}
      <header className="bg-white border-b border-gray-200 shadow-sm">
        <div className="h-16 px-6 flex items-center justify-between">
          <div className="flex items-center gap-4">
            <Button
              variant="ghost"
              size="sm"
              onClick={() => navigate('/')}
              className="text-gray-600 hover:text-lovable-orange"
            >
              <ArrowLeft className="mr-2 h-4 w-4" />
              返回首页
            </Button>
            <Separator orientation="vertical" className="h-6" />
            <h1 className="text-lg font-semibold text-lovable-gray-900">
              {project.name}
            </h1>
          </div>
          
          <div className="flex items-center gap-3">
            {/* Sandbox/Code 切换按钮 */}
            <div className="flex items-center gap-2 bg-gray-100 p-1 rounded-lg">
              <Button
                variant={activeTab === 'sandbox' ? 'default' : 'ghost'}
                size="sm"
                onClick={() => setActiveTab('sandbox')}
                className={activeTab === 'sandbox' ? '' : 'text-gray-600 hover:text-gray-900'}
              >
                <Eye className="mr-2 h-4 w-4" />
                Sandbox
              </Button>
              <Button
                variant={activeTab === 'code' ? 'default' : 'ghost'}
                size="sm"
                onClick={() => setActiveTab('code')}
                className={activeTab === 'code' ? '' : 'text-gray-600 hover:text-gray-900'}
              >
                <Code2 className="mr-2 h-4 w-4" />
                Code
              </Button>
            </div>
            
            {/* 保存状态 */}
            <div className="flex items-center gap-2 text-sm text-gray-500">
              <Save className="h-4 w-4" />
              <span>已保存</span>
            </div>
          </div>
        </div>
      </header>

      {/* 主内容区域 */}
      <div className="flex-1 flex overflow-hidden">
        <ChatPanel
          messages={project.messages}
          onSendMessage={handleSendMessage}
          loading={loading}
          onShowHistory={() => setShowHistory(!showHistory)}
        />
        <PreviewPanel files={project.files} activeTab={activeTab} />
      </div>

      {/* 历史记录模态框 */}
      {showHistory && (
        <div
          className="fixed inset-0 bg-black/50 flex items-center justify-center z-50"
          onClick={() => setShowHistory(false)}
        >
          <div
            className="bg-white rounded-2xl shadow-2xl w-full max-w-2xl max-h-[80vh] overflow-hidden"
            onClick={(e) => e.stopPropagation()}
          >
            <div className="p-6 border-b border-gray-200 flex items-center justify-between">
              <h2 className="text-xl font-semibold text-lovable-gray-900">
                📚 历史项目
              </h2>
              <Button
                variant="ghost"
                size="icon"
                onClick={() => setShowHistory(false)}
              >
                ✕
              </Button>
            </div>
            <div className="p-6">
              <p className="text-gray-500">历史记录功能待实现...</p>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default ProjectPage


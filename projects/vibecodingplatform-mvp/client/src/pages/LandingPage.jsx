import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { generateApp, generateAppStreaming } from '../utils/api'
import { saveCurrentProject, addToHistory, extractAppName } from '../utils/storage'
import { ensureProjectTheme } from '../utils/theme'
import Navbar from '../components/landing/Navbar'
import Hero from '../components/landing/Hero'
import PromptComposer from '../components/landing/PromptComposer'
import ExamplePrompts from '../components/landing/ExamplePrompts'

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
      console.log('开始生成应用（流式）:', prompt)
      
      // 创建项目对象（先创建空项目）
      const projectId = Date.now().toString()
      
      // 用户消息
      const userMsg = {
        role: 'user',
        content: prompt,
        timestamp: new Date().toISOString()
      }
      
      // AI 消息（流式状态）
      const aiMsg = {
        role: 'assistant',
        content: '',
        timestamp: new Date().toISOString(),
        streaming: true,
        steps: []
      }
      
      let project = {
        id: projectId,
        name: extractAppName(prompt),
        files: {},  // 先创建空文件
        prompt,
        messages: [userMsg, aiMsg],
        metadata: {},
        timestamp: new Date().toISOString()
      }
      
      // 🎨 自动选择主题
      project = ensureProjectTheme(project, prompt)
      
      // 保存初始项目
      saveCurrentProject(project)
      addToHistory(project)
      
      console.log('✓ 项目已创建（流式）:', projectId)
      
      // 立即跳转到项目页，让项目页处理流式生成
      navigate(`/project/${projectId}?generate=true`)
      
    } catch (err) {
      console.error('创建项目失败:', err)
      setError(err.message)
      setLoading(false)
    }
  }

  return (
    <div className="landing-page min-h-screen flex flex-col">
      {/* 顶部导航栏 */}
      <Navbar />
      
      {/* 主内容区 - 垂直居中，充足留白 */}
      <main className="flex-1 flex flex-col items-center justify-center px-6 py-32 pt-40">
        <div className="w-full max-w-4xl">
          {/* Hero 区域 */}
          <div className="mb-16">
            <Hero />
          </div>
          
          {/* 主输入卡片 - 视觉焦点 */}
          <div className="mb-20">
            <PromptComposer
              prompt={prompt}
              setPrompt={setPrompt}
              onGenerate={handleGenerate}
              loading={loading}
            />
          </div>

          {/* 错误提示 */}
          {error && (
            <div className="mb-12 landing-main-card p-5 border-red-200 bg-red-50">
              <p className="text-red-700 text-sm text-center font-medium">{error}</p>
            </div>
          )}

          {/* 示例提示词 */}
          <ExamplePrompts
            examples={examples}
            onSelectExample={(example) => setPrompt(example)}
            loading={loading}
          />
        </div>
      </main>
      
      {/* 页脚区域 */}
      <footer className="py-12 text-center">
        <p 
          className="text-xs"
          style={{ color: 'var(--landing-text-muted)' }}
        >
          © 2024 BuildFast. 用 AI 快速构建你的创意
        </p>
      </footer>
    </div>
  )
}

export default LandingPage


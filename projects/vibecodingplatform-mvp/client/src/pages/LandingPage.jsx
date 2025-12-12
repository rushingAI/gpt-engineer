import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Sparkles, History, Loader2 } from 'lucide-react'
import { generateApp } from '../utils/api'
import { saveCurrentProject, addToHistory, extractAppName } from '../utils/storage'
import { Button } from '@/components/ui/button'
import { Textarea } from '@/components/ui/textarea'
import { Card, CardContent } from '@/components/ui/card'

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
    <div className="min-h-screen bg-lovable-gray-50 flex flex-col items-center justify-center p-6">
      <div className="w-full max-w-4xl space-y-8">
        {/* 标题区域 */}
        <div className="text-center space-y-4">
          <h1 className="text-5xl md:text-6xl font-bold text-lovable-gray-900">
            🎨 Vibecoding Platform
          </h1>
          <p className="text-xl text-gray-600">
            用自然语言描述，AI 生成可运行的应用
          </p>
        </div>
        
        {/* 主输入区域 */}
        <Card className="shadow-lg hover:shadow-xl transition-shadow duration-200">
          <CardContent className="p-6 space-y-4">
            <Textarea
              value={prompt}
              onChange={(e) => setPrompt(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="描述你想要创建的应用... 例如：创建一个待办事项列表"
              disabled={loading}
              rows={6}
              className="text-base resize-none"
            />
            
            <Button
              onClick={handleGenerate}
              disabled={loading || !prompt.trim()}
              size="lg"
              className="w-full text-base font-semibold"
            >
              {loading ? (
                <>
                  <Loader2 className="mr-2 h-5 w-5 animate-spin" />
                  生成中...
                </>
              ) : (
                <>
                  <Sparkles className="mr-2 h-5 w-5" />
                  生成应用
                </>
              )}
            </Button>
          </CardContent>
        </Card>

        {/* 错误提示 */}
        {error && (
          <Card className="border-red-200 bg-red-50">
            <CardContent className="p-4">
              <p className="text-red-600 text-sm">❌ {error}</p>
            </CardContent>
          </Card>
        )}

        {/* 示例提示词 */}
        <div className="space-y-4">
          <h3 className="text-lg font-semibold text-lovable-gray-900">💡 示例提示词</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            {examples.map((example, index) => (
              <Card
                key={index}
                className="cursor-pointer hover:shadow-md hover:border-lovable-orange transition-all duration-200"
                onClick={() => !loading && setPrompt(example)}
              >
                <CardContent className="p-4">
                  <p className="text-sm text-gray-700">{example}</p>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>

        {/* 历史项目链接 */}
        <div className="flex justify-center">
          <Button
            onClick={() => navigate('/history')}
            variant="ghost"
            disabled={loading}
            className="text-lovable-orange hover:text-lovable-coral"
          >
            <History className="mr-2 h-5 w-5" />
            查看历史项目
          </Button>
        </div>
      </div>
    </div>
  )
}

export default LandingPage


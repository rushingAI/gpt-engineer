import { ArrowUp, Loader2 } from 'lucide-react'
import { Textarea } from '@/components/ui/textarea'

function PromptComposer({ prompt, setPrompt, onGenerate, loading }) {
  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey && !loading) {
      e.preventDefault()
      onGenerate()
    }
  }

  return (
    <div className="landing-main-card p-8 animate-scale-in relative">
      {/* 大号输入框 - 无边框，融入卡片 */}
      <Textarea
        value={prompt}
        onChange={(e) => setPrompt(e.target.value)}
        onKeyPress={handleKeyPress}
        placeholder="描述你想要创建的应用..."
        disabled={loading}
        rows={3}
        className="text-base resize-none border-0 focus:ring-0 focus:outline-none bg-transparent p-0 shadow-none pr-12"
        style={{
          fontSize: '16px',
          lineHeight: '1.6',
          color: '#0f0f0f',
          outline: 'none',
          boxShadow: 'none',
          border: 'none'
        }}
      />
      
      {/* 圆形生成按钮 - 固定在右下角 */}
      <button
        onClick={onGenerate}
        disabled={loading || !prompt.trim()}
        className="landing-primary-btn !p-0 w-9 h-9 !rounded-full flex items-center justify-center absolute bottom-6 right-6"
      >
        {loading ? (
          <Loader2 className="h-4 w-4 animate-spin" />
        ) : (
          <ArrowUp className="h-4 w-4" />
        )}
      </button>
    </div>
  )
}

export default PromptComposer


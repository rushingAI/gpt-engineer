import { useState, useRef, useEffect } from 'react'
import { History } from 'lucide-react'
import MessageList from './MessageList'
import ChatInput from './ChatInput'

function ChatPanel({ messages, onSendMessage, loading, onShowHistory }) {
  const [inputValue, setInputValue] = useState('')
  const messagesEndRef = useRef(null)

  // 自动滚动到最新消息
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  const handleSend = () => {
    if (!inputValue.trim() || loading) return
    
    onSendMessage(inputValue)
    setInputValue('')
  }

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }

  return (
    <div className="w-[360px] flex flex-col border-r relative z-10" style={{ 
      borderColor: 'var(--project-border)',
      background: '#ffffff'
    }}>
      {/* 对话头部 */}
      <div className="px-4 py-3 border-b" style={{ borderColor: 'var(--project-border)' }}>
        <div className="flex items-center justify-between">
          <h2 className="text-sm font-semibold" style={{ color: 'var(--project-text-primary)' }}>
            对话
          </h2>
          <button
            onClick={onShowHistory}
            className="flex items-center gap-1.5 px-2 py-1 rounded-md text-xs font-medium transition-all hover:bg-black/5"
            style={{ color: 'var(--project-text-secondary)' }}
          >
            <History className="h-3.5 w-3.5" />
            历史
          </button>
        </div>
      </div>

      {/* 消息列表 */}
      <div className="flex-1 overflow-y-auto px-4 py-4">
        <MessageList messages={messages} loading={loading} />
        <div ref={messagesEndRef} />
      </div>

      {/* 输入区域 */}
      <div className="p-4 border-t" style={{ borderColor: 'var(--project-border)' }}>
        <ChatInput
          value={inputValue}
          onChange={setInputValue}
          onSend={handleSend}
          onKeyPress={handleKeyPress}
          disabled={loading}
        />
      </div>
    </div>
  )
}

export default ChatPanel


import { useState, useRef, useEffect } from 'react'
import { History } from 'lucide-react'
import MessageList from './MessageList'
import ChatInput from './ChatInput'
import { Button } from '@/components/ui/button'
import { Separator } from '@/components/ui/separator'

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
    <div className="w-[320px] bg-white border-r border-gray-200 flex flex-col shadow-sm">
      {/* 对话头部 */}
      <div className="h-16 px-4 flex items-center justify-between border-b border-gray-200">
        <h2 className="text-lg font-semibold text-lovable-gray-900">💬 对话</h2>
        <Button
          variant="ghost"
          size="sm"
          onClick={onShowHistory}
          className="text-gray-600 hover:text-lovable-orange"
        >
          <History className="h-4 w-4 mr-2" />
          历史
        </Button>
      </div>

      {/* 消息列表 */}
      <div className="flex-1 overflow-y-auto px-4 py-4">
        <MessageList messages={messages} loading={loading} />
        <div ref={messagesEndRef} />
      </div>

      <Separator />

      {/* 输入区域 */}
      <div className="p-4">
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


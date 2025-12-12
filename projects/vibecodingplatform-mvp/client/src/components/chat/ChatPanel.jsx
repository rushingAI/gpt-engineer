import { useState, useRef, useEffect } from 'react'
import MessageList from './MessageList'
import ChatInput from './ChatInput'
import '../../styles/ChatPanel.css'

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
    <div className="chat-panel">
      <div className="chat-header">
        <h2>💬 对话</h2>
        <button onClick={onShowHistory} className="history-button">
          📚 历史记录
        </button>
      </div>

      <MessageList messages={messages} loading={loading} />
      <div ref={messagesEndRef} />

      <ChatInput
        value={inputValue}
        onChange={setInputValue}
        onSend={handleSend}
        onKeyPress={handleKeyPress}
        disabled={loading}
      />
    </div>
  )
}

export default ChatPanel


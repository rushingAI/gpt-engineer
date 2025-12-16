import StreamingMessage from './StreamingMessage'

function MessageList({ messages, loading }) {
  return (
    <div className="space-y-3">
      {messages.map((message, index) => {
        // 如果是流式消息（有 steps 字段），使用 StreamingMessage 组件
        if (message.role === 'assistant' && (message.steps || message.streaming)) {
          return <StreamingMessage key={index} message={message} />
        }
        
        // 普通消息
        return (
          <div
            key={index}
            className={message.role === 'user' ? 'flex justify-end' : 'flex justify-start'}
          >
            {/* 消息内容 - 极简风格 */}
            <div 
              className="max-w-[85%] rounded-lg px-3 py-2"
              style={{
                background: message.role === 'user' 
                  ? '#f5f5f5' 
                  : 'transparent',
                border: message.role === 'user' 
                  ? 'none'
                  : 'none'
              }}
            >
              <p 
                className="text-xs whitespace-pre-wrap break-words leading-relaxed"
                style={{
                  color: 'var(--project-text-primary)'
                }}
              >
                {message.content}
              </p>
              <p 
                className="text-[10px] mt-1.5"
                style={{
                  color: 'var(--project-text-muted)'
                }}
              >
                {formatTime(message.timestamp)}
              </p>
            </div>
          </div>
        )
      })}
      
      {/* 加载动画 - 极简风格 */}
      {loading && (
        <div className="flex justify-start">
          <div className="flex gap-1 px-3 py-2">
            <span 
              className="w-1.5 h-1.5 rounded-full animate-bounce" 
              style={{ 
                background: 'var(--project-text-muted)',
                animationDelay: '0ms' 
              }}
            ></span>
            <span 
              className="w-1.5 h-1.5 rounded-full animate-bounce" 
              style={{ 
                background: 'var(--project-text-muted)',
                animationDelay: '150ms' 
              }}
            ></span>
            <span 
              className="w-1.5 h-1.5 rounded-full animate-bounce" 
              style={{ 
                background: 'var(--project-text-muted)',
                animationDelay: '300ms' 
              }}
            ></span>
          </div>
        </div>
      )}
    </div>
  )
}

function formatTime(timestamp) {
  const date = new Date(timestamp)
  const now = new Date()
  const diffMs = now - date
  const diffSec = Math.floor(diffMs / 1000)
  const diffMin = Math.floor(diffSec / 60)
  const diffHour = Math.floor(diffMin / 60)
  
  if (diffSec < 10) return '刚刚'
  if (diffSec < 60) return `${diffSec}秒前`
  if (diffMin < 60) return `${diffMin}分钟前`
  if (diffHour < 24) return `${diffHour}小时前`
  
  return date.toLocaleString('zh-CN', {
    month: 'numeric',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
}

export default MessageList


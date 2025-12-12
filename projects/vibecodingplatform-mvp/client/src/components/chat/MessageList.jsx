import '../../styles/MessageList.css'

function MessageList({ messages, loading }) {
  return (
    <div className="message-list">
      {messages.map((message, index) => (
        <div
          key={index}
          className={`message message-${message.role}`}
        >
          <div className="message-avatar">
            {message.role === 'user' ? '👤' : '🤖'}
          </div>
          <div className="message-content">
            <div className="message-text">{message.content}</div>
            <div className="message-time">
              {formatTime(message.timestamp)}
            </div>
          </div>
        </div>
      ))}
      
      {loading && (
        <div className="message message-assistant">
          <div className="message-avatar">🤖</div>
          <div className="message-content">
            <div className="message-loading">
              <span className="dot"></span>
              <span className="dot"></span>
              <span className="dot"></span>
            </div>
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


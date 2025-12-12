import { Card, CardContent } from '@/components/ui/card'

function MessageList({ messages, loading }) {
  return (
    <div className="space-y-4">
      {messages.map((message, index) => (
        <div
          key={index}
          className={`flex gap-3 ${message.role === 'user' ? 'flex-row-reverse' : 'flex-row'}`}
        >
          {/* 头像 */}
          <div className={`flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center text-sm ${
            message.role === 'user' 
              ? 'bg-lovable-orange text-white' 
              : 'bg-gray-200 text-gray-700'
          }`}>
            {message.role === 'user' ? '👤' : '🤖'}
          </div>
          
          {/* 消息内容 */}
          <div className="flex-1 min-w-0">
            <Card className={`${
              message.role === 'user' 
                ? 'bg-gradient-to-br from-lovable-orange to-lovable-coral text-white border-transparent' 
                : 'bg-gray-50 border-gray-200'
            } shadow-sm`}>
              <CardContent className="p-3">
                <p className={`text-sm whitespace-pre-wrap break-words ${
                  message.role === 'user' ? 'text-white' : 'text-lovable-gray-900'
                }`}>
                  {message.content}
                </p>
                <p className={`text-xs mt-2 ${
                  message.role === 'user' ? 'text-white/70' : 'text-gray-500'
                }`}>
                  {formatTime(message.timestamp)}
                </p>
              </CardContent>
            </Card>
          </div>
        </div>
      ))}
      
      {/* 加载动画 */}
      {loading && (
        <div className="flex gap-3">
          <div className="flex-shrink-0 w-8 h-8 rounded-full bg-gray-200 text-gray-700 flex items-center justify-center text-sm">
            🤖
          </div>
          <Card className="bg-gray-50 border-gray-200 shadow-sm">
            <CardContent className="p-3">
              <div className="flex gap-1">
                <span className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0ms' }}></span>
                <span className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '150ms' }}></span>
                <span className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '300ms' }}></span>
              </div>
            </CardContent>
          </Card>
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


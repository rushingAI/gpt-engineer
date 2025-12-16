import { Loader2, CheckCircle2, Clock, AlertTriangle } from 'lucide-react'

/**
 * 图标映射表
 */
const iconMap = {
  'Loader2': Loader2,
  'CheckCircle2': CheckCircle2,
  'Clock': Clock,
  'AlertTriangle': AlertTriangle,
}

/**
 * StreamingMessage - 显示流式生成的 AI 消息
 * 
 * @param {object} message - 消息对象
 * @param {string} message.content - 基础描述文本（可选）
 * @param {array} message.steps - 步骤列表
 * @param {string} message.timestamp - 时间戳
 */
function StreamingMessage({ message }) {
  return (
    <div className="flex justify-start">
      <div className="max-w-[85%] rounded-lg px-3 py-2">
        {/* 基础描述文本（可选） */}
        {message.content && (
          <p 
            className="text-xs mb-2 whitespace-pre-wrap break-words leading-relaxed"
            style={{ color: 'var(--project-text-primary)' }}
          >
            {message.content}
          </p>
        )}
        
        {/* 步骤列表 */}
        {message.steps && message.steps.length > 0 && (
          <div className="space-y-1.5">
            {message.steps.map((step, index) => {
              const Icon = iconMap[step.icon] || Clock
              const isRunning = step.status === 'running'
              const isCompleted = step.status === 'completed'
              const isFailed = step.status === 'failed'
              const isWaiting = step.status === 'waiting'
              
              return (
                <div 
                  key={step.id || index}
                  className="flex items-center gap-2"
                >
                  <Icon 
                    className={`w-[18px] h-[18px] flex-shrink-0 ${isRunning ? 'animate-spin' : ''}`}
                    style={{ 
                      color: isCompleted 
                        ? '#22c55e' 
                        : isFailed 
                        ? '#ef4444'
                        : isWaiting
                        ? 'var(--project-text-muted)'
                        : 'var(--project-accent)' 
                    }}
                  />
                  <span 
                    className="text-xs"
                    style={{ 
                      color: isCompleted 
                        ? '#15803d' 
                        : isFailed
                        ? '#dc2626'
                        : isWaiting
                        ? 'var(--project-text-muted)'
                        : 'var(--project-text-secondary)' 
                    }}
                  >
                    {step.label}
                    {step.duration && !isCompleted && !isFailed && (
                      <span className="ml-1" style={{ color: 'var(--project-text-muted)' }}>
                        ({step.duration})
                      </span>
                    )}
                  </span>
                </div>
              )
            })}
          </div>
        )}
        
        {/* 时间戳 */}
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
}

/**
 * 格式化时间
 */
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

export default StreamingMessage


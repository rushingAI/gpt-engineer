import { ArrowUp, Loader2 } from 'lucide-react'

function ChatInput({ value, onChange, onSend, onKeyPress, disabled }) {
  return (
    <div className="project-input relative">
      <textarea
        value={value}
        onChange={(e) => onChange(e.target.value)}
        onKeyPress={onKeyPress}
        placeholder="输入消息，按 Enter 发送..."
        disabled={disabled}
        rows={2}
        className="w-full bg-transparent border-none outline-none resize-none pr-10"
        style={{
          color: 'var(--project-text-primary)',
          fontSize: '13px',
          lineHeight: '1.5'
        }}
      />
      {/* 圆形发送按钮 - 更小更紧凑 */}
      <button
        onClick={onSend}
        disabled={disabled || !value.trim()}
        className="project-primary-btn !p-0 w-7 h-7 !rounded-full flex items-center justify-center absolute bottom-1.5 right-1.5"
      >
        {disabled ? (
          <Loader2 className="h-3.5 w-3.5 animate-spin" />
        ) : (
          <ArrowUp className="h-3.5 w-3.5" />
        )}
      </button>
    </div>
  )
}

export default ChatInput


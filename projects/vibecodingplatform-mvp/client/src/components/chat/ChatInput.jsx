import '../../styles/ChatInput.css'

function ChatInput({ value, onChange, onSend, onKeyPress, disabled }) {
  return (
    <div className="chat-input-container">
      <textarea
        value={value}
        onChange={(e) => onChange(e.target.value)}
        onKeyPress={onKeyPress}
        placeholder="输入消息，按 Enter 发送..."
        disabled={disabled}
        rows={3}
        className="chat-input"
      />
      <button
        onClick={onSend}
        disabled={disabled || !value.trim()}
        className="send-button"
      >
        ✨ 发送
      </button>
    </div>
  )
}

export default ChatInput


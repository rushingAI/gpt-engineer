import { Send } from 'lucide-react'
import { Textarea } from '@/components/ui/textarea'
import { Button } from '@/components/ui/button'

function ChatInput({ value, onChange, onSend, onKeyPress, disabled }) {
  return (
    <div className="space-y-2">
      <Textarea
        value={value}
        onChange={(e) => onChange(e.target.value)}
        onKeyPress={onKeyPress}
        placeholder="输入消息，按 Enter 发送..."
        disabled={disabled}
        rows={3}
        className="resize-none"
      />
      <Button
        onClick={onSend}
        disabled={disabled || !value.trim()}
        size="sm"
        className="w-full"
      >
        <Send className="mr-2 h-4 w-4" />
        发送
      </Button>
    </div>
  )
}

export default ChatInput


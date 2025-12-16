import { Button } from '@/components/ui/button'

function Navbar() {
  return (
    <nav className="fixed top-0 left-0 right-0 z-50 backdrop-blur-md border-b border-black/0">
      <div className="max-w-7xl mx-auto px-6 h-20 flex items-center justify-between">
        {/* 左侧：Logo + 品牌名 */}
        <div className="flex items-center gap-3">
          <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-gray-900 to-gray-700 flex items-center justify-center shadow-sm">
            <span className="text-white font-bold text-base">BF</span>
          </div>
          <span className="text-xl font-bold tracking-tight" style={{ color: 'var(--landing-text-primary)' }}>
            BuildFast
          </span>
        </div>
        
        {/* 右侧：注册/登录按钮 */}
        <div className="flex items-center gap-2">
          <Button 
            variant="ghost" 
            className="text-sm font-medium hover:bg-black/5"
            style={{ color: 'var(--landing-text-secondary)' }}
          >
            登录
          </Button>
          <Button 
            className="bg-black hover:bg-gray-800 text-white shadow-sm text-sm font-medium px-5"
          >
            注册
          </Button>
        </div>
      </div>
    </nav>
  )
}

export default Navbar


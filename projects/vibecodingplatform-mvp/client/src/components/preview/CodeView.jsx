import { useState } from 'react'
import { FileCode, Sparkles } from 'lucide-react'

/**
 * CodeView - Lovable 风格：左侧文件树 + 右侧代码内容
 */
function CodeView({ files }) {
  const [selectedFile, setSelectedFile] = useState(null)

  if (!files || Object.keys(files).length === 0) {
    return (
      <div className="flex-1 flex items-center justify-center p-8">
        <div className="text-center space-y-3">
          {/* 现代线性图标 - 浅色圆形底座 */}
          <div className="inline-flex items-center justify-center w-14 h-14 rounded-full bg-black/5 mb-2">
            <Sparkles className="w-7 h-7" style={{ color: 'var(--project-text-primary)' }} />
          </div>
          <h3 className="text-base font-semibold" style={{ color: 'var(--project-text-primary)' }}>
            没有代码文件
          </h3>
          <p className="text-sm" style={{ color: 'var(--project-text-secondary)' }}>
            请先生成应用
          </p>
        </div>
      </div>
    )
  }

  const fileEntries = Object.entries(files).sort(([a], [b]) => a.localeCompare(b))
  
  // 自动选择第一个文件
  if (selectedFile === null && fileEntries.length > 0) {
    setSelectedFile(fileEntries[0][0])
  }

  const getFileName = (filepath) => {
    const parts = filepath.split('/')
    return parts[parts.length - 1]
  }

  return (
    <div className="flex-1 flex overflow-hidden">
      {/* 左侧：文件树 */}
      <div 
        className="w-[280px] border-r overflow-y-auto" 
        style={{ 
          borderColor: 'var(--project-border)',
          background: '#fafafa'
        }}
      >
        <div className="p-3 border-b" style={{ borderColor: 'var(--project-border)' }}>
          <h3 className="text-xs font-semibold" style={{ color: 'var(--project-text-secondary)' }}>
            FILES
          </h3>
        </div>
        <div className="p-2">
          {fileEntries.map(([filepath]) => (
            <button
              key={filepath}
              onClick={() => setSelectedFile(filepath)}
              className="w-full flex items-center gap-2 px-3 py-2 rounded-md text-left transition-all"
              style={{
                background: selectedFile === filepath ? 'rgba(0, 0, 0, 0.05)' : 'transparent',
                color: selectedFile === filepath ? 'var(--project-text-primary)' : 'var(--project-text-secondary)'
              }}
              onMouseEnter={(e) => {
                if (selectedFile !== filepath) {
                  e.currentTarget.style.background = 'rgba(0, 0, 0, 0.03)'
                }
              }}
              onMouseLeave={(e) => {
                if (selectedFile !== filepath) {
                  e.currentTarget.style.background = 'transparent'
                }
              }}
            >
              <FileCode className="h-3.5 w-3.5 flex-shrink-0" />
              <span className="text-xs font-mono truncate">{filepath}</span>
            </button>
          ))}
        </div>
      </div>
      
      {/* 右侧：代码内容 */}
      <div className="flex-1 overflow-auto" style={{ background: '#ffffff' }}>
        {selectedFile ? (
          <div className="h-full">
            {/* 文件名标题栏 */}
            <div 
              className="sticky top-0 px-4 py-2 border-b backdrop-blur-sm z-10"
              style={{ 
                borderColor: 'var(--project-border)',
                background: 'rgba(255, 255, 255, 0.8)'
              }}
            >
              <div className="flex items-center gap-2">
                <FileCode className="h-3.5 w-3.5" style={{ color: 'var(--project-text-secondary)' }} />
                <span className="text-xs font-mono font-medium" style={{ color: 'var(--project-text-primary)' }}>
                  {selectedFile}
                </span>
                <span className="ml-auto text-xs" style={{ color: 'var(--project-text-muted)' }}>
                  {files[selectedFile].split('\n').length} 行
                </span>
              </div>
            </div>
            {/* 代码内容 */}
            <pre 
              className="p-4 text-xs leading-relaxed font-mono"
              style={{ 
                color: 'var(--project-text-primary)',
                margin: 0,
                minHeight: '100%'
              }}
            >
              <code>{files[selectedFile]}</code>
            </pre>
          </div>
        ) : (
          <div className="flex items-center justify-center h-full">
            <p className="text-sm" style={{ color: 'var(--project-text-muted)' }}>
              选择一个文件查看代码
            </p>
          </div>
        )}
      </div>
    </div>
  )
}

export default CodeView


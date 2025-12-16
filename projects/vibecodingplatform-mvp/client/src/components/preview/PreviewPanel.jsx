import { Sparkles } from 'lucide-react'
import WebContainerPreview from './WebContainerPreview'

function PreviewPanel({ files, activeTab, project, onStepUpdate }) {
  console.log('PreviewPanel 渲染:', { 
    hasFiles: !!files, 
    fileCount: files ? Object.keys(files).length : 0,
    fileNames: files ? Object.keys(files) : [],
    activeTab,
    hasProject: !!project,
    hasStepCallback: !!onStepUpdate
  })

  if (!files || Object.keys(files).length === 0) {
    return (
      <div className="flex-1 flex items-center justify-center p-6">
        <div className="project-content-card max-w-md w-full p-8 text-center space-y-3">
          {/* 现代线性图标 - 浅色圆形底座 */}
          <div className="inline-flex items-center justify-center w-14 h-14 rounded-full bg-black/5 mb-2">
            <Sparkles className="w-7 h-7" style={{ color: 'var(--project-text-primary)' }} />
          </div>
          <h3 className="text-base font-semibold" style={{ color: 'var(--project-text-primary)' }}>
            还没有生成应用
          </h3>
          <p className="text-sm" style={{ color: 'var(--project-text-secondary)' }}>
            在左侧对话框中输入你的需求开始生成
          </p>
        </div>
      </div>
    )
  }

  // 统一使用 WebContainer 预览，传递步骤回调
  return (
    <WebContainerPreview 
      files={files} 
      activeTab={activeTab} 
      project={project}
      onStepUpdate={onStepUpdate}
    />
  )
}

export default PreviewPanel


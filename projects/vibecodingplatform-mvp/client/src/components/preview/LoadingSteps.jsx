import { Rocket, CheckCircle2, Loader2, Clock, Info } from 'lucide-react'

/**
 * LoadingSteps - 显示 WebContainer 启动步骤的加载组件
 */
function LoadingSteps({ currentStep, steps }) {
  const defaultSteps = [
    { id: 'boot', label: '正在启动容器...', duration: '2-5秒' },
    { id: 'mount', label: '挂载文件系统...', duration: '1秒' },
    { id: 'install', label: '安装依赖...', duration: '5-10秒' },
    { id: 'dev', label: '启动开发服务器...', duration: '2-3秒' },
  ]

  const stepsToShow = steps || defaultSteps

  return (
    <div className="flex-1 flex items-center justify-center p-6">
      <div className="project-content-card max-w-md w-full p-6">
        <div className="text-center mb-5">
          {/* 现代线性图标 - 浅色圆形底座 */}
          <div className="inline-flex items-center justify-center w-14 h-14 rounded-full bg-black/5 mb-3">
            <Rocket className="w-7 h-7" style={{ color: 'var(--project-text-primary)' }} />
          </div>
          <h3 className="text-base font-semibold mb-2" style={{ color: 'var(--project-text-primary)' }}>
            正在准备预览环境
          </h3>
          <p className="text-xs" style={{ color: 'var(--project-text-secondary)' }}>
            首次启动可能需要 10-20 秒
          </p>
        </div>

        <div className="space-y-2">
          {stepsToShow.map((step, index) => {
            const isActive = currentStep === step.id
            const isPast = stepsToShow.findIndex(s => s.id === currentStep) > index
            
            return (
              <div
                key={step.id}
                className="flex items-center gap-2.5 p-2.5 rounded-md transition-all border"
                style={{
                  background: isActive 
                    ? 'rgba(26, 26, 26, 0.03)' 
                    : isPast 
                    ? 'rgba(34, 197, 94, 0.03)' 
                    : 'transparent',
                  borderColor: isActive 
                    ? 'var(--project-accent)' 
                    : isPast 
                    ? '#22c55e' 
                    : 'var(--project-border)'
                }}
              >
                {/* 状态图标 - lucide-react 统一体系 */}
                <div className="flex-shrink-0">
                  {isPast ? (
                    <CheckCircle2 
                      className="w-[18px] h-[18px]" 
                      style={{ color: '#22c55e' }}
                    />
                  ) : isActive ? (
                    <Loader2 
                      className="w-[18px] h-[18px] animate-spin" 
                      style={{ color: 'var(--project-accent)' }}
                    />
                  ) : (
                    <Clock 
                      className="w-[18px] h-[18px]" 
                      style={{ color: 'var(--project-text-muted)' }}
                    />
                  )}
                </div>

                <div className="flex-1">
                  <div 
                    className="font-medium text-xs"
                    style={{
                      color: isActive 
                        ? 'var(--project-accent)' 
                        : isPast 
                        ? '#15803d' 
                        : 'var(--project-text-secondary)'
                    }}
                  >
                    {step.label}
                  </div>
                  {step.duration && !isPast && (
                    <div className="text-[10px] mt-0.5" style={{ color: 'var(--project-text-muted)' }}>
                      预计 {step.duration}
                    </div>
                  )}
                </div>
              </div>
            )
          })}
        </div>

        <div 
          className="mt-4 p-2.5 rounded-md border"
          style={{
            background: 'rgba(59, 130, 246, 0.03)',
            borderColor: 'rgba(59, 130, 246, 0.15)'
          }}
        >
          <p className="text-[10px] flex items-start gap-1.5" style={{ color: '#1d4ed8' }}>
            <Info className="w-3.5 h-3.5 flex-shrink-0" />
            <span>
              后续切换应用时会快很多(容器已缓存)
            </span>
          </p>
        </div>
      </div>
    </div>
  )
}

export default LoadingSteps

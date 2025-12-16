import { useState, useEffect, useRef } from 'react'
import { AlertTriangle, XCircle, Sparkles } from 'lucide-react'
import { webContainerManager, supportsWebContainers, getUnsupportedReason, convertToFileSystemTree, mergeWithPreset } from '@/utils/webcontainer'
import { getProjectTheme, getProjectThemeOverrides } from '@/utils/theme'
import LoadingSteps from './LoadingSteps'

/**
 * WebContainerPreview - 使用 WebContainers 预览 React 应用
 */
function WebContainerPreview({ files, activeTab, project, onStepUpdate }) {
  const [currentStep, setCurrentStep] = useState(null)
  const [previewUrl, setPreviewUrl] = useState(null)
  const [error, setError] = useState(null)
  const iframeRef = useRef(null)
  const containerRef = useRef(null)
  
  // 获取项目主题信息
  const themeName = project ? getProjectTheme(project) : 'teal'
  const themeOverrides = project ? getProjectThemeOverrides(project) : {}
  
  // 内部步骤更新函数
  const updateStep = (stepId, status) => {
    setCurrentStep(status === 'completed' ? null : stepId)
    onStepUpdate?.(stepId, status)
  }

  useEffect(() => {
    if (!supportsWebContainers()) {
      setError(getUnsupportedReason())
      return
    }

    if (!files || Object.keys(files).length === 0) {
      return
    }

    let isActive = true

    const startPreview = async () => {
      try {
        setError(null)
        setPreviewUrl(null)

        // 步骤 1: 启动容器
        updateStep('boot', 'running')
        console.log('🚀 Starting WebContainer...')
        const container = await webContainerManager.getContainer()
        
        if (!isActive) return
        containerRef.current = container
        updateStep('boot', 'completed')

        // 步骤 2: 挂载文件系统
        updateStep('mount', 'running')
        console.log('📁 Mounting files...')
        console.log('📄 Original AI files:', Object.keys(files))
        console.log('🎨 Project theme:', themeName)
        
        // 🎨 合并 Cyberpunk 预设和 AI 生成的业务文件，并应用主题
        const finalFiles = mergeWithPreset(files, themeName, themeOverrides)
        
        // 转换文件格式为 WebContainer FileSystemTree
        const fileSystemTree = convertToFileSystemTree(finalFiles)
        console.log('📄 Final file tree:', Object.keys(fileSystemTree))
        
        await container.mount(fileSystemTree)
        
        // 验证文件是否正确挂载
        try {
          const packageJson = await container.fs.readFile('package.json', 'utf-8')
          console.log('✅ package.json 存在:', packageJson.slice(0, 100))
        } catch (err) {
          console.error('❌ package.json 不存在或无法读取')
          throw new Error('package.json 文件缺失')
        }
        
        if (!isActive) return
        updateStep('mount', 'completed')

        // 步骤 3: 安装依赖
        updateStep('install', 'running')
        console.log('📦 Installing dependencies...')
        
        // 捕获 npm install 的输出
        const installProcess = await container.spawn('npm', ['install'])
        
        // 收集输出用于调试
        let installOutput = ''
        let installError = ''
        
        installProcess.output.pipeTo(new WritableStream({
          write(data) {
            const text = data
            installOutput += text
            console.log('npm install:', text)
          }
        }))
        
        // 等待安装完成
        const installExitCode = await installProcess.exit
        
        if (installExitCode !== 0) {
          console.error('❌ npm install failed')
          console.error('Exit code:', installExitCode)
          console.error('Output:', installOutput)
          updateStep('install', 'failed')
          throw new Error(`npm install 失败 (exit code: ${installExitCode})\n\n输出:\n${installOutput.slice(-500)}`)
        }
        
        console.log('✅ npm install succeeded')
        
        if (!isActive) return
        updateStep('install', 'completed')

        // 步骤 4: 启动开发服务器
        updateStep('dev', 'running')
        console.log('🎯 Starting dev server...')
        
        // 启动 dev server (不等待它结束,因为它是长期运行的进程)
        container.spawn('npm', ['run', 'dev'])

        // 监听服务器启动
        container.on('server-ready', (port, url) => {
          if (!isActive) return
          console.log('✅ Server ready:', url)
          updateStep('dev', 'completed')
          setPreviewUrl(url)
        })

      } catch (err) {
        console.error('WebContainer error:', err)
        if (isActive) {
          setError(err.message || '启动失败,请刷新页面重试')
          // 标记当前步骤失败
          if (currentStep) {
            updateStep(currentStep, 'failed')
          }
        }
      }
    }

    startPreview()

    return () => {
      isActive = false
    }
  }, [files, themeName, themeOverrides])

  // 显示浏览器不支持的错误
  if (error && error.includes('不支持')) {
    return (
      <div className="flex-1 flex items-center justify-center p-6">
        <div className="project-content-card max-w-md w-full p-6 text-center" style={{ borderColor: '#fca5a5' }}>
          {/* 现代线性图标 - 警告状态 */}
          <div className="inline-flex items-center justify-center w-14 h-14 rounded-full bg-red-50 mb-3">
            <AlertTriangle className="w-7 h-7 text-red-500" />
          </div>
          <h3 className="text-base font-semibold mb-2" style={{ color: 'var(--project-text-primary)' }}>
            浏览器不兼容
          </h3>
          <p className="mb-3 text-sm" style={{ color: 'var(--project-text-secondary)' }}>{error}</p>
          <div 
            className="text-xs text-left p-3 rounded-md space-y-2"
            style={{ background: 'var(--project-card)' }}
          >
            <p className="font-semibold" style={{ color: 'var(--project-text-primary)' }}>建议:</p>
            <ul className="list-disc list-inside space-y-1" style={{ color: 'var(--project-text-secondary)' }}>
              <li>使用 Chrome 89+ 或 Firefox 91+ 浏览器</li>
              <li>在桌面设备上访问 (移动端不支持)</li>
              <li>使用"生成分享链接"功能查看静态预览</li>
            </ul>
          </div>
        </div>
      </div>
    )
  }

  // 显示启动错误
  if (error) {
    return (
      <div className="flex-1 flex items-center justify-center p-6">
        <div className="project-content-card max-w-md w-full p-6 text-center" style={{ borderColor: '#fca5a5' }}>
          {/* 现代线性图标 - 错误状态 */}
          <div className="inline-flex items-center justify-center w-14 h-14 rounded-full bg-red-50 mb-3">
            <XCircle className="w-7 h-7 text-red-500" />
          </div>
          <h3 className="text-base font-semibold mb-2" style={{ color: 'var(--project-text-primary)' }}>
            启动失败
          </h3>
          <p className="mb-3 text-sm" style={{ color: 'var(--project-text-secondary)' }}>{error}</p>
          <button
            onClick={() => window.location.reload()}
            className="project-primary-btn"
          >
            刷新页面重试
          </button>
        </div>
      </div>
    )
  }

  // 显示加载步骤
  if (currentStep) {
    return <LoadingSteps currentStep={currentStep} />
  }

  // 显示预览 - 完全铺满
  if (previewUrl) {
    return (
      <div className="w-full h-full" style={{ display: 'flex', flexDirection: 'column' }}>
        <iframe
          ref={iframeRef}
          src={previewUrl}
          className="w-full h-full border-0"
          title="WebContainer Preview"
          sandbox="allow-scripts allow-same-origin allow-forms allow-modals allow-popups allow-downloads"
          style={{ 
            background: 'white',
            display: 'block',
            minHeight: 0,
            flex: 1
          }}
        />
      </div>
    )
  }

  // 默认状态
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

export default WebContainerPreview

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
        
        // 添加内存检查和错误处理
        let container = null
        try {
          container = await webContainerManager.getContainer()
        } catch (bootError) {
          console.error('WebContainer boot error:', bootError)
          
          // 如果是内存错误，尝试清理并重试一次
          if (bootError.message && bootError.message.includes('memory')) {
            console.warn('⚠️ 检测到内存错误，尝试清理并重试...')
            await webContainerManager.teardown()
            
            // 强制垃圾回收（如果可用）
            if (window.gc) {
              window.gc()
            }
            
            // 等待一小段时间让内存释放
            await new Promise(resolve => setTimeout(resolve, 1000))
            
            // 重试一次
            try {
              container = await webContainerManager.getContainer()
            } catch (retryError) {
              throw new Error('WebContainer 内存不足。请关闭其他标签页后刷新页面重试。')
            }
          } else {
            throw bootError
          }
        }
        
        if (!container) {
          throw new Error('WebContainer 启动失败：container 为 null')
        }
        
        if (!isActive) return
        containerRef.current = container
        updateStep('boot', 'completed')
        console.log('✅ WebContainer 启动成功')

        // 步骤 2: 挂载文件系统
        updateStep('mount', 'running')
        console.log('📁 Mounting files...')
        console.log('📄 Original AI files:', Object.keys(files))
        console.log('🎨 Project theme:', themeName)
        
        // 🎨 合并 Cyberpunk 预设和 AI 生成的业务文件，并应用主题
        const finalFiles = mergeWithPreset(files, themeName, themeOverrides)
        console.log('📄 Merged files count:', Object.keys(finalFiles).length)
        
        // 转换文件格式为 WebContainer FileSystemTree
        const fileSystemTree = convertToFileSystemTree(finalFiles)
        console.log('📄 Final file tree:', Object.keys(fileSystemTree))
        console.log('📄 File tree structure:', JSON.stringify(Object.keys(fileSystemTree).slice(0, 5)))
        
        // 确保 container 仍然有效
        if (!container) {
          throw new Error('Container is null before mount')
        }
        
        console.log('🔧 Mounting file system...')
        await container.mount(fileSystemTree)
        console.log('✅ File system mounted successfully')
        
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

        // 步骤 2.5: 注入批准的依赖（从 vibe.meta.json 读取）
        try {
          const vibeMetaContent = await container.fs.readFile('vibe.meta.json', 'utf-8')
          const vibeMeta = JSON.parse(vibeMetaContent)
          const approvedDeps = vibeMeta?.dependencies?.approved || {}
          
          if (Object.keys(approvedDeps).length > 0) {
            console.log('💉 注入批准的依赖:', Object.keys(approvedDeps))
            
            // 读取 package.json
            const packageJsonContent = await container.fs.readFile('package.json', 'utf-8')
            const packageJson = JSON.parse(packageJsonContent)
            
            // 合并批准的依赖
            packageJson.dependencies = {
              ...packageJson.dependencies,
              ...approvedDeps
            }
            
            // 写回 package.json
            await container.fs.writeFile(
              'package.json',
              JSON.stringify(packageJson, null, 2)
            )
            
            console.log('✅ 已注入依赖到 package.json:', Object.keys(approvedDeps).join(', '))
          } else {
            console.log('ℹ️ 无需注入额外依赖')
          }
        } catch (err) {
          console.warn('⚠️ 注入依赖失败（非致命）:', err.message)
          // 不阻断流程，继续安装
        }

        // 步骤 3: 安装依赖（优化内存使用）
        updateStep('install', 'running')
        console.log('📦 Installing dependencies...')
        
        // 使用优化的npm参数
        // --prefer-offline: 优先使用缓存
        // --no-audit: 跳过审计以减少内存和网络请求
        // --progress=false: 禁用进度条减少输出
        const installProcess = await container.spawn('npm', [
          'install',
          '--prefer-offline',
          '--no-audit',
          '--progress=false'
        ])
        
        // 收集输出用于调试（限制大小避免内存溢出）
        let installOutput = ''
        const MAX_OUTPUT_SIZE = 5000 // 限制输出大小
        
        installProcess.output.pipeTo(new WritableStream({
          write(data) {
            const text = data
            // 只保留最后5000个字符
            installOutput = (installOutput + text).slice(-MAX_OUTPUT_SIZE)
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
          
          // 检查是否是网络错误
          const isNetworkError = installOutput.includes('network') || 
                                 installOutput.includes('ETIMEDOUT') ||
                                 installOutput.includes('ENOTFOUND') ||
                                 installOutput.includes('proxy')
          
          if (isNetworkError) {
            throw new Error('网络连接失败：无法下载依赖包。请检查网络连接后重试。\n\n' +
                          '如果问题持续，可能是：\n' +
                          '1. 网络连接不稳定\n' +
                          '2. npm 镜像源无法访问\n' +
                          '3. 防火墙或代理设置阻止了连接')
          }
          
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
      // 清理容器引用，但不销毁全局实例（单例模式）
      if (containerRef.current) {
        console.log('🧹 清理 WebContainer 引用')
        containerRef.current = null
      }
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
    const isMemoryError = error.includes('内存') || error.includes('memory') || error.includes('Memory')
    const isNetworkError = error.includes('网络') || error.includes('network') || error.includes('ETIMEDOUT') || error.includes('proxy')
    
    return (
      <div className="flex-1 flex items-center justify-center p-6">
        <div className="project-content-card max-w-lg w-full p-6" style={{ borderColor: '#fca5a5' }}>
          {/* 现代线性图标 - 错误状态 */}
          <div className="text-center mb-4">
          <div className="inline-flex items-center justify-center w-14 h-14 rounded-full bg-red-50 mb-3">
            <XCircle className="w-7 h-7 text-red-500" />
          </div>
          <h3 className="text-base font-semibold mb-2" style={{ color: 'var(--project-text-primary)' }}>
              {isMemoryError ? 'WebAssembly 内存不足' : isNetworkError ? '网络连接失败' : '启动失败'}
          </h3>
          <p className="mb-3 text-sm" style={{ color: 'var(--project-text-secondary)' }}>{error}</p>
          </div>
          
          {/* 内存错误提示 */}
          {isMemoryError && (
            <div 
              className="text-xs text-left p-4 rounded-lg space-y-3 mb-4"
              style={{ background: 'var(--project-card)', border: '1px solid #fecaca' }}
            >
              <p className="font-semibold text-sm" style={{ color: 'var(--project-text-primary)' }}>💡 解决方法：</p>
              <ul className="list-disc list-inside space-y-2" style={{ color: 'var(--project-text-secondary)' }}>
                <li><strong>关闭其他标签页</strong> - 特别是占用大量内存的页面</li>
                <li><strong>重启浏览器</strong> - 清理内存缓存</li>
                <li><strong>使用 Chrome</strong> - 推荐 Chrome 89+ 或 Edge 浏览器</li>
                <li><strong>检查系统内存</strong> - 确保电脑有足够的可用内存（建议 8GB+）</li>
                <li><strong>禁用浏览器扩展</strong> - 某些扩展可能占用大量内存</li>
              </ul>
              
              <div className="pt-2 mt-3 border-t border-red-200">
                <p className="text-xs" style={{ color: 'var(--project-text-secondary)' }}>
                  <strong>技术说明：</strong>WebContainer 需要 WebAssembly 来运行 Node.js 环境。如果浏览器内存不足，WebAssembly 将无法分配必要的内存空间。
                </p>
              </div>
            </div>
          )}
          
          {/* 网络错误提示 */}
          {isNetworkError && (
            <div 
              className="text-xs text-left p-4 rounded-lg space-y-3 mb-4"
              style={{ background: 'var(--project-card)', border: '1px solid #fecaca' }}
            >
              <p className="font-semibold text-sm" style={{ color: 'var(--project-text-primary)' }}>🌐 解决方法：</p>
              <ul className="list-disc list-inside space-y-2" style={{ color: 'var(--project-text-secondary)' }}>
                <li><strong>检查网络连接</strong> - 确保可以正常访问互联网</li>
                <li><strong>重试</strong> - 网络波动可能导致临时失败，刷新重试即可</li>
                <li><strong>关闭 VPN/代理</strong> - 某些代理可能阻止 npm 访问</li>
                <li><strong>检查防火墙</strong> - 确保防火墙没有阻止浏览器网络请求</li>
                <li><strong>使用移动热点</strong> - 如果公司网络有限制，可以尝试手机热点</li>
              </ul>
              
              <div className="pt-2 mt-3 border-t border-red-200">
                <p className="text-xs" style={{ color: 'var(--project-text-secondary)' }}>
                  <strong>技术说明：</strong>需要网络连接从 npm 官方源下载依赖包。
                </p>
              </div>
            </div>
          )}
          
          <div className="flex gap-3">
          <button
            onClick={() => window.location.reload()}
              className="project-primary-btn flex-1"
          >
            刷新页面重试
          </button>
            {isMemoryError && (
              <button
                onClick={() => {
                  // 尝试清理并重新加载
                  webContainerManager.teardown().then(() => {
                    setTimeout(() => window.location.reload(), 500)
                  })
                }}
                className="project-secondary-btn flex-1"
              >
                强制清理重试
              </button>
            )}
          </div>
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

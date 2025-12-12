import { useState } from 'react'
import { Sandpack } from '@codesandbox/sandpack-react'
import TabBar from './TabBar'
import '../../styles/PreviewPanel.css'

function PreviewPanel({ files, activeTab }) {
  console.log('PreviewPanel 渲染:', { 
    hasFiles: !!files, 
    fileCount: files ? Object.keys(files).length : 0,
    fileNames: files ? Object.keys(files) : [],
    activeTab 
  })

  if (!files || Object.keys(files).length === 0) {
    return (
      <div className="preview-panel">
        <div className="preview-empty">
          <div className="empty-icon">📭</div>
          <h3>还没有生成应用</h3>
          <p>在左侧对话框中输入你的需求开始生成</p>
        </div>
      </div>
    )
  }

  return (
    <div className="preview-panel">
      
      <div className="preview-content" style={{ 
        width: '100%',
        height: 'calc(100vh - 130px)',
        overflow: 'hidden',
        background: '#f8fafc'
      }}>
        <div style={{ width: '100%', height: '100%' }}>
          {console.log('渲染 Sandpack，模式:', activeTab)}
          <Sandpack
            key={`${activeTab}-${JSON.stringify(files)}`}
            template="static"
            files={files}
            options={{
              showNavigator: activeTab === 'code',
              showTabs: activeTab === 'code',
              showLineNumbers: activeTab === 'code',
              showInlineErrors: true,
              wrapContent: true,
              editorHeight: '100%',
              editorWidthPercentage: activeTab === 'sandbox' ? 0 : 60,
              layout: activeTab === 'sandbox' ? 'preview' : 'code',
              activeFile: '/index.html',
              autorun: true,
              autoReload: true,
            }}
            theme="auto"
          />
        </div>
      </div>
    </div>
  )
}

export default PreviewPanel


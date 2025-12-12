import { useState } from 'react'
import { Sandpack } from '@codesandbox/sandpack-react'
import TabBar from './TabBar'
import '../../styles/PreviewPanel.css'

function PreviewPanel({ files }) {
  const [activeTab, setActiveTab] = useState('sandbox') // 'sandbox' or 'code'

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
      <TabBar activeTab={activeTab} onTabChange={setActiveTab} />
      
      <div className="preview-content">
        <Sandpack
          key={JSON.stringify(files)}
          template="static"
          files={files}
          options={{
            showNavigator: activeTab === 'code',
            showTabs: activeTab === 'code',
            showLineNumbers: activeTab === 'code',
            showInlineErrors: true,
            wrapContent: true,
            editorHeight: '100%',
            layout: activeTab === 'sandbox' ? 'preview' : 'code',
            activeFile: '/index.html',
            autorun: true,
            autoReload: true,
          }}
          theme="auto"
        />
      </div>
    </div>
  )
}

export default PreviewPanel


import { Sandpack } from '@codesandbox/sandpack-react'
import { Card, CardContent } from '@/components/ui/card'

function PreviewPanel({ files, activeTab }) {
  console.log('PreviewPanel 渲染:', { 
    hasFiles: !!files, 
    fileCount: files ? Object.keys(files).length : 0,
    fileNames: files ? Object.keys(files) : [],
    activeTab 
  })

  if (!files || Object.keys(files).length === 0) {
    return (
      <div className="flex-1 bg-lovable-gray-50 flex items-center justify-center p-8">
        <Card className="max-w-md w-full shadow-lg">
          <CardContent className="p-12 text-center space-y-4">
            <div className="text-6xl">📭</div>
            <h3 className="text-xl font-semibold text-lovable-gray-900">
              还没有生成应用
            </h3>
            <p className="text-gray-600">
              在左侧对话框中输入你的需求开始生成
            </p>
          </CardContent>
        </Card>
      </div>
    )
  }

  return (
    <div className="flex-1 bg-lovable-gray-50 flex flex-col overflow-hidden">
      <div className="flex-1 m-4 rounded-xl overflow-hidden shadow-lg bg-white border border-gray-200" style={{ display: 'flex', flexDirection: 'column' }}>
        {console.log('渲染 Sandpack，模式:', activeTab)}
        <div style={{ flex: 1, minHeight: 0 }}>
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
            theme="light"
            style={{ height: '100%', width: '100%' }}
          />
        </div>
      </div>
    </div>
  )
}

export default PreviewPanel


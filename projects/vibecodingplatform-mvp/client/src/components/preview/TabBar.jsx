function TabBar({ activeTab, onTabChange }) {
  console.log('TabBar 渲染:', { activeTab })
  
  return (
    <div 
      className="tab-bar" 
      style={{ 
        backgroundColor: '#ffffff',
        height: '60px',
        minHeight: '60px',
        maxHeight: '60px',
        position: 'relative',
        zIndex: 1000,
        flexShrink: 0,
        borderBottom: '2px solid #e2e8f0',
        display: 'flex',
        alignItems: 'center',
        gap: '0.5rem',
        padding: '0 1.5rem',
        width: '100%',
        boxSizing: 'border-box'
      }}
    >
      <button
        className={`tab-button ${activeTab === 'sandbox' ? 'active' : ''}`}
        onClick={() => {
          console.log('切换到 Sandbox')
          onTabChange('sandbox')
        }}
        style={{
          padding: '0.6rem 1.5rem',
          background: activeTab === 'sandbox' ? '#6366f1' : '#f8fafc',
          color: activeTab === 'sandbox' ? 'white' : '#64748b',
          border: `2px solid ${activeTab === 'sandbox' ? '#6366f1' : '#e2e8f0'}`,
          borderRadius: '8px',
          fontSize: '1rem',
          fontWeight: '600',
          cursor: 'pointer'
        }}
      >
        👁️ Sandbox
      </button>
      <button
        className={`tab-button ${activeTab === 'code' ? 'active' : ''}`}
        onClick={() => {
          console.log('切换到 Code')
          onTabChange('code')
        }}
        style={{
          padding: '0.6rem 1.5rem',
          background: activeTab === 'code' ? '#6366f1' : '#f8fafc',
          color: activeTab === 'code' ? 'white' : '#64748b',
          border: `2px solid ${activeTab === 'code' ? '#6366f1' : '#e2e8f0'}`,
          borderRadius: '8px',
          fontSize: '1rem',
          fontWeight: '600',
          cursor: 'pointer'
        }}
      >
        {'</>'} Code
      </button>
    </div>
  )
}

export default TabBar


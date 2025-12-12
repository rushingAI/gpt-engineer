import '../../styles/TabBar.css'

function TabBar({ activeTab, onTabChange }) {
  return (
    <div className="tab-bar">
      <button
        className={`tab-button ${activeTab === 'sandbox' ? 'active' : ''}`}
        onClick={() => onTabChange('sandbox')}
      >
        👁️ Sandbox
      </button>
      <button
        className={`tab-button ${activeTab === 'code' ? 'active' : ''}`}
        onClick={() => onTabChange('code')}
      >
        {'</>'} Code
      </button>
    </div>
  )
}

export default TabBar


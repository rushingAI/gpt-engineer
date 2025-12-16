function ExamplePrompts({ examples, onSelectExample, loading }) {
  return (
    <div className="space-y-8 animate-slide-up">
      {/* 标题 */}
      <div className="text-center">
        <p 
          className="text-sm font-medium uppercase tracking-wider"
          style={{ color: 'var(--landing-text-muted)' }}
        >
          快速开始
        </p>
      </div>
      
      {/* Chip 网格 - 更紧凑的间距 */}
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 max-w-3xl mx-auto">
        {examples.map((example, index) => (
          <button
            key={index}
            onClick={() => !loading && onSelectExample(example)}
            disabled={loading}
            className="landing-chip text-left"
            style={{
              opacity: loading ? 0.4 : 1,
              cursor: loading ? 'not-allowed' : 'pointer'
            }}
          >
            <p 
              className="text-sm leading-relaxed font-medium"
              style={{ color: 'var(--landing-text-secondary)' }}
            >
              {example}
            </p>
          </button>
        ))}
      </div>
    </div>
  )
}

export default ExamplePrompts


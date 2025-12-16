function Hero() {
  return (
    <div className="text-center space-y-7 animate-slide-down">
      {/* 主标题 - 大气、确保可见 */}
      <h1 
        className="text-3xl sm:text-4xl lg:text-5xl font-extrabold leading-tight"
        style={{ 
          color: '#0f0f0f',
          letterSpacing: '-0.025em',
          fontWeight: 800
        }}
      >
        把你的创意做成产品
      </h1>
      
      {/* 副标题 */}
      <p 
        className="text-sm sm:text-base lg:text-lg max-w-3xl mx-auto leading-relaxed font-normal"
        style={{ 
          color: '#525252'
        }}
      >
        一句话生成可运行应用，支持持续迭代与上线
      </p>
    </div>
  )
}

export default Hero


/**
 * 轻量 hash 函数（djb2 算法）
 * 用于 console error 去重，无需 crypto 强 hash
 */
function simpleHash(str) {
  let hash = 5381
  for (let i = 0; i < str.length; i++) {
    hash = ((hash << 5) + hash) + str.charCodeAt(i)
  }
  return (hash >>> 0).toString(36)
}

export class BuildReportCollector {
  constructor({ runId, prompt, themeName }) {
    this.runId = runId
    this.prompt = prompt
    this.themeName = themeName
    this.startedAt = new Date().toISOString()
    
    // 从 vibe.meta.json 读取（若不存在则为 null）
    this.telemetry = null
    this.l0 = null
    this.qualityGates = null
    
    this.phases = { install: null, dev: null, render: null }
    this.deps = { approved: {}, injected: [], injectError: null }
    this.errors = {
      console: { total: 0, uniqueCount: 0, samples: [], _seen: new Set() },
      classified: { INSTALL: 0, DEPENDENCY: 0, BUILD: 0, EXPORT: 0, RUNTIME: 0 }
    }
  }
  
  setTelemetry(telemetry) { this.telemetry = telemetry }
  setL0(l0) { this.l0 = l0 }
  setQualityGates(qg) { this.qualityGates = qg }
  
  // 补齐 setDeps 方法
  setDeps(deps) {
    this.deps = { ...this.deps, ...deps }
  }
  
  // 补齐 _hash 方法
  _hash(text) {
    return simpleHash(text)
  }
  
  phaseStart(name) {
    this.phases[name] = { 
      status: 'running', 
      _startMs: Date.now(),
      startedAt: new Date().toISOString() 
    }
  }
  
  phaseEnd(name, { status, exitCode, logTail, url, port, signal }) {
    const phase = this.phases[name]
    if (!phase) return
    
    const endMs = Date.now()
    phase.status = status
    phase.endedAt = new Date().toISOString()
    phase.duration_ms = endMs - (phase._startMs || endMs)
    delete phase._startMs
    
    if (exitCode !== undefined) phase.exitCode = exitCode
    if (logTail) phase.logTail = logTail.slice(-5000)
    if (url) phase.url = url
    if (port) phase.port = port
    // 记录渲染信号来源
    if (signal) phase.signal = signal
  }
  
  addConsoleError(message, source = 'iframe') {
    const hash = this._hash(message)
    this.errors.console.total++
    if (!this.errors.console._seen.has(hash)) {
      this.errors.console._seen.add(hash)
      this.errors.console.uniqueCount++
      if (this.errors.console.samples.length < 20) {
        this.errors.console.samples.push(message.slice(0, 500))
      }
    }
    const category = ErrorClassifier.classify(message)
    this.errors.classified[category]++
  }
  
  finalize() {
    const { _seen, ...consoleErrors } = this.errors.console
    return {
      runId: this.runId,
      timestamp: new Date().toISOString(),
      prompt: this.prompt,
      themeName: this.themeName,
      telemetry: this.telemetry,
      l0: this.l0,
      qualityGates: this.qualityGates,
      phases: this.phases,
      deps: this.deps,
      errors: { console: consoleErrors, classified: this.errors.classified }
    }
  }
}

export class ErrorClassifier {
  // 显式优先级数组，不依赖对象顺序
  static ORDER = ['INSTALL', 'DEPENDENCY', 'EXPORT', 'BUILD', 'RUNTIME']
  
  static PATTERNS = {
    // 安装阶段错误（最高优先级）
    INSTALL: [
      /npm ERR!/i, 
      /ERESOLVE/i, 
      /ETARGET/i, 
      /ENOTFOUND/i, 
      /ETIMEDOUT/i, 
      /network/i, 
      /proxy/i
    ],
    // 依赖解析错误
    DEPENDENCY: [
      /Failed to resolve import/i, 
      /Cannot find module/i, 
      /Module not found/i,
      /Could not resolve/i
    ],
    // 导出错误
    EXPORT: [
      /does not provide an export/i, 
      /is not exported/i, 
      /export.*not found/i,
      /has no exported member/i
    ],
    // 构建错误（收紧，避免误判）
    BUILD: [
      /Failed to parse source/i, 
      /SyntaxError/i, 
      /ts\(\d+\)/i,  // TypeScript 错误码格式 ts(2304)
      /\[vite\].*error/i,
      /\[vite\].*failed/i,
      /Internal server error/i,
      /Failed to load module script/i,
      /Build failed/i,
      /Transform failed/i
    ],
    // 运行时错误（默认兜底）
    RUNTIME: [
      /TypeError/i, 
      /ReferenceError/i, 
      /Cannot read properties/i, 
      /Uncaught/i,
      /is not a function/i,
      /is undefined/i
    ]
  }
  
  static classify(message) {
    // 按显式 ORDER 顺序匹配，确保优先级稳定
    for (const category of this.ORDER) {
      const patterns = this.PATTERNS[category]
      if (patterns && patterns.some(p => p.test(message))) {
        return category
      }
    }
    return 'RUNTIME'  // 默认
  }
}


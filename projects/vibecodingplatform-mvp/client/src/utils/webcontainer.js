/**
 * WebContainer 工具函数
 * 用于检测浏览器兼容性和管理 WebContainer 实例
 */

import { BASE_PRESET_FILES, PROTECTED_PATHS } from './cyberpunkPreset.js'
import { getTheme } from './themes.js'

/**
 * 过滤 AI 生成的文件，只保留允许的业务文件
 * 
 * 策略（与后端 policy_manager 一致）:
 * - 允许写入: src/pages/**, src/features/**, src/components/generated/**, 
 *            src/lib/generated/**, src/hooks/generated/**, src/__tests__/**, tests/**
 * - 禁止覆盖: 受保护的模板文件（package.json, vite.config, src/main.tsx 等）
 * 
 * @param {Object} files - AI 生成的文件字典
 * @returns {Object} 过滤后的文件字典
 */
export function filterGeneratedFiles(files) {
  // 允许的文件路径模式（中等隔离级别 + CSS Modules 支持）
  // 注意：这些模式应与后端 generation_policy.json 的 allowlist_patterns 保持一致
  const allowedPatterns = [
    /^src\/pages\//,                    // 允许页面文件
    /^src\/features\//,                 // 允许功能模块
    /^src\/components\/generated\//,    // 允许生成的业务组件
    /^src\/lib\/generated\//,           // 允许生成的业务逻辑
    /^src\/hooks\/generated\//,         // 允许生成的自定义 hooks
    /^src\/__tests__\//,                // 允许测试文件
    /^tests\//,                         // 允许测试目录
    /^src\/(components|lib|hooks)\/generated\/.*\.module\.css$/,  // 允许 CSS Modules（仅限 generated 目录下）
    /^vibe\.meta\.json$/,               // 允许 vibe.meta.json（元数据文件）
  ];

  const filteredFiles = {};
  let blockedCount = 0;
  let allowedCount = 0;
  let protectedCount = 0;
  
  for (const [path, content] of Object.entries(files)) {
    // 移除开头的 /
    const cleanPath = path.startsWith('/') ? path.slice(1) : path;
    
    // 1. 检查是否在受保护路径列表中（黑名单，优先级最高）
    const isProtected = PROTECTED_PATHS.some(pattern => pattern.test(cleanPath));
    
    if (isProtected) {
      console.warn(`🛡️  Blocked AI write to protected file: ${cleanPath}`);
      protectedCount++;
      continue;
    }
    
    // 2. 检查是否在允许列表中（白名单）
    const isAllowed = allowedPatterns.some(pattern => pattern.test(cleanPath));
    
    if (isAllowed) {
      filteredFiles[cleanPath] = content;
      allowedCount++;
    } else {
      console.warn(`🚫 Blocked AI write to unauthorized path: ${cleanPath}`);
      blockedCount++;
    }
  }
  
  console.log(`✅ File filtering complete: ${allowedCount} allowed, ${protectedCount} protected, ${blockedCount} blocked`);
  
  return filteredFiles;
}

/**
 * 合并 Cyberpunk 预设文件和 AI 生成的业务文件，并应用主题
 * @param {Object} aiFiles - AI 生成的文件字典
 * @param {string} themeName - 主题名称（默认 'teal'）
 * @param {Object} themeOverrides - 主题覆盖变量（可选）
 * @returns {Object} 合并后的完整文件字典
 */
export function mergeWithPreset(aiFiles, themeName = 'teal', themeOverrides = {}) {
  console.log(`🎨 Merging files with Cyberpunk preset (theme: ${themeName})...`);
  
  // 获取主题配置
  const theme = getTheme(themeName);
  
  // 克隆预设文件并注入主题
  const presetFilesWithTheme = { ...BASE_PRESET_FILES };
  
  // 🔧 智能合并 package.json（在过滤前处理，允许 AI 添加新依赖）
  const aiPackageJsonKey = Object.keys(aiFiles).find(
    key => key === 'package.json' || key === '/package.json'
  );
  if (aiPackageJsonKey) {
    const aiPackageJson = aiFiles[aiPackageJsonKey];
    presetFilesWithTheme['package.json'] = mergePackageJson(
      BASE_PRESET_FILES['package.json'],
      aiPackageJson
    );
    console.log(`  ↳ Merged package.json with AI dependencies`);
  }
  
  // 过滤 AI 文件（业务文件）
  const filteredAiFiles = filterGeneratedFiles(aiFiles);
  
  // 在 index.css 中注入主题变量
  if (presetFilesWithTheme['src/index.css']) {
    const originalCss = presetFilesWithTheme['src/index.css'];
    const themeVariables = generateThemeVariablesCSS(theme, themeOverrides);
    
    // 在 :root 块中注入主题变量（替换默认值）
    const updatedCss = injectThemeVariables(originalCss, themeVariables);
    presetFilesWithTheme['src/index.css'] = updatedCss;
    
    console.log(`  ↳ Theme variables injected into index.css`);
  }
  
  // 预设文件优先，AI 文件覆盖（但因为过滤了，实际上不会覆盖预设）
  const mergedFiles = {
    ...presetFilesWithTheme,
    ...filteredAiFiles
  };
  
  console.log(`📦 Total files in merged tree: ${Object.keys(mergedFiles).length}`);
  console.log('📋 Preset files:', Object.keys(BASE_PRESET_FILES).join(', '));
  console.log('📋 AI business files:', Object.keys(filteredAiFiles).join(', '));
  
  return mergedFiles;
}

// 依赖白名单（与后端策略同步）
// 🤖 此部分由 backend/scripts/sync_dependency_whitelist.py 自动生成
// 请勿手动修改，运行 python backend/scripts/sync_dependency_whitelist.py 更新
const ALLOWED_DEPENDENCIES = [
  'axios',
  'lodash',
  'date-fns',
  'uuid',
  'clsx',
  'zustand',
  'react-hook-form',
  'zod',
  'recharts',
  'lucide-react',
  'framer-motion',
  'react-router-dom',
  'react-query',
  '@tanstack/react-query',
];

// 自动批准的模式（类型定义等）
const AUTO_APPROVE_PATTERNS = [
  /^@types\//,  // 匹配所有以 @types/ 开头的包
];





/**
 * 检查依赖是否在白名单中
 * @param {string} depName - 依赖名称
 * @returns {boolean}
 */
function isDependencyAllowed(depName) {
  // 检查白名单
  if (ALLOWED_DEPENDENCIES.includes(depName)) {
    return true;
  }
  
  // 检查自动批准模式
  for (const pattern of AUTO_APPROVE_PATTERNS) {
    if (pattern.test(depName)) {
      return true;
    }
  }
  
  return false;
}

/**
 * 验证并修复 JSON 字符串
 * @param {string} jsonStr - JSON 字符串
 * @param {string} context - 上下文描述（用于错误日志）
 * @returns {Object|null} 解析后的对象，失败返回 null
 */
function validateAndParseJSON(jsonStr, context = 'JSON') {
  try {
    // 尝试解析
    const obj = JSON.parse(jsonStr);
    return obj;
  } catch (error) {
    console.error(`❌ ${context} 解析失败:`, error.message);
    
    // 尝试基本修复：移除常见问题
    try {
      // 移除尾部逗号
      let fixed = jsonStr.replace(/,(\s*[}\]])/g, '$1');
      // 尝试再次解析
      return JSON.parse(fixed);
    } catch (fixError) {
      console.error(`❌ ${context} 修复失败，返回 null`);
      return null;
    }
  }
}

/**
 * 智能合并 package.json（带依赖白名单和 JSON 验证）
 * @param {string} presetPackageJson - 预设的 package.json 字符串
 * @param {string} aiPackageJson - AI 生成的 package.json 字符串
 * @returns {string} 合并后的 package.json 字符串
 */
function mergePackageJson(presetPackageJson, aiPackageJson) {
  // 验证并解析预设 package.json
  const preset = validateAndParseJSON(presetPackageJson, 'Preset package.json');
  if (!preset) {
    console.error('❌ 预设 package.json 无效，返回原始预设');
    return presetPackageJson;
  }
  
  // 验证并解析 AI package.json
  const ai = validateAndParseJSON(aiPackageJson, 'AI package.json');
  if (!ai) {
    console.warn('⚠️  AI package.json 无效，忽略 AI 依赖');
    return presetPackageJson;
  }
  
  try {
    // 从预设依赖开始
    const mergedDependencies = { ...preset.dependencies };
    
    // 检查 AI 添加的新依赖（白名单过滤）
    const aiDeps = ai.dependencies || {};
    const approvedDeps = [];
    const rejectedDeps = [];
    
    for (const [dep, version] of Object.entries(aiDeps)) {
      if (!preset.dependencies || !preset.dependencies[dep]) {
        // 这是新依赖，检查白名单
        if (isDependencyAllowed(dep)) {
        mergedDependencies[dep] = version;
          approvedDeps.push(dep);
        } else {
          rejectedDeps.push(dep);
          console.warn(`🚫 依赖 "${dep}" 不在白名单中，已拒绝`);
        }
      }
      // 如果依赖已存在于预设中，保留预设的版本（确保兼容性）
    }
    
    if (approvedDeps.length > 0) {
      console.log(`  ✅ 批准新依赖: ${approvedDeps.join(', ')}`);
    }
    if (rejectedDeps.length > 0) {
      console.warn(`  🚫 拒绝依赖: ${rejectedDeps.join(', ')}`);
    }
    
    // 合并 devDependencies（同样的白名单逻辑）
    const mergedDevDependencies = { ...preset.devDependencies };
    const aiDevDeps = ai.devDependencies || {};
    
    for (const [dep, version] of Object.entries(aiDevDeps)) {
      if (!preset.devDependencies || !preset.devDependencies[dep]) {
        // 开发依赖也需要白名单检查
        if (isDependencyAllowed(dep)) {
        mergedDevDependencies[dep] = version;
        } else {
          console.warn(`🚫 开发依赖 "${dep}" 不在白名单中，已拒绝`);
        }
      }
    }
    
    // 构建最终的 package.json
    const merged = {
      ...preset,  // 使用预设的 name, version, scripts 等
      dependencies: mergedDependencies,
      devDependencies: mergedDevDependencies
    };
    
    // 安全地序列化为 JSON（带双重检查）
    try {
      const result = JSON.stringify(merged, null, 2);
      
      // 验证结果是否可以被解析（防止格式错误）
      JSON.parse(result);
      
      console.log('  ✅ package.json 合并成功并通过验证');
      return result;
    } catch (serializeError) {
      console.error('❌ package.json 序列化失败:', serializeError);
      return presetPackageJson;
    }
  } catch (error) {
    console.warn('⚠️ package.json 合并失败，使用预设版本:', error);
    return presetPackageJson;
  }
}

/**
 * 生成主题变量的 CSS 字符串
 * @param {Object} theme - 主题对象
 * @param {Object} overrides - 覆盖变量
 * @returns {string} CSS 变量字符串
 */
function generateThemeVariablesCSS(theme, overrides = {}) {
  const allColors = { ...theme.colors, ...overrides };
  
  return Object.entries(allColors)
    .map(([varName, value]) => `    ${varName}: ${value};`)
    .join('\n');
}

/**
 * 在 CSS 中注入主题变量（替换 :root 块中的默认值）
 * @param {string} css - 原始 CSS
 * @param {string} themeVariables - 主题变量 CSS
 * @returns {string} 更新后的 CSS
 */
function injectThemeVariables(css, themeVariables) {
  // 查找 :root 块中的主题变量部分（在注释之后）
  const rootBlockRegex = /(\/\* === 主题变量.*?===\s*\*\/\s*)([\s\S]*?)(--brand1:[\s\S]*?)(--gradient-end:[^\n]+)/;
  
  const match = css.match(rootBlockRegex);
  
  if (match) {
    // 替换主题变量部分
    const replacement = `$1$2${themeVariables}`;
    return css.replace(rootBlockRegex, replacement);
  }
  
  // 如果没找到特定的注释块，尝试直接在 :root 开始处插入
  const simpleRootRegex = /(:root\s*\{)/;
  if (simpleRootRegex.test(css)) {
    return css.replace(simpleRootRegex, `$1\n    /* === Dynamic theme (injected) === */\n${themeVariables}\n`);
  }
  
  // 如果都找不到，返回原始 CSS
  console.warn('⚠️ Could not find :root block to inject theme variables');
  return css;
}

/**
 * 将后端返回的文件格式转换为 WebContainer 的 FileSystemTree 格式
 * @param {Object} files - 后端返回的文件字典 { '/path/to/file': 'content' }
 * @returns {Object} WebContainer FileSystemTree
 */
export function convertToFileSystemTree(files) {
  const tree = {}
  
  for (const [path, content] of Object.entries(files)) {
    // 移除开头的斜杠
    const cleanPath = path.startsWith('/') ? path.slice(1) : path
    const parts = cleanPath.split('/')
    
    let current = tree
    
    // 遍历路径的每一部分
    for (let i = 0; i < parts.length; i++) {
      const part = parts[i]
      const isLastPart = i === parts.length - 1
      
      if (isLastPart) {
        // 这是文件
        current[part] = {
          file: {
            contents: content
          }
        }
      } else {
        // 这是目录
        if (!current[part]) {
          current[part] = {
            directory: {}
          }
        }
        current = current[part].directory
      }
    }
  }
  
  return tree
}

/**
 * 检测浏览器是否支持 WebContainers
 * @returns {boolean} 是否支持
 */
export function supportsWebContainers() {
  // 检查 SharedArrayBuffer (WebContainers 的核心依赖)
  if (typeof SharedArrayBuffer === 'undefined') {
    return false
  }
  
  // 检查是否在移动设备上 (WebContainers 不支持移动端)
  const isMobile = /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(
    navigator.userAgent
  )
  if (isMobile) {
    return false
  }
  
  // 检查浏览器版本
  const isChrome = /Chrome\/(\d+)/.test(navigator.userAgent)
  const isFirefox = /Firefox\/(\d+)/.test(navigator.userAgent)
  const isSafari = /Version\/(\d+).*Safari/.test(navigator.userAgent)
  
  if (isChrome) {
    const version = parseInt(navigator.userAgent.match(/Chrome\/(\d+)/)[1])
    return version >= 89
  }
  
  if (isFirefox) {
    const version = parseInt(navigator.userAgent.match(/Firefox\/(\d+)/)[1])
    return version >= 91
  }
  
  if (isSafari) {
    const version = parseFloat(navigator.userAgent.match(/Version\/(\d+\.\d+)/)[1])
    return version >= 15.2
  }
  
  // 对于其他浏览器,只要有 SharedArrayBuffer 就认为支持
  return true
}

/**
 * 获取不支持的原因
 * @returns {string} 原因描述
 */
export function getUnsupportedReason() {
  if (typeof SharedArrayBuffer === 'undefined') {
    return '浏览器不支持 SharedArrayBuffer (可能需要 HTTPS 或特定的 HTTP 头部)'
  }
  
  const isMobile = /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(
    navigator.userAgent
  )
  if (isMobile) {
    return '移动设备暂不支持 WebContainers'
  }
  
  return '浏览器版本过旧,请升级到 Chrome 89+, Firefox 91+, 或 Safari 15.2+'
}

/**
 * WebContainer 管理器
 * 确保同时只有一个活跃的容器实例
 */
class WebContainerManager {
  constructor() {
    this.activeContainer = null
    this.isBooting = false
  }
  
  /**
   * 获取或创建 WebContainer 实例
   * @returns {Promise<WebContainer>}
   */
  async getContainer() {
    if (this.activeContainer) {
      console.log('📦 Using existing WebContainer instance')
      return this.activeContainer
    }
    
    if (this.isBooting) {
      console.log('⏳ Waiting for WebContainer boot to complete...')
      // 等待当前启动完成
      await new Promise(resolve => {
        const checkInterval = setInterval(() => {
          if (!this.isBooting) {
            clearInterval(checkInterval)
            resolve()
          }
        }, 100)
      })
      
      // 确保启动成功
      if (!this.activeContainer) {
        throw new Error('WebContainer 启动失败：boot 完成但 container 为 null')
      }
      
      console.log('✅ WebContainer boot completed, returning container')
      return this.activeContainer
    }
    
    console.log('🚀 Booting new WebContainer instance...')
    const container = await this.bootContainer()
    
    if (!container) {
      throw new Error('WebContainer 启动失败：bootContainer 返回 null')
    }
    
    console.log('✅ WebContainer boot successful')
    return container
  }
  
  /**
   * 启动新的 WebContainer
   * @returns {Promise<WebContainer>}
   */
  async bootContainer() {
    // 双重检查：防止并发启动
    if (this.activeContainer) {
      console.log('📦 Container already exists, skipping boot')
      return this.activeContainer
    }
    
    if (this.isBooting) {
      console.log('⏳ Boot already in progress, waiting...')
      // 等待当前启动完成
      while (this.isBooting) {
        await new Promise(resolve => setTimeout(resolve, 100))
      }
      if (this.activeContainer) {
        return this.activeContainer
      }
      // 如果启动失败，抛出错误
      throw new Error('WebContainer boot failed in another call')
    }
    
    this.isBooting = true
    
    try {
      // 检查内存情况（如果API可用）
      if (performance.memory) {
        const memoryInfo = performance.memory
        const usedPercent = (memoryInfo.usedJSHeapSize / memoryInfo.jsHeapSizeLimit) * 100
        console.log(`📊 内存使用情况: ${usedPercent.toFixed(1)}% (${(memoryInfo.usedJSHeapSize / 1024 / 1024).toFixed(0)}MB / ${(memoryInfo.jsHeapSizeLimit / 1024 / 1024).toFixed(0)}MB)`)
        
        if (usedPercent > 90) {
          console.warn('⚠️  内存使用率过高，可能影响 WebContainer 启动')
        }
      }
      
      console.log('🔧 Importing WebContainer API...')
      const { WebContainer } = await import('@webcontainer/api')
      
      console.log('🔧 Calling WebContainer.boot()...')
      const container = await WebContainer.boot()
      
      if (!container) {
        throw new Error('WebContainer.boot() 返回 null 或 undefined')
      }
      
      console.log('✅ WebContainer.boot() 成功，container 实例已创建')
      this.activeContainer = container
      return container
    } catch (error) {
      console.error('❌ WebContainer boot 失败:', error)
      
      // 检查是否是内存错误
      if (error.message && (
        error.message.includes('memory') || 
        error.message.includes('Out of memory') ||
        error.message.includes('Cannot allocate')
      )) {
        throw new Error('内存不足：请关闭其他浏览器标签页，然后刷新页面重试。如果问题持续，请重启浏览器。')
      }
      
      // 如果错误是"已经有一个实例"，尝试返回现有实例
      if (error.message && error.message.includes('single WebContainer')) {
        console.warn('⚠️  检测到已存在的 WebContainer 实例，返回当前实例')
        if (this.activeContainer) {
          return this.activeContainer
        }
      }
      throw new Error(`WebContainer 启动失败: ${error.message}`)
    } finally {
      this.isBooting = false
    }
  }
  
  /**
   * 销毁当前容器
   */
  async teardown() {
    if (this.activeContainer) {
      try {
        await this.activeContainer.teardown()
      } catch (error) {
        console.warn('WebContainer teardown error:', error)
      }
      this.activeContainer = null
    }
  }
}

// 导出单例
export const webContainerManager = new WebContainerManager()

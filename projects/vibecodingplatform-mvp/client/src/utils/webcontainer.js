/**
 * WebContainer 工具函数
 * 用于检测浏览器兼容性和管理 WebContainer 实例
 */

import { BASE_PRESET_FILES, PROTECTED_PATHS } from './cyberpunkPreset.js'
import { getTheme } from './themes.js'

/**
 * 过滤 AI 生成的文件，只保留允许的业务文件
 * @param {Object} files - AI 生成的文件字典
 * @returns {Object} 过滤后的文件字典
 */
export function filterGeneratedFiles(files) {
  // 允许的文件路径模式
  const allowedPatterns = [
    /^src\/pages\//,              // 允许页面文件
    /^src\/features\//,           // 允许功能模块
    /^src\/App\.tsx$/,            // 允许路由配置
    /^src\/components\/generated\// // 允许生成的业务组件
  ];

  const filteredFiles = {};
  let blockedCount = 0;
  let allowedCount = 0;
  
  for (const [path, content] of Object.entries(files)) {
    // 移除开头的 /
    const cleanPath = path.startsWith('/') ? path.slice(1) : path;
    
    // 检查是否在受保护路径列表中
    const isProtected = PROTECTED_PATHS.some(pattern => pattern.test(cleanPath));
    
    if (isProtected) {
      console.warn(`🚫 Blocked AI write to protected file: ${cleanPath}`);
      blockedCount++;
      continue;
    }
    
    // 检查是否在允许列表中
    const isAllowed = allowedPatterns.some(pattern => pattern.test(cleanPath));
    
    if (isAllowed) {
      filteredFiles[cleanPath] = content;
      allowedCount++;
    } else {
      console.warn(`🚫 Blocked AI write to unauthorized path: ${cleanPath}`);
      blockedCount++;
    }
  }
  
  console.log(`✅ File filtering complete: ${allowedCount} allowed, ${blockedCount} blocked`);
  
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

/**
 * 智能合并 package.json
 * 保留预设的核心依赖和配置，但允许 AI 添加新的依赖
 * @param {string} presetPackageJson - 预设的 package.json 字符串
 * @param {string} aiPackageJson - AI 生成的 package.json 字符串
 * @returns {string} 合并后的 package.json 字符串
 */
function mergePackageJson(presetPackageJson, aiPackageJson) {
  try {
    const preset = JSON.parse(presetPackageJson);
    const ai = JSON.parse(aiPackageJson);
    
    // 从预设依赖开始
    const mergedDependencies = { ...preset.dependencies };
    
    // 检查 AI 添加的新依赖（不在预设中的）
    const aiDeps = ai.dependencies || {};
    const newDeps = [];
    
    for (const [dep, version] of Object.entries(aiDeps)) {
      if (!preset.dependencies || !preset.dependencies[dep]) {
        // 这是新依赖，添加进去
        mergedDependencies[dep] = version;
        newDeps.push(dep);
      }
      // 如果依赖已存在于预设中，保留预设的版本（确保兼容性）
    }
    
    if (newDeps.length > 0) {
      console.log(`  ↳ AI 添加了新依赖: ${newDeps.join(', ')}`);
    }
    
    // 合并 devDependencies（同样的逻辑）
    const mergedDevDependencies = { ...preset.devDependencies };
    const aiDevDeps = ai.devDependencies || {};
    
    for (const [dep, version] of Object.entries(aiDevDeps)) {
      if (!preset.devDependencies || !preset.devDependencies[dep]) {
        mergedDevDependencies[dep] = version;
      }
    }
    
    // 构建最终的 package.json
    const merged = {
      ...preset,  // 使用预设的 name, version, scripts 等
      dependencies: mergedDependencies,
      devDependencies: mergedDevDependencies
    };
    
    return JSON.stringify(merged, null, 2);
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
      return this.activeContainer
    }
    
    if (this.isBooting) {
      // 等待当前启动完成
      await new Promise(resolve => {
        const checkInterval = setInterval(() => {
          if (!this.isBooting) {
            clearInterval(checkInterval)
            resolve()
          }
        }, 100)
      })
      return this.activeContainer
    }
    
    return await this.bootContainer()
  }
  
  /**
   * 启动新的 WebContainer
   * @returns {Promise<WebContainer>}
   */
  async bootContainer() {
    this.isBooting = true
    
    try {
      const { WebContainer } = await import('@webcontainer/api')
      const container = await WebContainer.boot()
      this.activeContainer = container
      return container
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

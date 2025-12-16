/**
 * 主题应用工具 - 负责将主题应用到页面和 WebContainer
 */

import { getTheme, getRandomTheme } from './themes'
import { extractColorIntent, selectThemeByIntent } from './colorIntent'
import { saveProject, updateHistoryProject } from './storage'

/**
 * 应用主题到当前页面的 document.documentElement
 * @param {string} themeName - 主题名称
 * @param {object} overrides - 可选的颜色覆盖 {variableName: value}
 */
export function applyTheme(themeName, overrides = {}) {
  const theme = getTheme(themeName)
  const root = document.documentElement

  console.log(`🎨 应用主题: ${theme.displayName} (${themeName})`)

  // 应用主题的所有 CSS 变量
  Object.entries(theme.colors).forEach(([varName, value]) => {
    root.style.setProperty(varName, value)
  })

  // 应用覆盖值
  if (overrides && typeof overrides === 'object') {
    Object.entries(overrides).forEach(([varName, value]) => {
      if (value) {
        root.style.setProperty(varName, value)
        console.log(`  ↳ 覆盖变量: ${varName} = ${value}`)
      }
    })
  }

  console.log(`✅ 主题已应用`)
}

/**
 * 确保项目有主题配置（如果没有则自动选择并保存）
 * @param {object} project - 项目对象
 * @param {string} userPromptText - 可选的用户 prompt 文本，用于提取颜色意图
 * @returns {object} - 更新后的项目对象
 */
export function ensureProjectTheme(project, userPromptText = '') {
  // 确保 metadata 对象存在
  if (!project.metadata) {
    project.metadata = {}
  }

  // 如果已经有主题，直接返回
  if (project.metadata.themeName) {
    console.log(`✓ 项目已有主题: ${project.metadata.themeName}`)
    return project
  }

  console.log('🎨 项目缺少主题，开始自动选择...')

  // 尝试从 prompt 提取颜色意图
  let selectedTheme = null

  if (userPromptText) {
    const intent = extractColorIntent(userPromptText)
    
    if (intent.colorName || intent.hex) {
      selectedTheme = selectThemeByIntent(intent)
      console.log(`  ↳ 从 prompt 识别颜色意图:`, intent)
      console.log(`  ↳ 选择匹配主题: ${selectedTheme}`)
    }
  }

  // 如果没有提取到意图，随机选择
  if (!selectedTheme) {
    selectedTheme = getRandomTheme()
    console.log(`  ↳ 随机选择主题: ${selectedTheme}`)
  }

  // 更新项目对象
  project.metadata.themeName = selectedTheme
  project.metadata.themeOverrides = project.metadata.themeOverrides || {}

  // 保存到 localStorage
  saveProject(project)
  updateHistoryProject(project.id, { metadata: project.metadata })

  console.log(`✅ 主题已设置并保存: ${selectedTheme}`)

  return project
}

/**
 * 获取项目的主题名称（带默认值）
 * @param {object} project - 项目对象
 * @returns {string} - 主题名称
 */
export function getProjectTheme(project) {
  return project?.metadata?.themeName || 'teal'
}

/**
 * 获取项目的主题覆盖
 * @param {object} project - 项目对象
 * @returns {object} - 主题覆盖对象
 */
export function getProjectThemeOverrides(project) {
  return project?.metadata?.themeOverrides || {}
}

/**
 * 为 WebContainer 生成主题 CSS 注入代码
 * 这个函数返回一段 JavaScript 代码字符串，用于在 iframe 中应用主题
 * @param {string} themeName - 主题名称
 * @param {object} overrides - 可选的颜色覆盖
 * @returns {string} - JavaScript 代码字符串
 */
export function generateThemeInjectionScript(themeName, overrides = {}) {
  const theme = getTheme(themeName)
  const allColors = { ...theme.colors, ...overrides }

  const cssVariables = Object.entries(allColors)
    .map(([varName, value]) => `${varName}: ${value};`)
    .join('\n    ')

  return `
/* Auto-generated theme injection */
(function() {
  const style = document.createElement('style');
  style.textContent = \`
    :root {
      ${cssVariables}
    }
  \`;
  document.head.appendChild(style);
  console.log('🎨 Theme applied in WebContainer: ${themeName}');
})();
`
}


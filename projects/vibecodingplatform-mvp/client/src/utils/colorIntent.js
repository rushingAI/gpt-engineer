/**
 * 颜色意图提取 - 从用户 prompt 中提取颜色偏好
 */

import { getAllThemeNames, getTheme } from './themes'

/**
 * 颜色关键词映射表（中文 -> 主题名称）
 */
const COLOR_KEYWORDS = {
  // 橙黄系
  '橙': 'orange',
  '橙色': 'orange',
  '橘': 'orange',
  '橘色': 'orange',
  '黄': 'amber',
  '黄色': 'amber',
  '金': 'amber',
  '金色': 'amber',
  
  // 紫色系
  '紫': 'violet',
  '紫色': 'violet',
  '紫罗兰': 'violet',
  '洋红': 'magenta',
  
  // 蓝色系
  '蓝': 'blue',
  '蓝色': 'blue',
  '天蓝': 'sky',
  '天空蓝': 'sky',
  
  // 粉色系
  '粉': 'pink',
  '粉色': 'pink',
  '粉红': 'pink',
  
  // 绿色系
  '绿': 'emerald',
  '绿色': 'emerald',
  '青': 'teal',
  '青色': 'cyan',
  '青绿': 'teal',
  '青柠': 'lime',
  '翡翠': 'emerald',
  
  // 红色系
  '红': 'red',
  '红色': 'red',
  '赤': 'red',
}

/**
 * 英文颜色关键词映射
 */
const ENGLISH_COLOR_KEYWORDS = {
  'orange': 'orange',
  'amber': 'amber',
  'yellow': 'amber',
  'gold': 'amber',
  
  'purple': 'violet',
  'violet': 'violet',
  'magenta': 'magenta',
  
  'blue': 'blue',
  'sky': 'sky',
  
  'pink': 'pink',
  
  'green': 'emerald',
  'teal': 'teal',
  'cyan': 'cyan',
  'lime': 'lime',
  'emerald': 'emerald',
  
  'red': 'red',
}

/**
 * 从文本中提取颜色意图
 * @param {string} text - 用户输入的文本
 * @returns {object} - { colorName: string|null, hex: string|null }
 */
export function extractColorIntent(text) {
  if (!text || typeof text !== 'string') {
    return { colorName: null, hex: null }
  }

  const lowerText = text.toLowerCase()

  // 1. 检查是否有 hex 颜色代码 (#RRGGBB 或 #RGB)
  const hexMatch = text.match(/#([0-9a-fA-F]{6}|[0-9a-fA-F]{3})\b/)
  if (hexMatch) {
    const hex = hexMatch[0]
    console.log(`🎨 提取到 hex 颜色: ${hex}`)
    return { colorName: null, hex }
  }

  // 2. 检查中文颜色关键词
  for (const [keyword, themeName] of Object.entries(COLOR_KEYWORDS)) {
    if (text.includes(keyword)) {
      console.log(`🎨 提取到中文颜色关键词: ${keyword} -> ${themeName}`)
      return { colorName: themeName, hex: null }
    }
  }

  // 3. 检查英文颜色关键词
  for (const [keyword, themeName] of Object.entries(ENGLISH_COLOR_KEYWORDS)) {
    if (lowerText.includes(keyword)) {
      console.log(`🎨 提取到英文颜色关键词: ${keyword} -> ${themeName}`)
      return { colorName: themeName, hex: null }
    }
  }

  // 没有找到颜色意图
  return { colorName: null, hex: null }
}

/**
 * 将 hex 颜色映射到最接近的主题
 * 使用简单的色相区间映射
 * @param {string} hex - hex 颜色代码 (如 #FF9900)
 * @returns {string} - 主题名称
 */
function mapHexToTheme(hex) {
  // 移除 # 号
  hex = hex.replace('#', '')
  
  // 转换为 RGB
  let r, g, b
  if (hex.length === 3) {
    r = parseInt(hex[0] + hex[0], 16)
    g = parseInt(hex[1] + hex[1], 16)
    b = parseInt(hex[2] + hex[2], 16)
  } else {
    r = parseInt(hex.substring(0, 2), 16)
    g = parseInt(hex.substring(2, 4), 16)
    b = parseInt(hex.substring(4, 6), 16)
  }

  // 转换为 HSL 获取色相
  const rNorm = r / 255
  const gNorm = g / 255
  const bNorm = b / 255

  const max = Math.max(rNorm, gNorm, bNorm)
  const min = Math.min(rNorm, gNorm, bNorm)
  const delta = max - min

  let hue = 0

  if (delta === 0) {
    hue = 0
  } else if (max === rNorm) {
    hue = 60 * (((gNorm - bNorm) / delta) % 6)
  } else if (max === gNorm) {
    hue = 60 * (((bNorm - rNorm) / delta) + 2)
  } else {
    hue = 60 * (((rNorm - gNorm) / delta) + 4)
  }

  if (hue < 0) hue += 360

  console.log(`  ↳ hex ${hex} -> RGB(${r},${g},${b}) -> Hue ${Math.round(hue)}°`)

  // 根据色相区间映射主题
  // 色相环: 0°=红 30°=橙 60°=黄 120°=绿 180°=青 240°=蓝 300°=紫/洋红
  if (hue >= 0 && hue < 15) return 'red'          // 红
  if (hue >= 15 && hue < 40) return 'orange'      // 橙
  if (hue >= 40 && hue < 70) return 'amber'       // 黄/金
  if (hue >= 70 && hue < 100) return 'lime'       // 青柠
  if (hue >= 100 && hue < 150) return 'emerald'   // 绿/翡翠
  if (hue >= 150 && hue < 170) return 'teal'      // 青绿
  if (hue >= 170 && hue < 190) return 'cyan'      // 青
  if (hue >= 190 && hue < 220) return 'sky'       // 天蓝
  if (hue >= 220 && hue < 260) return 'blue'      // 蓝
  if (hue >= 260 && hue < 290) return 'violet'    // 紫
  if (hue >= 290 && hue < 330) return 'magenta'   // 洋红
  if (hue >= 330 && hue < 360) return 'pink'      // 粉

  return 'teal' // 默认
}

/**
 * 根据颜色意图选择主题
 * @param {object} intent - 颜色意图对象 { colorName, hex }
 * @returns {string} - 主题名称
 */
export function selectThemeByIntent(intent) {
  // 优先使用明确的颜色名称
  if (intent.colorName) {
    const themeNames = getAllThemeNames()
    // 检查主题是否存在
    if (themeNames.includes(intent.colorName)) {
      return intent.colorName
    }
  }

  // 如果有 hex，映射到最接近的主题
  if (intent.hex) {
    return mapHexToTheme(intent.hex)
  }

  // 都没有，返回 null（调用方应该随机选择）
  return null
}

/**
 * 测试函数：打印所有测试用例
 */
export function testColorIntent() {
  const testCases = [
    '创建一个橙色主题的计数器',
    '我要一个紫色的待办列表',
    '做一个蓝色科技风的仪表盘',
    '粉色可爱风格的应用',
    '用 #FF9900 作为主题色',
    '绿色环保主题',
    '红色警告风格',
    '普通的计数器应用', // 无颜色
  ]

  console.log('=== 颜色意图提取测试 ===')
  testCases.forEach((testCase, i) => {
    console.log(`\n测试 ${i + 1}: "${testCase}"`)
    const intent = extractColorIntent(testCase)
    console.log('  结果:', intent)
    const theme = selectThemeByIntent(intent)
    console.log('  选择主题:', theme || '(无匹配，应随机)')
  })
}


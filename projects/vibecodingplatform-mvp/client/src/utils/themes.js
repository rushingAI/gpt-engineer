/**
 * 主题池 - 提供多套预设主题配置
 * 每个主题定义一组 CSS 变量，用于控制应用的配色方案
 */

export const THEMES = {
  teal: {
    name: 'teal',
    displayName: '青绿霓虹',
    description: 'Cool cyberpunk teal - 经典赛博朋克青绿色',
    colors: {
      '--brand1': '174 72% 56%',      // 主色1 (青绿)
      '--brand2': '180 60% 40%',      // 主色2 (深青)
      '--glow': '174 72% 50%',        // 光晕色
      '--bg': '222 84% 5%',           // 背景色
      '--card': '220 18% 14%',        // 卡片背景
      '--ring': '174 72% 50%',        // 聚焦环
      '--border': '220 15% 22%',      // 边框色
      '--primary': '174 72% 50%',     // shadcn primary
      '--accent': '174 72% 50%',      // shadcn accent
      '--gradient-start': '174 72% 45%',
      '--gradient-end': '180 60% 40%',
    }
  },

  amber: {
    name: 'amber',
    displayName: '橙黄霓虹',
    description: 'Warm amber glow - 温暖的橙黄色调',
    colors: {
      '--brand1': '45 100% 60%',      // 金黄色
      '--brand2': '35 95% 55%',       // 橙色
      '--glow': '42 100% 50%',        // 金色光晕
      '--bg': '222 84% 5%',
      '--card': '220 18% 14%',
      '--ring': '42 100% 50%',
      '--border': '220 15% 22%',
      '--primary': '42 100% 50%',
      '--accent': '42 100% 50%',
      '--gradient-start': '45 100% 55%',
      '--gradient-end': '35 95% 50%',
    }
  },

  violet: {
    name: 'violet',
    displayName: '紫色霓虹',
    description: 'Electric violet - 电光紫色',
    colors: {
      '--brand1': '270 70% 65%',      // 亮紫
      '--brand2': '280 65% 55%',      // 深紫
      '--glow': '270 70% 60%',
      '--bg': '222 84% 5%',
      '--card': '220 18% 14%',
      '--ring': '270 70% 60%',
      '--border': '220 15% 22%',
      '--primary': '270 70% 60%',
      '--accent': '270 70% 60%',
      '--gradient-start': '270 70% 60%',
      '--gradient-end': '280 65% 50%',
    }
  },

  blue: {
    name: 'blue',
    displayName: '蓝色霓虹',
    description: 'Electric blue - 电光蓝',
    colors: {
      '--brand1': '210 100% 60%',     // 亮蓝
      '--brand2': '220 90% 55%',      // 深蓝
      '--glow': '210 100% 55%',
      '--bg': '222 84% 5%',
      '--card': '220 18% 14%',
      '--ring': '210 100% 55%',
      '--border': '220 15% 22%',
      '--primary': '210 100% 55%',
      '--accent': '210 100% 55%',
      '--gradient-start': '210 100% 55%',
      '--gradient-end': '220 90% 50%',
    }
  },

  pink: {
    name: 'pink',
    displayName: '粉色霓虹',
    description: 'Hot pink neon - 热力粉',
    colors: {
      '--brand1': '330 85% 65%',      // 亮粉
      '--brand2': '340 80% 60%',      // 玫红
      '--glow': '330 85% 60%',
      '--bg': '222 84% 5%',
      '--card': '220 18% 14%',
      '--ring': '330 85% 60%',
      '--border': '220 15% 22%',
      '--primary': '330 85% 60%',
      '--accent': '330 85% 60%',
      '--gradient-start': '330 85% 60%',
      '--gradient-end': '340 80% 55%',
    }
  },

  lime: {
    name: 'lime',
    displayName: '青柠霓虹',
    description: 'Bright lime green - 明亮青柠绿',
    colors: {
      '--brand1': '85 80% 60%',       // 青柠绿
      '--brand2': '95 75% 55%',       // 黄绿
      '--glow': '85 80% 55%',
      '--bg': '222 84% 5%',
      '--card': '220 18% 14%',
      '--ring': '85 80% 55%',
      '--border': '220 15% 22%',
      '--primary': '85 80% 55%',
      '--accent': '85 80% 55%',
      '--gradient-start': '85 80% 55%',
      '--gradient-end': '95 75% 50%',
    }
  },

  cyan: {
    name: 'cyan',
    displayName: '青色霓虹',
    description: 'Bright cyan - 明亮青色',
    colors: {
      '--brand1': '190 90% 55%',      // 亮青
      '--brand2': '195 85% 50%',      // 深青
      '--glow': '190 90% 50%',
      '--bg': '222 84% 5%',
      '--card': '220 18% 14%',
      '--ring': '190 90% 50%',
      '--border': '220 15% 22%',
      '--primary': '190 90% 50%',
      '--accent': '190 90% 50%',
      '--gradient-start': '190 90% 50%',
      '--gradient-end': '195 85% 45%',
    }
  },

  red: {
    name: 'red',
    displayName: '红色霓虹',
    description: 'Hot red neon - 热力红',
    colors: {
      '--brand1': '0 85% 60%',        // 亮红
      '--brand2': '10 80% 55%',       // 橙红
      '--glow': '0 85% 55%',
      '--bg': '222 84% 5%',
      '--card': '220 18% 14%',
      '--ring': '0 85% 55%',
      '--border': '220 15% 22%',
      '--primary': '0 85% 55%',
      '--accent': '0 85% 55%',
      '--gradient-start': '0 85% 55%',
      '--gradient-end': '10 80% 50%',
    }
  },

  emerald: {
    name: 'emerald',
    displayName: '翡翠霓虹',
    description: 'Emerald green - 翡翠绿',
    colors: {
      '--brand1': '160 75% 50%',      // 翡翠绿
      '--brand2': '165 70% 45%',      // 深翡翠
      '--glow': '160 75% 45%',
      '--bg': '222 84% 5%',
      '--card': '220 18% 14%',
      '--ring': '160 75% 45%',
      '--border': '220 15% 22%',
      '--primary': '160 75% 45%',
      '--accent': '160 75% 45%',
      '--gradient-start': '160 75% 45%',
      '--gradient-end': '165 70% 40%',
    }
  },

  orange: {
    name: 'orange',
    displayName: '橙色霓虹',
    description: 'Vibrant orange - 活力橙',
    colors: {
      '--brand1': '25 95% 60%',       // 亮橙
      '--brand2': '20 90% 55%',       // 深橙
      '--glow': '25 95% 55%',
      '--bg': '222 84% 5%',
      '--card': '220 18% 14%',
      '--ring': '25 95% 55%',
      '--border': '220 15% 22%',
      '--primary': '25 95% 55%',
      '--accent': '25 95% 55%',
      '--gradient-start': '25 95% 55%',
      '--gradient-end': '20 90% 50%',
    }
  },

  magenta: {
    name: 'magenta',
    displayName: '洋红霓虹',
    description: 'Electric magenta - 电光洋红',
    colors: {
      '--brand1': '300 75% 60%',      // 洋红
      '--brand2': '310 70% 55%',      // 深洋红
      '--glow': '300 75% 55%',
      '--bg': '222 84% 5%',
      '--card': '220 18% 14%',
      '--ring': '300 75% 55%',
      '--border': '220 15% 22%',
      '--primary': '300 75% 55%',
      '--accent': '300 75% 55%',
      '--gradient-start': '300 75% 55%',
      '--gradient-end': '310 70% 50%',
    }
  },

  sky: {
    name: 'sky',
    displayName: '天空蓝霓虹',
    description: 'Sky blue - 天空蓝',
    colors: {
      '--brand1': '200 95% 60%',      // 天空蓝
      '--brand2': '205 90% 55%',      // 深天蓝
      '--glow': '200 95% 55%',
      '--bg': '222 84% 5%',
      '--card': '220 18% 14%',
      '--ring': '200 95% 55%',
      '--border': '220 15% 22%',
      '--primary': '200 95% 55%',
      '--accent': '200 95% 55%',
      '--gradient-start': '200 95% 55%',
      '--gradient-end': '205 90% 50%',
    }
  }
}

/**
 * 获取所有主题名称列表
 */
export function getAllThemeNames() {
  return Object.keys(THEMES)
}

/**
 * 获取主题配置
 */
export function getTheme(themeName) {
  return THEMES[themeName] || THEMES.teal
}

/**
 * 随机选择一个主题（避免与上一个重复）
 */
export function getRandomTheme(excludeTheme = null) {
  const themeNames = getAllThemeNames()
  
  // 如果只有一个主题或没有排除项，直接随机
  if (themeNames.length <= 1 || !excludeTheme) {
    const randomIndex = Math.floor(Math.random() * themeNames.length)
    return themeNames[randomIndex]
  }
  
  // 过滤掉排除的主题
  const availableThemes = themeNames.filter(name => name !== excludeTheme)
  const randomIndex = Math.floor(Math.random() * availableThemes.length)
  return availableThemes[randomIndex]
}


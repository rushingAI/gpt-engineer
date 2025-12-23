// localStorage 操作工具函数

const STORAGE_KEY = 'vibecodingplatform_current_app'
const HISTORY_KEY = 'vibecodingplatform_history'
const MAX_HISTORY = 10

/**
 * 保存当前项目
 */
export function saveCurrentProject(project) {
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(project))
    return true
  } catch (error) {
    console.error('保存项目失败:', error)
    return false
  }
}

/**
 * 获取当前项目
 */
export function getCurrentProject() {
  try {
    const saved = localStorage.getItem(STORAGE_KEY)
    const project = saved ? JSON.parse(saved) : null
    return project ? migrateProjectFormat(project) : null
  } catch (error) {
    console.error('读取项目失败:', error)
    return null
  }
}

/**
 * 迁移项目数据格式（向后兼容）
 * 确保旧格式的消息能正确显示
 */
function migrateProjectFormat(project) {
  if (!project.messages) {
    return project
  }
  
  // 为旧消息添加默认字段
  project.messages = project.messages.map(msg => {
    if (msg.role === 'assistant' && !msg.hasOwnProperty('streaming')) {
      // 旧的 AI 消息，添加默认字段
      return {
        ...msg,
        streaming: false,
        steps: msg.steps || [] // 保留已有的 steps（如果有）
      }
    }
    return msg
  })
  
  return project
}

/**
 * 清除当前项目
 */
export function clearCurrentProject() {
  localStorage.removeItem(STORAGE_KEY)
}

/**
 * 获取项目（通过ID）
 * 优先从当前项目读取（确保获取最新数据），然后才从历史记录查找
 */
export function getProject(id) {
  // 1. 先检查是否是当前项目（最新数据）
  const currentProject = getCurrentProject()
  if (currentProject && currentProject.id === id) {
    console.log(`✓ 从当前项目读取: ${id}`)
    return currentProject
  }
  
  // 2. 从历史记录中查找
  const history = getHistory()
  const project = history.find(p => p.id === id) || null
  
  if (project) {
    console.log(`✓ 从历史记录读取: ${id}`)
  } else {
    console.warn(`⚠️ 未找到项目: ${id}`)
  }
  
  return project ? migrateProjectFormat(project) : null
}

/**
 * 获取历史记录
 */
export function getHistory() {
  try {
    const saved = localStorage.getItem(HISTORY_KEY)
    const history = saved ? JSON.parse(saved) : []
    // 迁移所有历史项目
    return history.map(migrateProjectFormat)
  } catch (error) {
    console.error('读取历史记录失败:', error)
    return []
  }
}

/**
 * 添加到历史记录
 */
export function addToHistory(project) {
  try {
    let history = getHistory()
    
    // 检查是否已存在（更新而非新增）
    const existingIndex = history.findIndex(p => p.id === project.id)
    if (existingIndex >= 0) {
      history[existingIndex] = project
    } else {
      // 添加到开头
      history.unshift(project)
      
      // 只保留最近 MAX_HISTORY 个
      if (history.length > MAX_HISTORY) {
        history = history.slice(0, MAX_HISTORY)
      }
    }
    
    localStorage.setItem(HISTORY_KEY, JSON.stringify(history))
    return true
  } catch (error) {
    console.error('添加到历史记录失败:', error)
    return false
  }
}

/**
 * 删除历史记录
 */
export function deleteFromHistory(id) {
  try {
    const history = getHistory()
    const newHistory = history.filter(p => p.id !== id)
    localStorage.setItem(HISTORY_KEY, JSON.stringify(newHistory))
    return true
  } catch (error) {
    console.error('删除历史记录失败:', error)
    return false
  }
}

/**
 * 更新历史记录中的项目
 */
export function updateHistoryProject(id, updates) {
  try {
    const history = getHistory()
    const index = history.findIndex(p => p.id === id)
    if (index >= 0) {
      history[index] = { ...history[index], ...updates }
      localStorage.setItem(HISTORY_KEY, JSON.stringify(history))
      return true
    }
    return false
  } catch (error) {
    console.error('更新历史记录失败:', error)
    return false
  }
}

/**
 * 保存项目（别名，与 saveCurrentProject 相同）
 * 用于主题系统的统一接口
 */
export function saveProject(project) {
  return saveCurrentProject(project)
}

/**
 * 确保项目有 metadata 对象（如果没有则创建空对象）
 * @param {object} project - 项目对象
 * @returns {object} - 带有 metadata 的项目对象
 */
export function ensureProjectMetadata(project) {
  if (!project.metadata) {
    project.metadata = {}
  }
  return project
}

/**
 * 从 prompt 提取应用名称
 */
export function extractAppName(prompt) {
  const cleanPrompt = prompt
    .replace(/^(创建|生成|做|制作)(一个)?/g, '')
    .trim()
  return cleanPrompt.substring(0, 20) + (cleanPrompt.length > 20 ? '...' : '')
}


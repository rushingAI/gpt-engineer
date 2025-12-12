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
    return saved ? JSON.parse(saved) : null
  } catch (error) {
    console.error('读取项目失败:', error)
    return null
  }
}

/**
 * 清除当前项目
 */
export function clearCurrentProject() {
  localStorage.removeItem(STORAGE_KEY)
}

/**
 * 获取项目（通过ID）
 */
export function getProject(id) {
  const history = getHistory()
  return history.find(p => p.id === id) || null
}

/**
 * 获取历史记录
 */
export function getHistory() {
  try {
    const saved = localStorage.getItem(HISTORY_KEY)
    return saved ? JSON.parse(saved) : []
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
 * 从 prompt 提取应用名称
 */
export function extractAppName(prompt) {
  const cleanPrompt = prompt
    .replace(/^(创建|生成|做|制作)(一个)?/g, '')
    .trim()
  return cleanPrompt.substring(0, 20) + (cleanPrompt.length > 20 ? '...' : '')
}


// 智能判断使用 improve 还是 generate

/**
 * 判断是否应该使用 improve_fn（小改动）还是 gen_code（大改动/新功能）
 * @param {string} userMessage - 用户输入的消息
 * @returns {boolean} - true 使用 improve, false 使用 generate
 */
export function shouldUseImprove(userMessage) {
  // 小改动关键词（使用 improve）
  const improveKeywords = [
    '修改', '改', '换', '调整', '优化', '更新', '变更',
    '改成', '改为', '变成', '换成', '改变',
    '调大', '调小', '放大', '缩小',
    '改颜色', '改背景', '改字体', '改大小',
    '修复', 'fix', 'bug', '问题'
  ]
  
  // 大改动/新功能关键词（使用 generate）
  const genKeywords = [
    '添加', '增加', '新增', '加上', '实现', '加入',
    '创建', '生成', '做一个', '加一个', '再加',
    '新建', '构建', '开发'
  ]
  
  const message = userMessage.toLowerCase()
  
  // 检查是否包含关键词
  const hasImproveKeyword = improveKeywords.some(kw => message.includes(kw))
  const hasGenKeyword = genKeywords.some(kw => message.includes(kw))
  
  // 如果有明确的"改"关键词且没有"添加"关键词，用 improve
  if (hasImproveKeyword && !hasGenKeyword) {
    console.log('📝 检测到小改动，使用 improve_fn')
    return true
  }
  
  // 如果有"添加"关键词，用 generate（重新生成）
  if (hasGenKeyword) {
    console.log('🆕 检测到新功能，使用 gen_code')
    return false
  }
  
  // 默认用 improve（更快，适合简单优化）
  console.log('📝 默认使用 improve_fn')
  return true
}

/**
 * 构建完整的上下文 prompt（用于 generate）
 * @param {Array} messages - 对话历史
 * @param {string} currentMessage - 当前消息
 * @returns {string} - 完整的 prompt
 */
export function buildFullPrompt(messages, currentMessage) {
  // 提取用户的所有需求
  const userRequests = messages
    .filter(m => m.role === 'user')
    .map(m => m.content)
    .join('。')
  
  // 组合成完整 prompt
  return `${userRequests}。${currentMessage}`
}


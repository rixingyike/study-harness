/**
 * 极简前端 SDK 契约层 (API Client)
 * 收拢所有与 FastAPI 后端交互的 HTTP 请求，杜绝在各组件中散落 URL。
 */

const API_BASE = '/api'

export const chatApi = {
  /**
   * 获取所有历史会话列表
   */
  async getSessions() {
    const res = await fetch(`${API_BASE}/sessions`)
    if (!res.ok) throw new Error(`获取会话失败: HTTP ${res.status}`)
    return await res.json()
  },

  /**
   * 获取指定会话的消息历史
   */
  async getMessages(sessionId) {
    const res = await fetch(`${API_BASE}/sessions/${sessionId}/messages`)
    if (!res.ok) throw new Error(`获取消息失败: HTTP ${res.status}`)
    return await res.json()
  },

  /**
   * 创建新会话
   */
  async createSession(title = '新建对话') {
    const res = await fetch(`${API_BASE}/sessions`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ title })
    })
    if (!res.ok) throw new Error(`创建会话失败: HTTP ${res.status}`)
    return await res.json()
  },

  /**
   * 删除指定会话
   */
  async deleteSession(sessionId) {
    const res = await fetch(`${API_BASE}/sessions/${sessionId}`, {
      method: 'DELETE'
    })
    if (!res.ok) throw new Error(`删除会话失败: HTTP ${res.status}`)
    return await res.json()
  },

  /**
   * 发送用户消息并触发 Think -> Act -> Observe 核心循环
   */
  async sendMessage(sessionId, content) {
    const res = await fetch(`${API_BASE}/sessions/${sessionId}/messages`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ content })
    })
    if (!res.ok) throw new Error(`发送消息失败: HTTP ${res.status}`)
    return await res.json()
  }
}

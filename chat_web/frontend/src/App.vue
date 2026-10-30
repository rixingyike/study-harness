<template>
  <div class="flex h-full w-full app-viewport-height overflow-hidden bg-slate-50 text-slate-800 font-sans relative">
    <!-- 移动端背景遮罩层（展开历史抽屉时显示，点击即可折叠收起） -->
    <div
      v-if="isSidebarOpen"
      @click="isSidebarOpen = false"
      class="fixed inset-0 bg-slate-900/40 backdrop-blur-xs z-40 md:hidden transition-opacity"
    ></div>

    <!-- ================= 左手边：互动的历史列表（支持手机端折叠/展开与桌面端常驻） ================= -->
    <aside
      :class="[
        'fixed md:static inset-y-0 left-0 z-50 w-72 md:w-64 flex-shrink-0 flex flex-col bg-white border-r border-slate-200 shadow-xl md:shadow-sm transition-transform duration-300 ease-in-out',
        isSidebarOpen ? 'translate-x-0' : '-translate-x-full md:translate-x-0'
      ]"
    >
      <!-- 顶部：新建对话按钮 与 手机端折叠关闭按钮 -->
      <div class="p-3 border-b border-slate-200 flex items-center gap-2">
        <button
          @click="handleCreateSession"
          class="flex-1 flex items-center justify-center gap-2 px-4 py-2.5 bg-red-700 hover:bg-red-800 active:scale-[0.98] text-white rounded-lg text-sm font-medium transition shadow-sm"
        >
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
          </svg>
          新建对话
        </button>

        <!-- 手机端快速折叠收起按钮 -->
        <button
          @click="isSidebarOpen = false"
          class="md:hidden p-2 text-slate-400 hover:text-slate-700 hover:bg-slate-100 rounded-lg transition"
          title="收起历史列表"
        >
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      </div>

      <!-- 历史会话列表 -->
      <div class="flex-1 overflow-y-auto p-2 space-y-1">
        <div v-if="sessions.length === 0" class="text-center text-xs text-slate-400 py-6">
          暂无历史互动记录
        </div>
        <div
          v-for="sess in sessions"
          :key="sess.id"
          @click="handleSelectSession(sess.id)"
          :class="[
            'group relative flex items-center justify-between px-3 py-2.5 rounded-lg text-sm cursor-pointer transition select-none',
            currentSessionId === sess.id
              ? 'bg-red-50 text-red-900 font-medium border-l-4 border-red-700 shadow-xs'
              : 'text-slate-600 hover:bg-slate-100 hover:text-slate-900'
          ]"
        >
          <!-- 会话标题 -->
          <div class="flex items-center gap-2.5 truncate pr-6">
            <svg class="w-4 h-4 flex-shrink-0 opacity-70 text-slate-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.8" d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z" />
            </svg>
            <span class="truncate">{{ sess.title }}</span>
          </div>

          <!-- 删除按钮 -->
          <button
            @click.stop="deleteSession(sess.id)"
            class="opacity-0 group-hover:opacity-100 p-1 text-slate-400 hover:text-red-600 rounded transition"
            title="删除会话"
          >
            <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
            </svg>
          </button>
        </div>
      </div>

      <!-- 底部作者/系统标记 -->
      <div class="p-3 border-t border-slate-200 text-xs text-slate-500 flex items-center justify-between bg-slate-50/50">
        <span>金石碼农 · 极简架构</span>
        <span class="px-1.5 py-0.5 rounded bg-slate-200 text-[10px] text-slate-600 font-mono">Python3 + Vue3</span>
      </div>
    </aside>

    <!-- ================= 右手边：主交互区 ================= -->
    <main class="flex-1 min-w-0 flex flex-col h-full overflow-hidden bg-slate-50">
      <!-- 顶栏：当前会话标题与状态，以及移动端展开历史菜单的按钮 -->
      <header class="h-14 flex items-center justify-between px-4 sm:px-6 border-b border-slate-200 bg-white shadow-xs flex-shrink-0">
        <div class="flex items-center gap-2 sm:gap-3 min-w-0">
          <!-- 手机端展开侧边栏菜单按钮 -->
          <button
            @click="isSidebarOpen = true"
            class="md:hidden p-1.5 -ml-1 text-slate-600 hover:text-slate-900 hover:bg-slate-100 rounded-lg transition flex-shrink-0"
            title="展开历史对话列表"
          >
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16" />
            </svg>
          </button>

          <h1 class="text-sm font-semibold text-slate-800 truncate">
            {{ currentSessionTitle || '请选择或新建会话' }}
          </h1>
          <span v-if="currentSessionId" class="hidden sm:inline-block text-xs text-slate-400 font-mono bg-slate-100 px-2 py-0.5 rounded border border-slate-200">
            ID: {{ currentSessionId.slice(0, 8) }}
          </span>
        </div>
        <div class="flex items-center gap-1.5 sm:gap-2 text-xs text-slate-500 flex-shrink-0">
          <span class="inline-block w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></span>
          <span class="hidden xs:inline">Harness 循环引擎在线</span>
          <span class="xs:hidden">在线</span>
        </div>
      </header>

      <!-- 上边：输入框的上面是倒叙的本轮互动的历史 (最新互动在最上方，历史轮次向下排列) -->
      <div ref="messageContainer" class="flex-1 min-h-0 overflow-y-auto px-3 sm:px-4 py-4 sm:py-6">
        <!-- 空状态引导 -->
        <div v-if="interactionRounds.length === 0" class="h-full flex flex-col items-center justify-center text-center text-slate-400 p-6 sm:p-8">
          <div class="w-14 h-14 sm:w-16 sm:h-16 rounded-2xl bg-white border border-slate-200 flex items-center justify-center text-red-600 mb-4 shadow-sm">
            <svg class="w-7 h-7 sm:w-8 sm:h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.6" d="M13 10V3L4 14h7v7l9-11h-7z" />
            </svg>
          </div>
          <h2 class="text-base sm:text-lg font-semibold text-slate-800 mb-2">已就绪，随时开启多轮互动</h2>
          <p class="text-xs text-slate-500 max-w-sm leading-relaxed">
            融合第二篇 Think -> Act -> Observe 核心循环引擎。从发出提示语到最终结果之间的思考推演全过程，将以灰色折叠块完整留存。
          </p>
        </div>

        <!-- 倒序互动历史列表：最新轮次在顶部，历史轮次依次向下 -->
        <div v-else class="max-w-4xl mx-auto space-y-3 sm:space-y-4">
          <div
            v-for="round in interactionRounds"
            :key="round.id"
            class="rounded-xl border border-slate-200 bg-white p-4 sm:p-5 shadow-xs transition hover:shadow-sm space-y-3.5"
          >
            <!-- 轮次头部标牌 -->
            <div class="flex items-center justify-between border-b border-slate-100 pb-2">
              <div class="flex items-center gap-2">
                <span
                  class="w-2 h-2 rounded-full"
                  :class="round.isLatest ? 'bg-red-600 animate-pulse' : 'bg-slate-300'"
                ></span>
                <span class="text-xs font-semibold text-slate-700">
                  第 {{ round.roundIndex }} 轮互动
                </span>
                <span
                  v-if="round.isLatest"
                  class="text-[10px] bg-red-50 text-red-700 border border-red-200 px-1.5 py-0.5 rounded font-medium"
                >
                  最新
                </span>
              </div>
              <span class="text-[11px] text-slate-400 font-mono">{{ round.time }}</span>
            </div>

            <!-- 用户提问 -->
            <div class="flex items-start gap-2.5 sm:gap-3">
              <div class="w-6 h-6 sm:w-7 sm:h-7 rounded-full bg-slate-100 border border-slate-300 flex items-center justify-center text-xs font-medium text-slate-700 flex-shrink-0 mt-0.5">
                我
              </div>
              <div class="flex-1 bg-red-50/70 border border-red-100 text-slate-800 rounded-xl px-3.5 py-2.5 text-sm leading-relaxed whitespace-pre-wrap break-words">
                {{ round.userMessage?.content }}
              </div>
            </div>

            <!-- AI 回答：包含中间思考折叠块与最终交付结果 -->
            <div v-if="round.assistantMessage" class="space-y-3">
              <!-- 核心：从发出提示语到最终结果之间的思考过程（灰色折叠显示） -->
              <details
                v-if="round.assistantMessage.thinking"
                class="group rounded-xl border border-slate-200 bg-slate-100/70 overflow-hidden text-xs transition"
              >
                <summary class="flex items-center justify-between px-3.5 py-2.5 cursor-pointer text-slate-500 hover:text-slate-800 hover:bg-slate-200/50 select-none font-medium transition">
                  <span class="flex items-center gap-2">
                    <svg class="w-3.5 h-3.5 text-slate-400 group-open:rotate-90 transition-transform duration-200 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
                    </svg>
                    <span class="flex items-center gap-1.5 text-slate-700 font-semibold">
                      <span>💭 思考与推演全流程</span>
                      <span class="text-[10px] bg-slate-200 text-slate-600 px-1.5 py-0.5 rounded font-mono">Think-Act-Observe</span>
                    </span>
                  </span>
                  <span class="text-[11px] text-slate-400 font-mono">点击展开 / 收起</span>
                </summary>
                <div class="px-3.5 py-3 border-t border-slate-200 bg-slate-50/90 text-slate-600 leading-relaxed font-mono whitespace-pre-wrap break-words text-[11px] sm:text-xs">
                  {{ round.assistantMessage.thinking }}
                </div>
              </details>

              <!-- 最终结果交付气泡 -->
              <div class="flex items-start gap-2.5 sm:gap-3">
                <div class="w-6 h-6 sm:w-7 sm:h-7 rounded-full bg-red-700 text-white flex items-center justify-center text-xs font-bold flex-shrink-0 mt-0.5 shadow-xs">
                  AI
                </div>
                <div class="flex-1 bg-slate-50 border border-slate-200 text-slate-800 rounded-xl px-3.5 py-2.5 text-sm leading-relaxed whitespace-pre-wrap break-words shadow-2xs">
                  {{ round.assistantMessage.content }}
                </div>
              </div>
            </div>

            <!-- AI 思考等待中动画 (仅在最新轮次且等待时显示) -->
            <div v-else-if="loading && round.isLatest" class="space-y-2">
              <div class="rounded-xl border border-dashed border-slate-300 bg-slate-100/70 p-3 text-xs text-slate-600 flex items-center justify-between">
                <div class="flex items-center gap-2">
                  <span class="inline-block w-2.5 h-2.5 rounded-full bg-red-600 animate-pulse"></span>
                  <span class="font-medium text-slate-700">正在执行思考与推演循环（Think -> Act -> Observe）...</span>
                </div>
                <div class="flex items-center gap-1">
                  <span class="inline-block w-1.5 h-1.5 rounded-full bg-red-500 animate-bounce"></span>
                  <span class="inline-block w-1.5 h-1.5 rounded-full bg-red-500 animate-bounce [animation-delay:0.2s]"></span>
                  <span class="inline-block w-1.5 h-1.5 rounded-full bg-red-500 animate-bounce [animation-delay:0.4s]"></span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 下边：右边的输入框放在底部，输入框加高，右边配等高大号发送按钮，移动端动态安全区底部留白 -->
      <footer class="p-3 sm:p-4 safe-area-bottom bg-white border-t border-slate-200 flex-shrink-0 shadow-sm z-10">
        <div class="max-w-4xl mx-auto">
          <form @submit.prevent="handleSendMessage" class="flex items-stretch gap-2 sm:gap-3">
            <!-- 加高输入框：方便输入多行更多内容 -->
            <textarea
              v-model="inputContent"
              @keydown.enter.exact.prevent="handleSendMessage"
              placeholder="发送消息进行互动...（Enter 发送，Shift+Enter 换行）"
              rows="3"
              class="flex-1 bg-white border border-slate-300 rounded-xl p-2.5 sm:p-3 text-sm text-slate-800 placeholder-slate-400 resize-none focus:outline-none focus:ring-2 focus:ring-red-500/20 focus:border-red-600 shadow-xs transition leading-relaxed min-h-[72px] sm:min-h-[80px]"
            ></textarea>

            <!-- 变大并与输入框等高的发送按钮 -->
            <button
              type="submit"
              :disabled="!inputContent.trim() || loading"
              class="w-18 sm:w-24 px-3 sm:px-4 bg-red-700 hover:bg-red-800 active:scale-[0.98] disabled:bg-slate-200 disabled:text-slate-400 disabled:cursor-not-allowed text-white font-medium rounded-xl transition flex flex-col sm:flex-row items-center justify-center gap-1 sm:gap-1.5 shadow-sm flex-shrink-0 select-none"
            >
              <svg class="w-5 h-5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M14 5l7 7m0 0l-7 7m7-7H3" />
              </svg>
              <span class="text-xs sm:text-base font-semibold">发送</span>
            </button>
          </form>
          <div class="hidden sm:block mt-2 text-center text-[11px] text-slate-400">
            倒序呈现历史互动 · 灰色折叠展示思考推演 · 融合第二篇 Think-Act-Observe 状态机
          </div>
        </div>
      </footer>
    </main>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, nextTick } from 'vue'
import { chatApi } from './api'

// 状态管理
const sessions = ref([])
const currentSessionId = ref('')
const messages = ref([])
const inputContent = ref('')
const loading = ref(false)
const messageContainer = ref(null)
const isSidebarOpen = ref(false) // 手机端历史侧边栏抽屉折叠/展开状态

// 动态计算移动端视口高度，精准应对移动端 Safari/微信浏览器底部工具栏遮挡
const updateViewportHeight = () => {
  const vh = window.innerHeight * 0.01
  document.documentElement.style.setProperty('--vh', `${vh}px`)
}

const currentSessionTitle = computed(() => {
  const current = sessions.value.find(s => s.id === currentSessionId.value)
  return current ? current.title : ''
})

// 将消息计算为按轮次组织的倒序列表 (最新互动轮次排在最顶部)
const interactionRounds = computed(() => {
  const list = messages.value
  if (!list || list.length === 0) return []

  const rounds = []
  let currentRound = null
  let roundCounter = 1

  for (let i = 0; i < list.length; i++) {
    const msg = list[i]
    if (msg.role === 'user') {
      currentRound = {
        id: msg.id || `round_${roundCounter}`,
        roundIndex: roundCounter++,
        userMessage: msg,
        assistantMessage: null,
        time: msg.created_at ? new Date(msg.created_at).toLocaleTimeString() : ''
      }
      rounds.push(currentRound)
    } else if (msg.role === 'assistant') {
      if (currentRound && !currentRound.assistantMessage) {
        currentRound.assistantMessage = msg
      } else {
        // 若为单条助手消息则独立成轮
        currentRound = {
          id: msg.id || `round_${roundCounter}`,
          roundIndex: roundCounter++,
          userMessage: { role: 'user', content: '（前置上下文）' },
          assistantMessage: msg,
          time: msg.created_at ? new Date(msg.created_at).toLocaleTimeString() : ''
        }
        rounds.push(currentRound)
      }
    }
  }

  // 倒序排列：最新的一轮互动在最上方
  const reversed = [...rounds].reverse()
  if (reversed.length > 0) {
    reversed[0].isLatest = true
  }
  return reversed
})

// 倒序模式下定位到最顶部 (显示最新互动)
const scrollToTop = async () => {
  await nextTick()
  if (messageContainer.value) {
    messageContainer.value.scrollTop = 0
  }
}

// 获取会话列表
const fetchSessions = async () => {
  try {
    sessions.value = await chatApi.getSessions()
    // 如果当前没有选中会话且有历史会话，默认选中第一个
    if (!currentSessionId.value && sessions.value.length > 0) {
      await switchSession(sessions.value[0].id)
    } else if (sessions.value.length === 0) {
      await createNewSession()
    }
  } catch (err) {
    console.error('获取会话失败:', err)
  }
}

// 选择会话（手机端点击后自动折叠侧边栏抽屉）
const handleSelectSession = async (sessionId) => {
  isSidebarOpen.value = false
  await switchSession(sessionId)
}

// 切换会话核心逻辑
const switchSession = async (sessionId) => {
  if (currentSessionId.value === sessionId) return
  currentSessionId.value = sessionId
  try {
    messages.value = await chatApi.getMessages(sessionId)
    scrollToTop()
  } catch (err) {
    console.error('获取消息失败:', err)
  }
}

// 新建会话按钮响应（手机端点击后自动折叠侧边栏抽屉）
const handleCreateSession = async () => {
  isSidebarOpen.value = false
  await createNewSession()
}

// 新建会话核心逻辑
const createNewSession = async () => {
  try {
    const newSession = await chatApi.createSession('新建对话')
    sessions.value.unshift(newSession)
    currentSessionId.value = newSession.id
    messages.value = []
    scrollToTop()
  } catch (err) {
    console.error('新建会话失败:', err)
  }
}

// 删除会话
const deleteSession = async (sessionId) => {
  if (!confirm('确定删除此对话吗？')) return
  try {
    await chatApi.deleteSession(sessionId)
    sessions.value = sessions.value.filter(s => s.id !== sessionId)
    if (currentSessionId.value === sessionId) {
      if (sessions.value.length > 0) {
        await switchSession(sessions.value[0].id)
      } else {
        await createNewSession()
      }
    }
  } catch (err) {
    console.error('删除会话失败:', err)
  }
}

// 发送消息（支持重复多次互动）
const handleSendMessage = async () => {
  const text = inputContent.value.trim()
  if (!text || loading.value) return

  // 若无会话先建会话
  if (!currentSessionId.value) {
    await createNewSession()
  }

  // 先在本地界面即时渲染用户消息气泡（倒序模式下立即显示在最顶部）
  const tempUserMsg = {
    id: 'temp_' + Date.now(),
    session_id: currentSessionId.value,
    role: 'user',
    content: text,
    created_at: new Date().toISOString()
  }
  messages.value.push(tempUserMsg)
  inputContent.value = ''
  loading.value = true
  scrollToTop()

  try {
    const assistantMsg = await chatApi.sendMessage(currentSessionId.value, text)
    messages.value.push(assistantMsg)
    // 若这是首条互动，刷新会话标题
    if (messages.value.length <= 2) {
      const cur = sessions.value.find(s => s.id === currentSessionId.value)
      if (cur && cur.title === '新建对话') {
        cur.title = text.split('\n')[0].slice(0, 20) || '新建对话'
      }
    }
  } catch (err) {
    console.error('发送失败:', err)
  } finally {
    loading.value = false
    scrollToTop()
  }
}

onMounted(() => {
  updateViewportHeight()
  window.addEventListener('resize', updateViewportHeight)
  window.addEventListener('orientationchange', updateViewportHeight)
  fetchSessions()
})

onUnmounted(() => {
  window.removeEventListener('resize', updateViewportHeight)
  window.removeEventListener('orientationchange', updateViewportHeight)
})
</script>

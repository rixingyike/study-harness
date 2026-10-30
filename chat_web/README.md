# AI 智能对话控制台基础框架 (Python3 + Vue3)

高度对齐 ChatGPT / Google Gemini 经典 Web 布局的极简多轮交互基础框架：
- **左手边**：互动的历史会话列表（支持新建、切换与删除，标题随首句自动更新）。
- **右手边**：上面是互动的历史消息流（自动平滑滚动到底部），下面是固定在底部的多行输入框（Enter 发送，Shift+Enter 换行）。
- **交互特性**：支持多次、多轮重复互动，所有数据通过 SQLite 自动持久化保存。

---

## 快速启动

### 方式一：生产单进程一键启动（推荐）

前端已完成静态打包编译（`frontend/dist`），直接在后端启动即可同时提供接口与完整 Web 界面：

```bash
cd backend
python3 main.py
```

浏览器访问：`http://127.0.0.1:8000`

---

### 方式二：前后端双进程开发调试

**终端 1（后端 API）**：
```bash
cd backend
python3 main.py
# 运行在 http://127.0.0.1:8000
```

**终端 2（前端热重载）**：
```bash
cd frontend
npm install
npm run dev
# 运行在 http://127.0.0.1:3000，自动反向代理 API 至 8000
```

---

## 核心接口说明 (FastAPI)

- `GET /api/sessions`：获取所有历史会话列表
- `POST /api/sessions`：新建会话
- `DELETE /api/sessions/{session_id}`：删除指定会话及关联消息
- `GET /api/sessions/{session_id}/messages`：获取指定会话的历史消息
- `POST /api/sessions/{session_id}/messages`：发送消息进行多轮互动并持久化

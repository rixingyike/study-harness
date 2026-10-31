import os
import sys
import json
import sqlite3
import uuid
from datetime import datetime
from pathlib import Path
from typing import List, Optional
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from sqlmodel import SQLModel, Field, create_engine
import importlib

# ----------------- 路径与第二篇 Harness 核心循环引擎复用 -----------------
STUDY_HARNESS_ROOT = Path(__file__).resolve().parents[2]
if str(STUDY_HARNESS_ROOT) not in sys.path:
    sys.path.insert(0, str(STUDY_HARNESS_ROOT))

# 直接复用第二篇的单文件状态机引擎（包含配置好的 client、物理工具 TOOL_MAP 与描述表 tools）
ch02 = importlib.import_module("02_think_act_observe_loop")

# ----------------- 数据模型与库表结构 (SQLModel) -----------------
class SessionItem(SQLModel, table=True):
    __tablename__ = "sessions"
    __table_args__ = {"extend_existing": True}
    id: str = Field(primary_key=True)
    title: str = Field(default="新建对话")
    created_at: str
    updated_at: str

class MessageItem(SQLModel, table=True):
    __tablename__ = "messages"
    __table_args__ = {"extend_existing": True}
    id: str = Field(primary_key=True)
    session_id: str = Field(index=True)
    role: str  # 'user' | 'assistant'
    content: str
    thinking: Optional[str] = Field(default=None)  # 思考与推演全记录
    created_at: str

class SendMessageRequest(SQLModel):
    content: str = Field(min_length=1, description="用户发送的消息内容")

class CreateSessionRequest(SQLModel):
    title: Optional[str] = "新建对话"

# ----------------- 数据库引擎与自动建表 (SQLModel + SQLite) -----------------
DB_PATH = os.path.join(os.path.dirname(__file__), "chat.db")
sqlite_url = f"sqlite:///{DB_PATH}"
engine = create_engine(sqlite_url, connect_args={"check_same_thread": False})

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    # 核心：自动扫描所有 table=True 的模型；已存在则自动跳过，绝不重复建表或覆盖历史数据
    SQLModel.metadata.create_all(engine)

init_db()

# ----------------- 复用第二篇状态机并收集思考日志 -----------------
def run_harness_engine(history_messages: List[dict], user_prompt: str, max_turns: int = 5) -> tuple[str, str]:
    """
    直接借用第二篇的 client、tools 与 TOOL_MAP，
    一边驱动 Think -> Act -> Observe 循环，一边收集思考日志供前端折叠展示。
    """
    client = ch02.client
    tools = ch02.tools
    tool_map = ch02.TOOL_MAP

    thinking_logs = []
    context_msgs = [
        {"role": "system", "content": "你是一位脚踏实地的智能助手。请善用本地工具搜集事实后再下结论。"}
    ]
    for m in history_messages[-6:]:
        context_msgs.append({"role": m["role"], "content": m["content"]})
    context_msgs.append({"role": "user", "content": user_prompt})

    turn = 0
    final_content = ""

    while turn < max_turns:
        turn += 1
        thinking_logs.append(f"--- 【第 {turn} 轮循环 Think】模型正在审视上下文并盘算策略 ---")

        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=context_msgs,
            tools=tools,
            temperature=0.2
        )
        msg = response.choices[0].message
        context_msgs.append(msg)

        reasoning = getattr(msg, "reasoning_content", None)
        if reasoning:
            thinking_logs.append(f"【深度推演 Reasoning】\n{reasoning.strip()}")

        # 没有工具调用，说明思考收敛，推导出最终结论
        if not msg.tool_calls:
            thinking_logs.append("【思考收敛 Finish】模型判断事实搜集完整，推导得出最终交付成果。")
            final_content = msg.content or "（任务已执行完毕）"
            break

        # 触发工具调用 (Act -> Observe)
        for tc in msg.tool_calls:
            func_name = tc.function.name
            try:
                func_args = json.loads(tc.function.arguments) if tc.function.arguments else {}
            except Exception:
                func_args = {}

            thinking_logs.append(f"【行动 Act】决定动用物理工具：{func_name}，参数：{json.dumps(func_args, ensure_ascii=False)}")

            func = tool_map.get(func_name)
            observation = func(**func_args) if func else f"错误：未注册的工具 {func_name}"

            obs_text = str(observation)
            obs_preview = obs_text if len(obs_text) <= 300 else obs_text[:300] + "...(后略)"
            thinking_logs.append(f"【观察 Observe】物理环境返回客观事实：\n{obs_preview}")

            context_msgs.append({
                "role": "tool",
                "tool_call_id": tc.id,
                "content": obs_text
            })

    if turn >= max_turns and not final_content:
        thinking_logs.append(f"【安全刹车 Stop】已达到最大循环步数（{max_turns}步），强制刹车防死循环。")
        final_content = "任务已达最大步数限制，当前中间推演进展已汇总在上方折叠日志中。"

    return "\n\n".join(thinking_logs), final_content

# ----------------- FastAPI 应用与路由 -----------------
app = FastAPI(title="Study-Harness AI Web 控制台", version="2.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/sessions", response_model=List[SessionItem])
def list_sessions():
    with get_db() as conn:
        rows = conn.execute("SELECT * FROM sessions ORDER BY updated_at DESC").fetchall()
        return [
            SessionItem(
                id=r["id"],
                title=r["title"],
                created_at=r["created_at"],
                updated_at=r["updated_at"]
            )
            for r in rows
        ]

@app.post("/api/sessions", response_model=SessionItem)
def create_session(req: CreateSessionRequest):
    session_id = str(uuid.uuid4())
    now_str = datetime.now().isoformat()
    with get_db() as conn:
        conn.execute(
            "INSERT INTO sessions (id, title, created_at, updated_at) VALUES (?, ?, ?, ?)",
            (session_id, req.title or "新建对话", now_str, now_str)
        )
        conn.commit()
    return SessionItem(id=session_id, title=req.title or "新建对话", created_at=now_str, updated_at=now_str)

@app.delete("/api/sessions/{session_id}")
def delete_session(session_id: str):
    with get_db() as conn:
        conn.execute("DELETE FROM messages WHERE session_id = ?", (session_id,))
        cursor = conn.execute("DELETE FROM sessions WHERE id = ?", (session_id,))
        conn.commit()
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="会话不存在")
    return {"success": True, "message": "会话已删除"}

@app.get("/api/sessions/{session_id}/messages", response_model=List[MessageItem])
def list_messages(session_id: str):
    with get_db() as conn:
        sess = conn.execute("SELECT id FROM sessions WHERE id = ?", (session_id,)).fetchone()
        if not sess:
            raise HTTPException(status_code=404, detail="会话不存在")
        rows = conn.execute(
            "SELECT * FROM messages WHERE session_id = ? ORDER BY created_at ASC",
            (session_id,)
        ).fetchall()
        return [
            MessageItem(
                id=r["id"],
                session_id=r["session_id"],
                role=r["role"],
                content=r["content"],
                thinking=r["thinking"] if "thinking" in r.keys() else None,
                created_at=r["created_at"]
            )
            for r in rows
        ]

@app.post("/api/sessions/{session_id}/messages", response_model=MessageItem)
def send_message(session_id: str, req: SendMessageRequest):
    now_str = datetime.now().isoformat()
    with get_db() as conn:
        sess = conn.execute("SELECT * FROM sessions WHERE id = ?", (session_id,)).fetchone()
        if not sess:
            raise HTTPException(status_code=404, detail="会话不存在")

        # 首问截取会话标题
        msg_count = conn.execute(
            "SELECT COUNT(*) as cnt FROM messages WHERE session_id = ?",
            (session_id,)
        ).fetchone()["cnt"]

        if msg_count == 0:
            new_title = req.content.strip().split("\n")[0][:20] or "新建对话"
            conn.execute(
                "UPDATE sessions SET title = ?, updated_at = ? WHERE id = ?",
                (new_title, now_str, session_id)
            )
        else:
            conn.execute(
                "UPDATE sessions SET updated_at = ? WHERE id = ?",
                (now_str, session_id)
            )

        # 存入用户消息
        user_msg_id = str(uuid.uuid4())
        conn.execute(
            "INSERT INTO messages (id, session_id, role, content, thinking, created_at) VALUES (?, ?, ?, ?, ?, ?)",
            (user_msg_id, session_id, "user", req.content, None, now_str)
        )
        conn.commit()

        # 读取前置上下文
        history_rows = conn.execute(
            "SELECT role, content FROM messages WHERE session_id = ? AND id != ? ORDER BY created_at ASC",
            (session_id, user_msg_id)
        ).fetchall()
        history_list = [{"role": r["role"], "content": r["content"]} for r in history_rows]

    # 直接调用融合第二篇核心的循环状态机
    thinking_process, final_reply = run_harness_engine(history_list, req.content)

    # 存入助手回复与思考日志
    assistant_msg_id = str(uuid.uuid4())
    assistant_now_str = datetime.now().isoformat()
    with get_db() as conn:
        conn.execute(
            "INSERT INTO messages (id, session_id, role, content, thinking, created_at) VALUES (?, ?, ?, ?, ?, ?)",
            (assistant_msg_id, session_id, "assistant", final_reply, thinking_process, assistant_now_str)
        )
        conn.execute(
            "UPDATE sessions SET updated_at = ? WHERE id = ?",
            (assistant_now_str, session_id)
        )
        conn.commit()

    return MessageItem(
        id=assistant_msg_id,
        session_id=session_id,
        role="assistant",
        content=final_reply,
        thinking=thinking_process,
        created_at=assistant_now_str
    )

# ----------------- 静态托管前端页面 -----------------
FRONTEND_DIST = os.path.abspath(os.path.join(os.path.dirname(__file__), "../frontend/dist"))

if os.path.exists(FRONTEND_DIST):
    app.mount("/assets", StaticFiles(directory=os.path.join(FRONTEND_DIST, "assets")), name="assets")

    @app.get("/{full_path:path}")
    def serve_frontend(full_path: str):
        target = os.path.join(FRONTEND_DIST, full_path)
        if os.path.exists(target) and os.path.isfile(target):
            return FileResponse(target)
        return FileResponse(os.path.join(FRONTEND_DIST, "index.html"))

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 3010))
    print(f"==================================================")
    print(f" Study-Harness AI 控制台启动中...")
    print(f" 本地访问地址: http://127.0.0.1:{port}")
    print(f" 状态机引擎  : 已直接复用第二篇 02_think_act_observe_loop")
    print(f"==================================================")
    uvicorn.run(app, host="0.0.0.0", port=port)

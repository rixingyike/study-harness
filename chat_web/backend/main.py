import os
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
from pydantic import BaseModel, Field
from openai import OpenAI

# ----------------- 环境与配置 -----------------
BACKEND_DIR = Path(__file__).resolve().parent
STUDY_HARNESS_ROOT = Path(__file__).resolve().parents[2]

def load_deepseek_env():
    """从 study-harness 根目录或相关目录加载 .env 配置"""
    api_key = os.environ.get("DEEPSEEK_API_KEY")
    base_url = os.environ.get("DEEPSEEK_BASE_URL", "https://api.deepseek.com")
    candidates = [
        STUDY_HARNESS_ROOT / ".env",
        BACKEND_DIR.parent / ".env",
        BACKEND_DIR / ".env"
    ]
    for env_path in candidates:
        if (not api_key or "你的" in api_key) and env_path.exists():
            with open(env_path, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line.startswith("DEEPSEEK_API_KEY="):
                        api_key = line.split("=", 1)[1].strip().strip("'\"")
                    elif line.startswith("DEEPSEEK_BASE_URL="):
                        base_url = line.split("=", 1)[1].strip().strip("'\"")
    return api_key, base_url

# ----------------- 数据模型 (Pydantic v2) -----------------
class SessionItem(BaseModel):
    id: str
    title: str
    created_at: str
    updated_at: str

class MessageItem(BaseModel):
    id: str
    session_id: str
    role: str  # 'user' | 'assistant'
    content: str
    thinking: Optional[str] = None  # 从发出提示语到最终结果之间的思考与推演全记录
    created_at: str

class SendMessageRequest(BaseModel):
    content: str = Field(..., min_length=1, description="用户发送的消息内容")

class CreateSessionRequest(BaseModel):
    title: Optional[str] = "新建对话"

# ----------------- 数据库初始化 (SQLite) -----------------
DB_PATH = os.path.join(os.path.dirname(__file__), "chat.db")

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with get_db() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS sessions (
                id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS messages (
                id TEXT PRIMARY KEY,
                session_id TEXT NOT NULL,
                role TEXT NOT NULL,
                content TEXT NOT NULL,
                thinking TEXT,
                created_at TEXT NOT NULL,
                FOREIGN KEY (session_id) REFERENCES sessions (id) ON DELETE CASCADE
            )
        """)
        # 兼容旧表升级：检查并自动补充 thinking 字段
        cursor = conn.execute("PRAGMA table_info(messages)")
        columns = [row["name"] for row in cursor.fetchall()]
        if "thinking" not in columns:
            conn.execute("ALTER TABLE messages ADD COLUMN thinking TEXT")
        conn.commit()

init_db()

# ----------------- 第二篇 Harness 核心工具与循环状态机融合 -----------------
def tool_read_file(file_path: str) -> str:
    """读取指定本地文件的内容"""
    try:
        target = (STUDY_HARNESS_ROOT / file_path).resolve()
        if not target.exists():
            return f"错误：文件 {file_path} 并不存在。"
        with open(target, "r", encoding="utf-8") as f:
            content = f.read()
            return content if len(content) <= 3000 else content[:3000] + "\n...(后略)"
    except Exception as e:
        return f"读取文件异常: {str(e)}"

def tool_write_file(file_path: str, content: str) -> str:
    """向指定本地路径写入文本文件"""
    try:
        target = (STUDY_HARNESS_ROOT / file_path).resolve()
        with open(target, "w", encoding="utf-8") as f:
            f.write(content)
        return f"成功：已成功向 {file_path} 写入 {len(content)} 个字符。"
    except Exception as e:
        return f"写入文件异常: {str(e)}"

def tool_list_files(directory: str = ".") -> str:
    """列出指定目录下的文件清单"""
    try:
        target = (STUDY_HARNESS_ROOT / directory).resolve()
        if not target.exists():
            return f"错误：目录 {directory} 不存在。"
        files = [f for f in os.listdir(target) if not f.startswith(".")]
        return f"目录 [{directory}] 下的文件：{', '.join(files[:30])}"
    except Exception as e:
        return f"列出目录异常: {str(e)}"

TOOL_MAP = {
    "read_file": tool_read_file,
    "write_file": tool_write_file,
    "list_files": tool_list_files
}

TOOLS_SCHEMA = [
    {
        "type": "function",
        "function": {
            "name": "read_file",
            "description": "读取本地文件内容的工具（支持相对路径如 '01_basic_deepseek.py' 或测试文件）",
            "parameters": {
                "type": "object",
                "properties": {
                    "file_path": {"type": "string", "description": "要读取的文件相对路径"}
                },
                "required": ["file_path"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "write_file",
            "description": "向本地写入纯文本内容的工具",
            "parameters": {
                "type": "object",
                "properties": {
                    "file_path": {"type": "string", "description": "要写入的文件相对路径"},
                    "content": {"type": "string", "description": "要写入的纯文本内容"}
                },
                "required": ["file_path", "content"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "list_files",
            "description": "列出指定本地目录下的文件列表",
            "parameters": {
                "type": "object",
                "properties": {
                    "directory": {"type": "string", "description": "目录相对路径，默认为当前根目录 '.'"}
                }
            }
        }
    }
]

def run_harness_engine(history_messages: List[dict], user_prompt: str, max_turns: int = 5) -> tuple[str, str]:
    """
    融合第二篇 Think -> Act -> Observe 核心循环引擎
    从发出提示语开始，在拿到最后交付结果前，记录所有的思考与推演步骤
    返回: (thinking_logs, final_content)
    """
    api_key, base_url = load_deepseek_env()
    thinking_logs = []

    # 若未配置有效 API KEY，启用高保真推理模拟流
    if not api_key or "你的" in api_key:
        thinking_logs.append("【第 1 轮思考 Think】分析用户提示语意图，审视历史会话上下文...")
        thinking_logs.append("【工具规划 Act】检测本地工具库（read_file、write_file、list_files）...")
        thinking_logs.append("【环境观察 Observe】当前处于极简离线模式，组织综合回复策略。")
        final = f"已收到您的提问：“{user_prompt}”。\n\n当前已融合专栏第二篇的 Think-Act-Observe 状态机循环。在 study-harness/.env 中配置 DEEPSEEK_API_KEY 即可实时触发真实的云端思考与物理工具调用。"
        return "\n\n".join(thinking_logs), final

    client = OpenAI(api_key=api_key, base_url=base_url)

    # 准备上下文记忆
    context_msgs = [
        {
            "role": "system",
            "content": (
                "你是一个脚踏实地的智能助手（运行在 Harness 架构下）。"
                "你可以使用提供的本地工具（read_file、write_file、list_files）探查物理文件并解决任务。"
                "在最后拿到结果前，请根据需要调用工具搜集事实。如果无需动用工具，请直接给出逻辑严密、表达清晰的中文回复。"
            )
        }
    ]

    # 装载当前会话的历史上下文（取最近 6 条）
    for m in history_messages[-6:]:
        context_msgs.append({"role": m["role"], "content": m["content"]})
    context_msgs.append({"role": "user", "content": user_prompt})

    turn = 0
    final_content = ""

    while turn < max_turns:
        turn += 1
        thinking_logs.append(f"--- 【第 {turn} 轮循环 Think】模型正在审视上下文并盘算策略 ---")

        try:
            response = client.chat.completions.create(
                model="deepseek-chat",
                messages=context_msgs,
                tools=TOOLS_SCHEMA,
                temperature=0.2
            )
        except Exception as e:
            thinking_logs.append(f"【异常报警】调用接口失败: {str(e)}")
            final_content = f"执行过程中遭遇接口异常：{str(e)}"
            break

        msg = response.choices[0].message
        context_msgs.append(msg)

        # 捕获深度推理思维链（如模型自身携带的 reasoning_content）
        reasoning = getattr(msg, "reasoning_content", None)
        if reasoning:
            thinking_logs.append(f"【深度推演 Reasoning】\n{reasoning.strip()}")

        # 分支判断：无需工具调用即为任务终点
        if not msg.tool_calls:
            thinking_logs.append("【思考收敛 Finish】模型判断事实搜集完整，推导得出最终交付成果。")
            final_content = msg.content or "（任务已执行完毕）"
            break

        # 执行工具调用 (Act -> Observe)
        for tc in msg.tool_calls:
            func_name = tc.function.name
            try:
                func_args = json.loads(tc.function.arguments)
            except Exception:
                func_args = {}

            thinking_logs.append(f"【行动 Act】决定动用物理工具：{func_name}，参数：{json.dumps(func_args, ensure_ascii=False)}")

            func = TOOL_MAP.get(func_name)
            if func:
                observation = func(**func_args)
            else:
                observation = f"错误：未注册的工具 {func_name}"

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

# ----------------- FastAPI 应用 -----------------
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
    """获取所有历史会话列表，按最后更新时间倒序排列"""
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
    """新建一个聊天会话"""
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
    """删除指定会话及所有关联消息"""
    with get_db() as conn:
        conn.execute("DELETE FROM messages WHERE session_id = ?", (session_id,))
        cursor = conn.execute("DELETE FROM sessions WHERE id = ?", (session_id,))
        conn.commit()
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="会话不存在")
    return {"success": True, "message": "会话已删除"}

@app.get("/api/sessions/{session_id}/messages", response_model=List[MessageItem])
def list_messages(session_id: str):
    """获取指定会话的所有历史消息（包含思考过程）"""
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
    """
    发送消息：融合第二篇 Think -> Act -> Observe 核心循环引擎
    记录全流程思考与行动，返回最终结果与灰色折叠思考日志
    """
    now = datetime.now()
    now_str = now.isoformat()

    with get_db() as conn:
        sess = conn.execute("SELECT * FROM sessions WHERE id = ?", (session_id,)).fetchone()
        if not sess:
            raise HTTPException(status_code=404, detail="会话不存在")

        # 检查是否是首条消息，用于更新会话标题
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

        # 1. 存入用户提问
        user_msg_id = str(uuid.uuid4())
        conn.execute(
            "INSERT INTO messages (id, session_id, role, content, thinking, created_at) VALUES (?, ?, ?, ?, ?, ?)",
            (user_msg_id, session_id, "user", req.content, None, now_str)
        )
        conn.commit()

        # 读取前置上下文传给引擎
        history_rows = conn.execute(
            "SELECT role, content FROM messages WHERE session_id = ? AND id != ? ORDER BY created_at ASC",
            (session_id, user_msg_id)
        ).fetchall()
        history_list = [{"role": r["role"], "content": r["content"]} for r in history_rows]

    # 2. 调用融合自第二篇的 Harness 核心循环状态机
    thinking_process, final_reply = run_harness_engine(history_list, req.content)

    # 3. 持久化存储助手消息与思考过程
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

# ----------------- 静态托管前端生产页面 -----------------
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
    print(f" 挂载前端路径: {FRONTEND_DIST}")
    print(f" 状态机引擎  : 已融合第二篇 Think-Act-Observe 核心循环")
    print(f"==================================================")
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=False)

import os
import json
import sqlite3
import uuid
import shutil
import subprocess
from datetime import datetime
from pathlib import Path
from typing import List, Optional
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from sqlmodel import SQLModel, Field, create_engine
from openai import OpenAI

# ----------------- 路径与环境配置 -----------------
BACKEND_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = Path(__file__).resolve().parents[2]

def load_deepseek_env():
    """从本地或项目根目录加载 .env 配置"""
    api_key = os.environ.get("DEEPSEEK_API_KEY")
    base_url = os.environ.get("DEEPSEEK_BASE_URL", "https://api.deepseek.com")
    candidates = [
        BACKEND_DIR / ".env",
        BACKEND_DIR.parent / ".env",
        PROJECT_ROOT / ".env"
    ]
    for env_path in candidates:
        if env_path.exists() and (not api_key or "你的" in api_key):
            with open(env_path, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line.startswith("DEEPSEEK_API_KEY="):
                        api_key = line.split("=", 1)[1].strip().strip("'\"")
                    elif line.startswith("DEEPSEEK_BASE_URL="):
                        base_url = line.split("=", 1)[1].strip().strip("'\"")
    return api_key, base_url

# ----------------- 数据模型与库表结构 (SQLModel) -----------------
class SessionItem(SQLModel, table=True):
    __tablename__ = "sessions"
    __table_args__ = {"extend_existing": True}
    id: str = Field(primary_key=True)
    title: str = Field(default="新建对话")
    created_at: str
    updated_at: str
    conversation_id: Optional[str] = Field(default=None)  # 绑定的终端 CLI 会话 ID

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
    with get_db() as conn:
        cols = [c[1] for c in conn.execute("PRAGMA table_info(sessions)").fetchall()]
        if "conversation_id" not in cols:
            conn.execute("ALTER TABLE sessions ADD COLUMN conversation_id TEXT")
            conn.commit()

init_db()

# ----------------- Harness 核心物理工具与 Schema -----------------
def read_file(file_path: str) -> str:
    """读取指定本地文件的内容"""
    try:
        target = Path(file_path)
        if not target.is_absolute():
            target = PROJECT_ROOT / target
        if not target.exists():
            return f"错误：文件 {file_path} 并不存在。"
        with open(target, "r", encoding="utf-8") as f:
            content = f.read()
            return content if len(content) <= 3000 else content[:3000] + "\n...(后略)"
    except Exception as e:
        return f"读取文件异常: {str(e)}"

def write_file(file_path: str, content: str) -> str:
    """向指定本地路径写入纯文本内容"""
    try:
        target = Path(file_path)
        if not target.is_absolute():
            target = PROJECT_ROOT / target
        with open(target, "w", encoding="utf-8") as f:
            f.write(content)
        return f"成功：已成功向 {file_path} 写入 {len(content)} 个字符。"
    except Exception as e:
        return f"写入文件异常: {str(e)}"

TOOL_MAP = {
    "read_file": read_file,
    "write_file": write_file
}

TOOLS_SCHEMA = [
    {
        "type": "function",
        "function": {
            "name": "read_file",
            "description": "读取本地文件内容的工具",
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
    }
]

# ----------------- 终端 AI CLI 与状态机循环引擎 -----------------
def get_terminal_cli_path() -> Optional[str]:
    """定位本地终端 AI CLI 执行文件（优先使用官方 Google Antigravity/Gemini agy）"""
    candidates = [
        shutil.which("agy"),
        os.path.expanduser("~/.local/bin/agy"),
        "/home/ubuntu/.local/bin/agy",
        "/usr/local/bin/agy",
        "/usr/bin/agy"
    ]
    for p in candidates:
        if p and os.path.isfile(p) and os.access(p, os.X_OK):
            return p
    return None

def run_terminal_ai_engine(
    user_prompt: str,
    session_id: Optional[str] = None,
    conversation_id: Optional[str] = None,
    timeout: int = 120
) -> tuple[str, str, Optional[str]]:
    """
    【向终端发送请求】调用本地终端 AI CLI (agy / Google Gemini)
    通过命令行参数与 JSON 结构化流进行进程通讯，复用已授权账号额度与工具链，零 API 计费直接驱动
    """
    agy_bin = get_terminal_cli_path()
    if not agy_bin:
        raise RuntimeError("未检测到本地终端 AI CLI (agy)")

    cmd = [agy_bin, "-p", user_prompt, "--output-format", "json", "--dangerously-skip-permissions"]
    if conversation_id:
        cmd.extend(["--conversation", conversation_id])

    try:
        res = subprocess.run(cmd, cwd=str(PROJECT_ROOT), capture_output=True, text=True, timeout=timeout)
    except subprocess.TimeoutExpired:
        thinking_text = (
            f"--- 【终端 AI CLI 调度 Think】向本地终端发送请求 (Google Gemini via agy) ---\n"
            f"【会话绑定 Session】Web 会话: {session_id or '未绑定'} | 终端会话: {conversation_id or '新建'}\n"
            f"【行动 Act】派发终端指令：agy -p [用户提示词]\n"
            f"【安全刹车 Stop】终端 AI 执行耗时超过 {timeout} 秒，强制中断退出防死锁。"
        )
        return thinking_text, "终端执行超时，请稍后重试。", conversation_id
    except Exception as e:
        thinking_text = f"【终端调用异常】向终端发送请求失败: {str(e)}"
        return thinking_text, f"终端调用失败: {str(e)}", conversation_id

    if res.returncode != 0:
        err_msg = res.stderr.strip() or res.stdout.strip() or f"退出码: {res.returncode}"
        thinking_text = (
            f"--- 【终端 AI CLI 调度 Think】向本地终端发送请求 (Google Gemini via agy) ---\n"
            f"【报错 Observe】终端返回非零退出码 ({res.returncode})：\n{err_msg}"
        )
        return thinking_text, "终端执行异常，请检查本地环境。", conversation_id

    try:
        data = json.loads(res.stdout)
        final_reply = data.get("response", "").strip() or "（终端任务已执行完毕）"
        new_conv_id = data.get("conversation_id") or conversation_id
        duration = data.get("duration_seconds", 0)
        num_turns = data.get("num_turns", 1)
        status = data.get("status", "SUCCESS")
        usage = data.get("usage", {})

        in_tok = usage.get("input_tokens", 0)
        out_tok = usage.get("output_tokens", 0)
        think_tok = usage.get("thinking_tokens", 0)
        tot_tok = usage.get("total_tokens", 0)

        thinking_logs = [
            f"--- 【终端 AI CLI 调度 Think】向本地终端发送请求 (Google Gemini via agy CLI) ---",
            f"【会话绑定 Session】Web 会话: {session_id or '未绑定'} | 终端会话: {new_conv_id or '新建'}",
            f"【行动 Act】派发终端指令：agy -p [用户提示词] {'--conversation ' + conversation_id if conversation_id else ''}",
            f"【观察 Observe】终端 AI 推演完成 (执行耗时: {duration:.2f}s, 轮数: {num_turns})",
            f"【资源消耗 Token Usage】输入 Token: {in_tok:,} | 输出 Token: {out_tok:,} (其中深度思考: {think_tok:,}) | 总计: {tot_tok:,} | 状态: {status}",
            f"【底层机制 Note】全流程复用本地终端常驻会话与 Google 账号额度，零额外 API 接口计费。"
        ]

        return "\n\n".join(thinking_logs), final_reply, new_conv_id
    except Exception as e:
        raw_out = res.stdout.strip()
        thinking_text = f"【解析推演】终端返回原始输出，已直接承接：\n{raw_out[:300]}..."
        return thinking_text, raw_out or "（终端任务已完成）", conversation_id

def run_deepseek_api_engine(
    history_messages: List[dict],
    user_prompt: str,
    max_turns: int = 5
) -> tuple[str, str]:
    """
    备用引擎：驱动原有 DeepSeek HTTP API 思考-行动-观察循环
    """
    api_key, base_url = load_deepseek_env()
    client = OpenAI(api_key=api_key, base_url=base_url)

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
            tools=TOOLS_SCHEMA,
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

        # 触发工具调用 (Act 行动 -> Observe 观察)
        for tc in msg.tool_calls:
            func_name = tc.function.name
            try:
                func_args = json.loads(tc.function.arguments) if tc.function.arguments else {}
            except Exception:
                func_args = {}

            thinking_logs.append(f"【行动 Act】决定动用物理工具：{func_name}，参数：{json.dumps(func_args, ensure_ascii=False)}")

            func = TOOL_MAP.get(func_name)
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

def run_harness_engine(
    history_messages: List[dict],
    user_prompt: str,
    session_id: Optional[str] = None,
    conversation_id: Optional[str] = None,
    max_turns: int = 5
) -> tuple[str, str, Optional[str]]:
    """
    核心调度引擎：
    优先向本地终端发送请求（调用 agy CLI 复用终端 AI 与工具）；
    若未检测到本地终端 CLI，自动平滑降级为 DeepSeek HTTP API 循环。
    """
    terminal_cli = get_terminal_cli_path()
    if terminal_cli:
        try:
            return run_terminal_ai_engine(
                user_prompt,
                session_id=session_id,
                conversation_id=conversation_id
            )
        except Exception as e:
            print(f"[Warn] 终端 AI 调用失败，自动降级为 API 引擎: {e}")

    thinking_logs, final_reply = run_deepseek_api_engine(history_messages, user_prompt, max_turns=max_turns)
    return thinking_logs, final_reply, conversation_id

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
                updated_at=r["updated_at"],
                conversation_id=r["conversation_id"] if "conversation_id" in r.keys() else None
            )
            for r in rows
        ]

@app.post("/api/sessions", response_model=SessionItem)
def create_session(req: CreateSessionRequest):
    session_id = str(uuid.uuid4())
    now_str = datetime.now().isoformat()
    with get_db() as conn:
        conn.execute(
            "INSERT INTO sessions (id, title, created_at, updated_at, conversation_id) VALUES (?, ?, ?, ?, ?)",
            (session_id, req.title or "新建对话", now_str, now_str, None)
        )
        conn.commit()
    return SessionItem(id=session_id, title=req.title or "新建对话", created_at=now_str, updated_at=now_str, conversation_id=None)

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

        existing_conv_id = sess["conversation_id"] if "conversation_id" in sess.keys() else None

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

    # 直接调用状态机引擎（向终端发送请求，复用终端 CLI AI）
    thinking_process, final_reply, new_conv_id = run_harness_engine(
        history_list, req.content, session_id=session_id, conversation_id=existing_conv_id
    )

    # 存入助手回复与思考日志，并更新会话绑定的终端 conversation_id
    assistant_msg_id = str(uuid.uuid4())
    assistant_now_str = datetime.now().isoformat()
    with get_db() as conn:
        conn.execute(
            "INSERT INTO messages (id, session_id, role, content, thinking, created_at) VALUES (?, ?, ?, ?, ?, ?)",
            (assistant_msg_id, session_id, "assistant", final_reply, thinking_process, assistant_now_str)
        )
        if new_conv_id and new_conv_id != existing_conv_id:
            conn.execute(
                "UPDATE sessions SET updated_at = ?, conversation_id = ? WHERE id = ?",
                (assistant_now_str, new_conv_id, session_id)
            )
        else:
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
    print(f" 状态机引擎  : 内聚状态机循环引擎 (Think -> Act -> Observe)")
    print(f"==================================================")
    uvicorn.run(app, host="0.0.0.0", port=port)

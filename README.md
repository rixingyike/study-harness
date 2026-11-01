# Study-Harness：打造属于你自己的智能体 Harness

本仓库是微信公众号专栏**《打造属于你自己的智能体 Harness》**的官方配套开源代码库。由浅入深、循序渐进，带你从零手搓一套工业级的智能体基座。

---

## 目录索引与配套代码

* **第 01 讲**：大模型 API 底层通信与前缀缓存（Prompt Caching）极简原理
* **第 02 讲**：Think-Act-Observe 思考-行动-观察三元核心回路
* **第 03 讲**：[`chat_web/`](./chat_web) - 现代多轮对话交互控制台（FastAPI + Vue3 + SQLite 历史会话持久化）
* **第 04 讲**：[`start_kitty.sh`](./start_kitty.sh) - 极简终端守护脚本（Kitty IPC + tmux 会话保活，高效复用终端 AI）

---

## 第 04 讲实战：复用终端里的 AI CLI (`start_kitty.sh`)

各大顶尖厂商（如 Google、Anthropic）都在其官方终端 CLI 中内置了成熟的 Harness 工程能力（上下文自动压缩剪枝、精准 Diff 补丁、工具调用重试）。**复用终端里的成熟 AI，是普通人开发智能体最省钱、最强大的途径。**

### 1. 脚本原理与极简设计

文件 [`start_kitty.sh`](./start_kitty.sh) 仅约 20 行，砍去了冗长的跨平台容错，只保留最核心的工业逻辑：
1. **自动清理残留 Socket**：防止异常断电造成的死锁；
2. **IPC 控制门**：通过 Kitty `-o allow_remote_control=yes --listen-on=unix:...` 开放标准化遥控接口；
3. **会话持久化**：在 Kitty 内部运行 `tmux new-session -A -s workspace`，断网不断会话；
4. **无头服务器渲染**：在无显示器的 Linux 云端，自动调用 `xvfb-run` 创建虚拟帧缓冲（Framebuffer），完美解决 PTY 渲染问题。

### 2. 快速启动

在服务器或本地终端执行：

```bash
chmod +x ./start_kitty.sh
./start_kitty.sh
```

> **提示**：若在后台常驻运行，可使用 `nohup ./start_kitty.sh > /dev/null 2>&1 &`。

### 3. 连接终端并复用 AI CLI（以 Google Gemini 为例）

当后台 Kitty 终端启动后，直接通过 tmux 连接进入工作区：

```bash
tmux attach -t workspace
```

连接进入终端后，直接输入你已安装的 AI CLI 工具即可畅快使用：

* **复用 Google Gemini**：
  输入 `agy`，回车即可启动 Google 官方终端智能体（Antigravity CLI），直接调用背后的 Google Gemini 模型与全套系统级工具链；
* **复用 Claude**：
  输入 `claude`（Claude Code），直接利用已订阅的 Claude Pro 账号额度；
* **复用 DeepSeek / 开源模型**：
  输入 `aider`，直接挂载白菜价的高性价比 API。

离开终端时，按快捷键 `Ctrl + B`，再按 `D` 即可安全脱离（Detach）。服务器后台的 AI 任务不会中断，关机合盖也能全天候自动跑。

### 4. 外部程序远程操控终端 (IPC API)

你的 Web 后端（如 Python/Node.js）或自动化脚本无需 hack 进程，通过 Kitty 开放的 Unix Socket 即可直接遥控终端：

* **向终端发送指令（如启动 agy）**：
  ```bash
  kitten @ --to "unix:$HOME/.kitty.sock" send-text --match id:1 "agy\r"
  ```
* **读取终端屏幕输出**：
  ```bash
  kitten @ --to "unix:$HOME/.kitty.sock" get-text --match id:1
  ```

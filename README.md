# Study-Harness：打造属于你自己的智能体 Harness

本仓库是微信公众号专栏**《打造属于你自己的智能体 Harness》**的官方配套开源代码库。由浅入深、循序渐进，带你从零手搓一套工业级的智能体基座。

---

## 目录索引与配套代码

* **第 01 讲**：大模型 API 底层通信与前缀缓存（Prompt Caching）极简原理
* **第 02 讲**：Think-Act-Observe 思考-行动-观察三元核心回路
* **第 03 讲**：[`chat_web/`](./chat_web) - 现代多轮对话交互控制台（FastAPI + Vue3 + SQLite 历史会话持久化）
* **第 04 讲**：[`start_kitty.sh`](./start_kitty.sh)（服务端终端守护脚本）与 [`connect.sh`](./connect.sh)（macOS 本地一键直连脚本）

---

## 第 04 讲实战：复用终端里的 AI CLI (`start_kitty.sh`)

各大顶尖厂商（如 Google、Anthropic）都在其官方终端 CLI 中内置了成熟的 Harness 工程能力（上下文自动压缩剪枝、精准 Diff 补丁、工具调用重试）。**复用终端里的成熟 AI，是普通人开发智能体最省钱、最强大的途径。**

### 1. 脚本原理与极简设计

文件 [`start_kitty.sh`](./start_kitty.sh) 全长仅 26 行，兼顾了极致精简与高安全容错：
1. **自动清理残留 Socket**：探测活跃实例防重复启动，清理异常断电死锁；
2. **IPC 控制门**：通过 Kitty `-o allow_remote_control=yes --listen-on=unix:...` 开放标准化遥控接口；
3. **会话持久化**：在 Kitty 内部运行 `tmux new-session -A -s workspace`，断网不断会话；
4. **无头服务器渲染**：在无显示器的 Linux 云端，自动调用 `xvfb-run` 创建虚拟帧缓冲（Framebuffer），完美解决 PTY 渲染问题。

#### 完整脚本源码 (`start_kitty.sh`)

```bash
#!/bin/bash
# ==============================================================================
# 极简版 Kitty + tmux 终端守护启动脚本 (专栏《打造属于你自己的智能体 Harness》第 4 讲配套)
# 作用：启动带 IPC 远程控制的 Kitty 终端，内置 tmux workspace 会话，实现终端 AI 的稳定复用
# 特性：支持 systemd 开机自启、实例防重检测、失效死 Socket 自愈清理、无头服务器虚拟渲染
# ==============================================================================
set -e

SOCK_PATH="${HOME}/.kitty.sock"
SOCK="unix:${SOCK_PATH}"
SESSION_NAME="${KITTY_TMUX_SESSION:-workspace}"

# 1. 活跃检测与防冲突：若已有活跃实例在运行，直接提示并安全退出
if [ -S "$SOCK_PATH" ] || [ -e "$SOCK_PATH" ]; then
    if kitten @ --to "$SOCK" ls >/dev/null 2>&1; then
        echo "✅ Kitty 实例已在后台运行中 (Socket: $SOCK_PATH)，无需重复启动。"
        echo "💡 直接执行接入：tmux attach -t $SESSION_NAME"
        exit 0
    fi
    # 若是宕机或异常断电留下的失效死 Socket，自动清理
    echo "⚠️ 检测到残留的失效 socket，正在清理: $SOCK_PATH"
    rm -f "$SOCK_PATH"
fi

echo "🚀 正在启动 Kitty 终端 (IPC: $SOCK, tmux: $SESSION_NAME)..."

# 2. 核心启动：无桌面 Linux 环境借助 xvfb-run 提供虚拟帧缓冲；本地桌面直接启动
if [ -z "$DISPLAY" ] && command -v xvfb-run >/dev/null 2>&1; then
    exec xvfb-run -a -s "-screen 0 1024x768x24" kitty -o allow_remote_control=yes --listen-on="$SOCK" tmux new-session -A -s "$SESSION_NAME"
else
    exec kitty -o allow_remote_control=yes --listen-on="$SOCK" tmux new-session -A -s "$SESSION_NAME"
fi
```

#### 让 AI 生成此脚本的提示语模板 (Prompt)

如果你想让本地 AI（如 Workbuddy、Cursor）自动生成此类脚本，直接发送以下提示语即可：

> **“请帮我写一个极简且安全的 Kitty 终端守护启动脚本 start_kitty.sh：**
> 1. 开启 Kitty 原生 IPC 远程控制监听（`unix:~/.kitty.sock`），并在终端内部默认启动并接入名为 `workspace` 的 tmux 会话；
> 2. 做好防重与自愈：启动前用 `kitten @` 探测该 socket，若已有活跃实例则直接提示退出，若为异常断电残留的死 socket 则自动清理；
> 3. 适配无桌面云服务器：若检测到无 `DISPLAY` 环境变量，自动通过 `xvfb-run` 创建虚拟屏幕渲染，桌面环境则直接启动；
> 4. 核心启动命令使用 `exec` 执行，便于后续 systemd 进程托管，全长控制在 30 行以内。”

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

---

### 5. 生产环境开机自启与守护 (Systemd 部署)

在真实服务器生产环境中，该脚本正是通过 Linux 原生 `systemd` 实现了**开机自启动**与**宕机 3 秒自动拉起自愈**。

服务配置文件位于：`/etc/systemd/system/app-kitty-daemon.service`

```ini
[Unit]
Description=Kitty Terminal Remote Control Daemon
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu
Environment="PATH=/home/ubuntu/.local/bin:/usr/local/bin:/usr/bin:/bin"
ExecStart=/Users/jsmn/workspace/scripts/start_kitty.sh
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
```

#### 自启与运维管理命令

* **设为开机自启并启动**：
  ```bash
  sudo systemctl daemon-reload
  sudo systemctl enable --now app-kitty-daemon.service
  ```
* **查看运行状态**：
  ```bash
  systemctl status app-kitty-daemon.service
  ```
* **重启服务**：
  ```bash
  sudo systemctl restart app-kitty-daemon.service
  ```
* **查看运行日志**：
  ```bash
  journalctl -u app-kitty-daemon.service -f -n 50
  ```

有 `systemd` 在底层保驾护航，配合脚本内部的 Socket 活跃防重检测与失效自愈逻辑，无论服务器怎么重启，后台 AI 终端都能够全天候稳定在线。

---

## 客户端实战：macOS 本地一键直连与密钥免密登录

搞定了服务端的终端保活后，平时我们在个人电脑（如 macOS）上做开发时，怎样做到“一条指令瞬间直达云端 AI 终端”？

### 6. macOS 本地一键直连脚本 (`connect.sh`)

配套客户端脚本：[`connect.sh`](./connect.sh)

```bash
#!/bin/bash
# macOS 本地一键直连云端 AI 终端工作区脚本
SERVER_USER="${SERVER_USER:-ubuntu}"
SERVER_IP="${SERVER_IP:-你的服务器公网IP}"
PORT="${SERVER_PORT:-22}"

# -t 参数强制分配伪终端（PTY），远程直接接入 tmux 会话
exec ssh -t -p "$PORT" "${SERVER_USER}@${SERVER_IP}" "tmux attach -t workspace"
```

#### 使用方法：
1. 赋予执行权限：
   ```bash
   chmod +x ./connect.sh
   ```
2. 直接运行：
   ```bash
   ./connect.sh
   # 或者通过环境变量传入临时 IP：
   SERVER_IP=123.45.67.89 ./connect.sh
   ```
   只要云服务器已启动，敲完这一行直接无缝置身于云端 `tmux workspace` 终端中！直接敲 `agy` 即可唤起 Google Gemini，按 `Ctrl+B` 然后按 `D` 安全断开，本地电脑合盖也不会打断后台任务。

#### 进阶技巧：macOS 极简别名与 SSH Config 极速直达
如果你连 `./connect.sh` 都不想敲，有两种更极致的极简配置方式：

**方式 A：Shell 别名（Alias）**
在本地 `~/.zshrc`（或 `~/.bash_profile`）中加入一行：
```bash
alias ai="ssh -t ubuntu@你的服务器公网IP 'tmux attach -t workspace'"
```
执行 `source ~/.zshrc` 生效后，在 Mac 终端里直接敲一个单词 `ai` 并回车，瞬间直达云端！

**方式 B：SSH 配置文件（~/.ssh/config）**
在 macOS 本地的 `~/.ssh/config` 中追加：
```ssh-config
Host ai
    HostName 你的服务器公网IP
    User ubuntu
    Port 22
    IdentityFile ~/.ssh/id_ed25519
    RequestTTY yes
    RemoteCommand tmux attach -t workspace
```
这样只需执行：
```bash
ssh ai
```
系统会自动调用指定密钥、分配 PTY 并直达 tmux 会话。

---

### 7. 密钥自动免密登录的底层实现原理与配置

为了让一键直连完全不弹密码提示框，同时杜绝服务器被恶意爆破密码的风险，工业界一律采用 **SSH 非对称密钥认证机制**。

#### (1) 底层认证原理（为什么不用输密码，且比密码更安全？）
1. **公钥与私钥配对（非对称加密）**：
   * **私钥（Private Key，如 `id_ed25519`）**：存放在本地 macOS 个人电脑中，权限严格受限（`chmod 600`），**绝对不能泄露给任何人**；
   * **公钥（Public Key，如 `id_ed25519.pub`）**：存放在云端服务器的 `~/.ssh/authorized_keys` 中，相当于在服务器上挂了一把“公开的锁”。
2. **挑战/应答握手流程（Challenge-Response Authentication）**：
   * 当 Mac 发起连接请求时，服务器生成一串随机的字符串（“挑战包”），并用存储的公钥加密后发给 Mac；
   * Mac 本地拿到加密包后，用自己私藏的私钥进行解密，并将解密结果与数字签名发回服务器；
   * 服务器用公钥验证签名通过，瞬间放行登录！
   * **整个过程密码从不在网络中传输，黑客即便截获网络流量也无法推断出私钥**。

#### (2) 三步实操配置流程

**第 1 步：在 macOS 本地生成高强度密钥对**
推荐使用现代高性能的 Ed25519 算法（比传统 RSA 更快、更短、更安全）：
```bash
ssh-keygen -t ed25519 -C "macbook_ai_connect"
```
（一路回车即可，会在本地 `~/.ssh/` 下生成 `id_ed25519` 私钥和 `id_ed25519.pub` 公钥）

**第 2 步：将公钥一键上传到云服务器**
使用系统自带的 `ssh-copy-id` 命令：
```bash
ssh-copy-id -i ~/.ssh/id_ed25519.pub ubuntu@你的服务器公网IP
```
（输入最后一次服务器原本的账号密码，该命令会自动将公钥写入服务器端的 `~/.ssh/authorized_keys` 文件中）

**第 3 步：服务器端安全权限护栏校验**
SSH 协议对文件权限有着极度严格的铁律。如果权限设置过宽，SSH 服务端出于安全考虑会直接拒绝免密登录：
在云服务器端确保以下权限设置正确：
```bash
chmod 700 ~/.ssh
chmod 600 ~/.ssh/authorized_keys
```
在 macOS 本地端确保私钥权限安全：
```bash
chmod 600 ~/.ssh/id_ed25519
```

完成上述配置后，本地无论是执行 `./connect.sh`、`ssh ai` 还是 `ai` 别名，都不会再提示任何密码输入，毫秒级直接连入云端终端，即开即用！

#### (3) 借助 Workbuddy 等本地 AI 智能体一键完成（一句提示语）

如果你的 macOS 个人电脑中安装了类似 **Workbuddy**（或同类具备本地终端执行能力的现代 AI 智能体），你甚至连上面这一串命令都无需手动输入。

你只需要直接对 Workbuddy 说一句大白话提示语：

> **“帮我生成 ed25519 密钥，把公钥配置到远程服务器 123.45.67.89 实现免密登录，并在本地建一个连入 tmux workspace 的一键直连脚本。”**

Workbuddy 就会全自动在后台帮你生成本地密钥对、将公钥写入服务器端 `authorized_keys`、校验权限，并创建可执行的连接脚本。

#### (4) 核心架构哲学：必须先知道“服务器上的 SSH 是用完即销毁的”

尽管本地 AI 工具能够秒级执行上述指令，但**工具永远不会替你构思顶层设计**。要想完成上述这一整套工作流，**创作者必须首先具备这套架构认知，并且深刻理解“服务器上的 SSH 会话是用完就销毁的透明管道”这一核心道理：**

1. **新手的致命误区**：很多初学者以为 SSH 连接必须时刻保持、电脑不能合盖，误把任务直接挂在 SSH 窗口里。一旦遇到 WiFi 抖动或断网，终端掉线导致任务中止，就会陷入无尽的焦虑中；
2. **老手的架构真相**：
   * **SSH 是临时耗材**：SSH 连接不过是一根即插即用、用完即毁的透明传导电缆。敲一行连接，干完按 `Ctrl+B, D` 随时销毁断开，不浪费任何本地与网络资源；
   * **Kitty + tmux 是常驻母体**：真正承载业务执行状态与长久记忆的，是服务器端通过 `xvfb-run` + Kitty Socket + `tmux workspace` 焊死在 Linux 系统底层的常驻中枢。

**正因为你心里预先知道了这套“端云分离、SSH 即连即毁、tmux 常驻保活”的完整方案，你才能下出那句精准的 Workbuddy 提示语，把现代 AI 工具的效能发挥到极致。**

---

### 8. Web 控制台升级：核心循环全面接入终端 AI (agy CLI)

在之前的版本中，Web 框架的状态机循环（Think-Act-Observe）是通过 HTTP 请求直接调用 DeepSeek 接口实现的。

而在第 04 讲中，我们完成了核心循环的升级：**将原先向外部 HTTP API 接口发送请求，全面改造为向本地终端 AI CLI（Google Gemini 驱动的 `agy`）发送请求**。

#### (1) 改造核心点 (`chat_web/backend/main.py`)
1. **指令派发与流控**：
   通过 Python 的 `subprocess.run`，以命令行参数及结构化 JSON 格式直接与 `agy` CLI 交互：
   ```bash
   agy -p "用户输入内容" --output-format json --dangerously-skip-permissions [--conversation <conv_id>]
   ```
2. **多轮对话状态持久化**：
   在 SQLite 数据库的 `sessions` 表中新增 `conversation_id` 字段。每次从终端 AI 返回持久化会话 ID 后自动绑定，实现 Web 页面上的多轮对话与终端 CLI 的上下文无缝同步；
3. **推演与思考日志呈现**：
   将终端 CLI 返回的真实思考推演（`thinking_tokens`）、耗时及 Token 消耗完整格式化为推演日志，直观呈现在 Web 前端的灰色折叠卡片中；
4. **双轨平滑降级（无缝兼容）**：
   自动探测本地终端是否具备 `agy` 命令。若检测到则优先走极速免费的终端 AI 线路；若未检测到终端环境，自动无感降级为原有的 DeepSeek HTTP API 循环，确保读者无论在什么环境下都能开箱即用。

#### (2) 线上运行验证 (Systemd 托管)
修改后的代码已全面部署于服务端的 `app-sh.service`，监听 `PORT=3010`（线上域名 `sh.yishulun.com`）。Web 界面输入消息后，直接由本地常驻的终端 AI 完成推理并极速返回。

#### (3) 官方在线体验站

本套系统已通过 Systemd 常驻运行在云端服务器，配置了反向代理与域名解析，欢迎直接访问体验：

👉 **[https://sh.yishulun.com](https://sh.yishulun.com)**

无论在手机还是电脑端打开，均可新建对话体验多轮推演。点击消息上方的灰色折叠卡片，即可实时查看后台终端 `agy` 驱动的 Think-Act-Observe 全流程推演日志！

#### (4) 架构探秘：为什么共享终端屏幕上看不到打字？（多指令并行与人机解耦）

很多读者实测时会产生疑问：*我明明连着云端终端，为什么在网页上跟 AI 聊天时，终端屏幕上没有打字记录？*

这恰恰是工业级智能体架构最关键的分水岭：
* **若采用“屏幕打字注入”（`tmux send-keys`）**：相当于多个用户同时抢一个键盘和一个光标。若两人同时提问，或者你正用 SSH 敲命令，按键会在屏幕上瞬间拼成乱码，且并发度被锁死在 1（必须排队死等上一个人打完字）；
* **当前采用的“独立子进程架构”（`subprocess.run`）**：每一条 Web 指令都在后台唤醒一个独立的 `agy` 无头算力进程。不仅**多会话在多核 CPU 上完全并行推进**，而且**你在 SSH 终端里改代码、敲命令完全不受哪怕一个光标的打扰**，实现了彻底的人机解耦与记忆隔离。

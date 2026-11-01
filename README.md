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

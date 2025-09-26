# 🎨 Stable Diffusion Telegram Bot

一个强大且特性丰富的 Telegram 机器人，为你桥接 [Stable Diffusion Web UI (AUTOMATIC1111)](https://github.com/AUTOMATIC1111/stable-diffusion-webui) 和 Telegram，无需直接访问 WebUI，即可在 Telegram 聊天中高效生成、管理图片！

<!-- 你可以替换成自己的机器人截图 -->

---

## ✨ 主要功能

- **核心绘图** ：通过 `/draw` 命令和自然语言提示生成图片
- **高级参数** ：支持在命令中动态指定尺寸、步数、采样器、种子等参数（如 `--w`、`--h`、`--s`、`--seed` ...）
- **模型管理** ：远程查看 (`/list_models`) 和切换 (`/use_model`) Stable Diffusion 主模型
- **VAE 管理** ：远程查看 (`/list_vaes`) 和切换 (`/use_vae`) VAE 模型
- **状态查看** ：随时用 `/status` 查询当前加载的模型和 VAE
- **动态配置** ：管理员可用 `/config` 实时修改 API 地址、授权用户和默认参数
- **快捷设置** ：管理员可用 `/set_neg` 快速更新默认负面提示词
- **权限控制** ：区分普通用户和管理员，保证安全，只有授权用户可用，只有管理员可配
- **Docker 支持** ：自带 `Dockerfile`，一键部署
- **持久化存储** ：所有配置保存在 `bot_config.json`，重启不丢失

---

## 📋 先决条件

请确保你具备以下环境与资源：

1. **Python 3.8+**  
   [官方下载链接](https://www.python.org/)
2. **Stable Diffusion Web UI**  
   一个运行中的 AUTOMATIC1111 Web UI 实例  
   **重要！** 启动时必须加 `--api` 参数，如：`./webui.sh --api`
3. **Telegram Bot Token**  
   通过 Telegram 的 [@BotFather](https://t.me/BotFather) 创建机器人并获取
4. **Docker & Docker Compose**（如需 Docker 部署）  
   [安装指引](https://docs.docker.com/get-docker/)

---

## 🚀 安装与启动

你可以选择手动部署或 Docker 部署（推荐）。

---

### 方案一：手动部署（本地或服务器直接运行）

1. **克隆仓库**
    ```bash
    git clone https://github.com/briomianopc/sdwebui_tg_bot.git
    cd sdwebui_tg_bot
    ```

2. **创建虚拟环境并安装依赖**
    ```bash
    python -m venv venv
    # Windows: venv\Scripts\activate
    # Linux/macOS:
    source venv/bin/activate
    pip install -r requirements.txt
    ```

3. **配置参数**

   - 编辑 `sd_tg_bot.py`，填写你的 `TELEGRAM_BOT_TOKEN` 和 `ADMIN_USER_IDS`
   - 创建/编辑 `bot_config.json`，至少填写 `sd_api_url` 和 `allowed_user_ids`（详见下文“配置说明”）

4. **启动机器人**
    ```bash
    python sd_tg_bot.py
    ```
    你会看到 “机器人已启动，开始轮询...” 的提示。

---

### 方案二：Docker 部署（推荐）

1. **克隆仓库**
    ```bash
    git clone https://github.com/briomianopc/sdwebui_tg_bot.git
    cd sdwebui_tg_bot
    ```

2. **配置参数**
   - 同上，编辑 `sd_tg_bot.py` 和 `bot_config.json`
   - **注意**：如 SD WebUI 运行在宿主机，`sd_api_url` 建议设为 `http://host.docker.internal:7860`

3. **构建 Docker 镜像**
    ```bash
    docker build -t sd-tg-bot .
    ```

4. **运行 Docker 容器**
    ```bash
    docker run -d \
      --name sd-tg-bot-container \
      -v "$(pwd)/bot_config.json:/app/bot_config.json" \
      --add-host=host.docker.internal:host-gateway \
      --restart unless-stopped \
      sd-tg-bot
    ```

5. **管理容器**
    - 查看日志：`docker logs -f sd-tg-bot-container`
    - 停止容器：`docker stop sd-tg-bot-container`
    - 启动容器：`docker start sd-tg-bot-container`

---

## ⚙️ 配置说明

你需要配置两个地方：

### 1. `sd_tg_bot.py`
- `TELEGRAM_BOT_TOKEN`：你的 BotFather Token
- `ADMIN_USER_IDS`：Python 列表，填你自己的 Telegram User ID（可通过 [@userinfobot](https://t.me/userinfobot) 获取）。只有这些 ID 可用管理命令

### 2. `bot_config.json`
- `sd_api_url`：Stable Diffusion Web UI API 地址
- `allowed_user_ids`：允许使用机器人的 Telegram User ID 列表
- `default_settings`：默认绘图参数（如 negative_prompt、steps、sampler_name 等）

首次启动时如未存在会自动生成。

---

## 📖 使用方法（命令总览）

与你的机器人对话，支持以下命令：

### 所有授权用户可用

| 命令 | 描述 | 示例 |
| ---- | ---- | ---- |
| `/draw <prompt> [params]` | 生成图片 | `/draw a cute cat --w 768 --s 30` |
| `/status` | 查看当前模型和 VAE |  |
| `/list_models` | 列出所有可用主模型 |  |
| `/list_vaes` | 列出所有可用 VAE |  |
| `/help` | 显示帮助信息 |  |

### 仅管理员可用

| 命令 | 描述 | 示例 |
| ---- | ---- | ---- |
| `/set_neg <text>` | 设置默认负面提示词 | `/set_neg blurry, low quality` |
| `/use_model <name>` | 切换主模型（需完整名称） | `/use_model anything-v5-PrtRE.safetensors` |
| `/use_vae <name>` | 切换 VAE（需完整名称） | `/use_vae vae-ft-mse-840000-ema-pruned.safetensors` |
| `/config show` | 显示完整 JSON 配置 |  |
| `/config <key> <value>` | 修改一个配置项 | `/config default_settings.steps 35` |
| `/config add_user <id>` | 授权新用户 | `/config add_user 987654321` |
| `/config remove_user <id>` | 移除用户授权 | `/config remove_user 987654321` |

---

## 📝 常见问题

- **如何获取自己的 Telegram User ID？**
  > 在 Telegram 搜索 [@userinfobot](https://t.me/userinfobot)，发送 /start 即可获取
- **Docker 网络连接问题？**
  > 推荐 WebUI 启动参数使用 `--api`，并将 `sd_api_url` 设置为 `http://host.docker.internal:7860`
- **配置修改后需重启吗？**
  > 基本配置变动实时生效，无需重启；如修改代码请重启

---

## ⚖️ 许可证

本项目采用 [MIT 许可证](LICENSE)。

---

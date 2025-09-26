# 🎨 Stable Diffusion Telegram Bot

这是一个功能强大、特性丰富的 Telegram 机器人，它充当了你本地或服务器上运行的 [Stable Diffusion Web UI (AUTOMATIC1111)](https://github.com/AUTOMATIC1111/stable-diffusion-webui) 的远程控制面板。

通过这个机器人，你可以直接在 Telegram 中生成图片、管理模型、切换 VAE 以及调整各种默认设置，而无需直接访问 Web UI 界面。

 <!-- 你可以替换成自己的机器人截图 -->

## ✨ 主要功能

-   **核心绘图功能**: 使用 `/draw` 命令，通过文字提示生成图片。
-   **高级参数支持**: 在 `/draw` 命令中动态指定尺寸、步数、采样器、种子等 (`--w`, `--h`, `--s`, `--seed` ...)。
-   **模型管理**: 远程查看 (`/list_models`) 和切换 (`/use_model`) Stable Diffusion 主模型。
-   **VAE 管理**: 远程查看 (`/list_vaes`) 和切换 (`/use_vae`) VAE 模型。
-   **状态查看**: 使用 `/status` 命令随时检查 Web UI 当前加载的模型和 VAE。
-   **动态配置**: 管理员可通过 `/config` 命令实时修改 API 地址、授权用户和默认绘图参数。
-   **快捷设置**: 管理员可通过 `/set_neg` 命令快速更新默认的负面提示词。
-   **权限控制**: 清晰的管理员和普通用户角色，确保只有授权用户才能使用，只有管理员才能修改配置。
-   **Docker 支持**: 提供 `Dockerfile`，实现一键式、可移植的部署。
-   **持久化存储**: 所有配置都保存在 `bot_config.json` 中，即使机器人重启也不会丢失。

## 📋 先决条件

在开始之前，请确保你已准备好以下各项：

1.  **Python 3.8+**: [下载地址](https://www.python.org/)
2.  **Stable Diffusion Web UI**: 一个正在运行的 AUTOMATIC1111 Web UI 实例。
    -   **最重要**: 启动 Web UI 时**必须**添加 `--api` 启动参数。例如：`./webui.sh --api`。
3.  **Telegram Bot Token**: 在 Telegram 中与 `@BotFather` 对话，创建一个新的机器人以获取此 Token。
4.  **Docker & Docker Compose** (如果选择 Docker 部署): [安装指南](https://docs.docker.com/get-docker/)

## 🚀 安装与启动

你可以选择两种方式来部署此机器人：**手动部署**或**通过 Docker 部署**（推荐）。

### 方案一：手动部署 (在本地或服务器直接运行)

1.  **克隆仓库**:
    ```bash
    git clone https://your-repo-url.com/sd-tg-bot.git
    cd sd-tg-bot
2.
创建虚拟环境并安装依赖:

# 创建虚拟环境
python -m venv venv
# 激活虚拟环境 (Windows: venv\Scripts\activate)
source venv/bin/activate
# 安装依赖
pip install -r requirements.txt
3.
进行配置 (详见下方的配置说明部分):

修改 sd_tg_bot.py 文件中的 TELEGRAM_BOT_TOKEN 和 ADMIN_USER_IDS。

创建并修改 bot_config.json 文件，至少要确认 sd_api_url 和 allowed_user_ids。

4.
启动机器人:

python sd_tg_bot.py
你将在终端看到 "机器人已启动，开始轮询..." 的消息。

方案二：通过 Docker 部署 (推荐)
使用 Docker 可以将机器人及其环境完全隔离，部署和管理都非常方便。

1.
克隆仓库:

git clone https://your-repo-url.com/sd-tg-bot.git
cd sd-tg-bot
2.
进行配置 (详见下方的配置说明部分):

修改 sd_tg_bot.py 文件中的 TELEGRAM_BOT_TOKEN 和 ADMIN_USER_IDS。

创建并修改 bot_config.json 文件。特别注意：如果 SD Web UI 运行在宿主机上，你需要将 sd_api_url 设置为 "http://host.docker.internal:7860"。

3.
构建 Docker 镜像:

docker build -t sd-tg-bot .
4.
运行 Docker 容器:
此命令会在后台启动容器，并将配置文件挂载到容器中，实现持久化存储。

docker run -d \
  --name sd-tg-bot-container \
  -v "$(pwd)/bot_config.json:/app/bot_config.json" \
  --add-host=host.docker.internal:host-gateway \
  --restart unless-stopped \
  sd-tg-bot
5.
管理容器:

查看日志: docker logs -f sd-tg-bot-container

停止容器: docker stop sd-tg-bot-container

启动容器: docker start sd-tg-bot-container

⚙️ 配置说明
你需要配置两个地方：

1.
sd_tg_bot.py:

TELEGRAM_BOT_TOKEN: 填入你从 @BotFather 获取的 Token。

ADMIN_USER_IDS: 一个 Python 列表，填入你自己的 Telegram User ID (纯数字，通过 @userinfobot 获取)。只有此列表中的用户才能执行管理员命令。

2.
bot_config.json:
这个文件存储了机器人的所有运行时配置。首次启动时若不存在会自动创建。

sd_api_url: 你的 Stable Diffusion Web UI API 地址。

allowed_user_ids: 一个 JSON 数组，包含所有有权使用此机器人的用户的 User ID。

default_settings: 默认的绘图参数，如 negative_prompt, steps, sampler_name 等。

📖 使用方法 (命令列表)
与你的机器人开始聊天，发送以下命令：

所有授权用户可用
命令	描述	示例
/draw <prompt> [params]	核心绘图命令，生成图片。	/draw a cute cat --w 768 --s 30
/status	查看 Web UI 当前加载的模型和 VAE。	
/list_models	列出所有可用的主模型。	
/list_vaes	列出所有可用的 VAE。	
/help	显示此帮助信息。	
仅限管理员可用
命令	描述	示例
/set_neg <text>	快捷设置默认的负面提示词。	/set_neg blurry, low quality
/use_model <name>	切换主模型。名称需完整。	/use_model anything-v5-PrtRE.safetensors
/use_vae <name>	切换 VAE 模型。名称需完整。	/use_vae vae-ft-mse-840000-ema-pruned.safetensors
/config show	显示完整的 JSON 配置。	
/config <key> <value>	修改一个配置项。	/config default_settings.steps 35
/config add_user <id>	授权一个新用户。	/config add_user 987654321
/config remove_user <id>	移除一个用户的授权。	/config remove_user 987654321
⚖️ 许可证
本项目采用 MIT 许可证。

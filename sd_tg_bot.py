# -*- coding: utf-8 -*-

"""
A comprehensive Telegram Bot to interact with the Stable Diffusion Web UI API.
Final version including all features: drawing, config management, model/VAE control,
and a dedicated command for setting the default negative prompt.
"""

import logging
import requests
import base64
import io
import json
import os
import shlex

from telegram import Update, InputFile
from telegram.ext import Application, CommandHandler, ContextTypes

# --- 基础配置 (需要你来修改) ---
# 1. 在这里填入你从 @BotFather 获取的 Telegram Bot Token
TELEGRAM_BOT_TOKEN = "YOUR_TELEGRAM_BOT_TOKEN"

# 2. 在这里填入你自己的 Telegram User ID，作为初始管理员。
#    在 Telegram 中搜索 @userinfobot 可以获取你的 ID。
ADMIN_USER_IDS = [123456789] 

# 配置文件名
CONFIG_FILE = "bot_config.json"

# --- 日志配置 ---
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# --- 配置管理 ---
def load_config():
    """从 JSON 文件加载配置，如果文件不存在则创建默认配置。"""
    if not os.path.exists(CONFIG_FILE):
        logger.info(f"配置文件 {CONFIG_FILE} 不存在，将创建默认配置。")
        default_config = {
            "sd_api_url": "http://127.0.0.1:7860",
            "allowed_user_ids": ADMIN_USER_IDS,
            "default_settings": {
                "prompt": "",
                "negative_prompt": "nsfw, (low quality, worst quality:1.4), bad anatomy, bad hands, text, error, missing fingers, extra digit, fewer digits, cropped, worst quality, low quality, normal quality, jpeg artifacts, signature, watermark, username, blurry",
                "seed": -1,
                "sampler_name": "DPM++ 2M Karras",
                "steps": 28,
                "cfg_scale": 7.0,
                "width": 512,
                "height": 768,
                "restore_faces": True,
                "enable_hr": False,
                "hr_scale": 2.0,
                "hr_upscaler": "Latent",
                "denoising_strength": 0.7,
                "override_settings": {}
            }
        }
        save_config(default_config)
        return default_config
    try:
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            logger.info(f"成功从 {CONFIG_FILE} 加载配置。")
            return json.load(f)
    except (json.JSONDecodeError, IOError) as e:
        logger.error(f"加载配置文件失败: {e}，机器人将无法启动。")
        return {}

def save_config(config_data):
    """将配置安全地保存到 JSON 文件。"""
    try:
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(config_data, f, indent=4, ensure_ascii=False)
        logger.info(f"配置已成功保存到 {CONFIG_FILE}。")
    except IOError as e:
        logger.error(f"保存配置文件失败: {e}")

config = load_config()

# --- 参数解析辅助函数 ---
def parse_draw_args(args):
    """安全地解析 /draw 命令的参数，支持带引号的值。"""
    full_text = " ".join(args)
    try:
        parts = shlex.split(full_text)
    except ValueError:
        return full_text, {}
    
    prompt_parts, override_params, i = [], {}, 0
    while i < len(parts):
        part = parts[i]
        if part.startswith("--"):
            key = part[2:]
            if i + 1 < len(parts) and not parts[i+1].startswith("--"):
                value = parts[i+1]
                i += 2
            else:
                value = True
                i += 1
            override_params[key] = value
        else:
            prompt_parts.append(part)
            i += 1
            
    prompt = " ".join(prompt_parts)
    
    param_map = {'s': 'steps', 'w': 'width', 'h': 'height', 'cfg': 'cfg_scale', 'sampler': 'sampler_name', 'seed': 'seed', 'neg': 'negative_prompt'}
    final_params = {}
    for key, value in override_params.items():
        final_key = param_map.get(key, key)
        if isinstance(value, str):
            if value.lower() == 'true': value = True
            elif value.lower() == 'false': value = False
            elif value.isdigit(): value = int(value)
            elif value.replace('.', '', 1).isdigit(): value = float(value)
        final_params[final_key] = value
        
    return prompt, final_params

# --- Telegram 命令处理函数 ---

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_html(f"你好，{update.effective_user.mention_html()}! 我是你的私人AI绘图助理。输入 /help 查看所有命令。")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """根据用户身份显示不同的帮助信息。"""
    is_admin = update.effective_user.id in ADMIN_USER_IDS
    help_text = """
🎨 *Stable Diffusion 绘图机器人帮助文档* 🎨
---
*基础绘图功能 (所有授权用户可用)*
➡️  `/draw <prompt> [参数]`
核心绘图命令。示例: `/draw a cat --w 768 --s 30`
---
*模型和状态管理 (所有授权用户可用)*
➡️  `/status`: 查看当前模型和 VAE。
➡️  `/list_models`: 列出所有可用主模型。
➡️  `/list_vaes`: 列出所有可用 VAE。
"""
    admin_help_text = """
---
*管理员功能 (仅限管理员)*
➡️  `/set_neg <text>`
快捷设置默认的负面提示词。

➡️  `/use_model <model_name>`
切换 Web UI 使用的主模型。

➡️  `/use_vae <vae_name>`
切换 Web UI 使用的 VAE。

➡️  `/config show`: 显示所有配置。
➡️  `/config <key> <value>`: 修改配置项。
➡️  `/config add_user <id>`: 添加授权用户。
➡️  `/config remove_user <id>`: 移除授权用户。
"""
    final_help_text = help_text + (admin_help_text if is_admin else "")
    await update.message.reply_text(final_help_text, parse_mode='Markdown')

async def config_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """处理高级配置命令。"""
    if update.effective_user.id not in ADMIN_USER_IDS:
        await update.message.reply_text("抱歉，你没有权限执行此操作。")
        return
        
    args = context.args
    if not args:
        await update.message.reply_text("用法: /config [show|add_user|remove_user|<key>] [...]")
        return

    command, global_config = args[0].lower(), globals()['config']
    if command == "show":
        await update.message.reply_text(f"<pre>{json.dumps(global_config, indent=2, ensure_ascii=False)}</pre>", parse_mode='HTML')
    elif command in ["add_user", "remove_user"]:
        if len(args) != 2 or not args[1].isdigit():
            await update.message.reply_text(f"用法: /config {command} <用户ID>")
            return
        user_to_modify = int(args[1])
        user_list = global_config["allowed_user_ids"]
        if command == "add_user" and user_to_modify not in user_list:
            user_list.append(user_to_modify)
            save_config(global_config)
            await update.message.reply_text(f"用户 {user_to_modify} 已被授权。")
        elif command == "remove_user" and user_to_modify in user_list:
            user_list.remove(user_to_modify)
            save_config(global_config)
            await update.message.reply_text(f"用户 {user_to_modify} 的授权已被移除。")
    elif len(args) >= 2:
        key_path, value_str = args[0], " ".join(args[1:])
        if value_str.lower() in ['true', 'false']: value = value_str.lower() == 'true'
        elif value_str.isdigit(): value = int(value_str)
        elif value_str.replace('.', '', 1).isdigit(): value = float(value_str)
        else: value = value_str
        try:
            keys, d = key_path.split('.'), global_config
            for k in keys[:-1]: d = d[k]
            d[keys[-1]] = value
            save_config(global_config)
            await update.message.reply_text(f"配置 '{key_path}' 已更新。")
        except (KeyError, TypeError) as e:
            await update.message.reply_text(f"配置项 '{key_path}' 无效或路径错误。错误: {e}")
    else:
        await update.message.reply_text("无效的 /config 命令。")

async def draw(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """处理核心的绘图请求。"""
    if update.message.from_user.id not in config.get("allowed_user_ids", []):
        await update.message.reply_text("抱歉，你没有权限使用此机器人。")
        return
        
    if not context.args:
        await update.message.reply_text("用法: /draw <prompt> [参数]")
        return
    
    prompt, override_params = parse_draw_args(context.args)
    if not prompt:
        await update.message.reply_text("错误：Prompt 不能为空！")
        return

    logger.info(f"用户 {update.message.from_user.id} 请求绘图。Prompt: '{prompt}', 参数: {override_params}")
    sent_message = await update.message.reply_text(f"收到请求！正在为您生成图片... 🎨\nPrompt: {prompt}")
    
    payload = config["default_settings"].copy()
    payload["prompt"] = prompt
    payload.update(override_params)
    api_url = f"{config.get('sd_api_url', '')}/sdapi/v1/txt2img"

    try:
        response = requests.post(url=api_url, json=payload, timeout=300)
        response.raise_for_status()
        r = response.json()
        
        if "images" in r and r['images']:
            image_data = base64.b64decode(r['images'][0])
            image_stream = io.BytesIO(image_data)
            image_stream.name = 'generated_image.png'
            
            caption_parts = [f"✨ Prompt: {prompt}"]
            if override_params:
                caption_parts.append("\n⚙️ 自定义参数:")
                for key, val in override_params.items():
                    caption_parts.append(f"  - {key}: {val}")
            
            await context.bot.send_photo(chat_id=update.effective_chat.id, photo=InputFile(image_stream), caption="\n".join(caption_parts))
            await context.bot.delete_message(chat_id=sent_message.chat_id, message_id=sent_message.message_id)
        else:
            await update.message.reply_text(f"图片生成失败，API 未返回图片数据。响应: `{r}`", parse_mode='Markdown')
    except requests.exceptions.RequestException as e:
        await update.message.reply_text(f"无法连接到 Stable Diffusion API。\n错误: {e}")
    except Exception as e:
        logger.error(f"处理绘图请求时发生未知错误: {e}", exc_info=True)
        await update.message.reply_text(f"处理请求时发生未知错误: {e}")

async def get_current_status(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.effective_user.id not in config.get("allowed_user_ids", []):
        await update.message.reply_text("抱歉，你没有权限。")
        return
    try:
        response = requests.get(url=f"{config.get('sd_api_url', '')}/sdapi/v1/options", timeout=30)
        response.raise_for_status()
        options = response.json()
        await update.message.reply_text(f"📊 *当前状态*\n🎨 *主模型*: `{options.get('sd_model_checkpoint', 'N/A')}`\n✨ *VAE*: `{options.get('sd_vae', 'N/A')}`", parse_mode='Markdown')
    except requests.exceptions.RequestException as e:
        await update.message.reply_text(f"无法获取状态。错误: {e}")

async def list_resources(update: Update, context: ContextTypes.DEFAULT_TYPE, resource_type: str) -> None:
    if update.effective_user.id not in config.get("allowed_user_ids", []):
        await update.message.reply_text("抱歉，你没有权限。")
        return
    endpoint_map = {'models': '/sdapi/v1/sd-models', 'vaes': '/sdapi/v1/sd-vaes'}
    title_map = {'models': '可用的大模型', 'vaes': '可用的 VAEs'}
    api_url = f"{config.get('sd_api_url', '')}{endpoint_map[resource_type]}"
    await update.message.reply_text(f"正在获取 {title_map[resource_type]} 列表...")
    try:
        response = requests.get(url=api_url, timeout=60)
        response.raise_for_status()
        items = response.json()
        if not items:
            await update.message.reply_text(f"未找到任何{title_map[resource_type]}。")
            return
        item_names = [item.get('title' if resource_type == 'models' else 'model_name', 'N/A') for item in items]
        message = f"📚 *{title_map[resource_type]}*:\n\n" + "\n".join([f"`{name}`" for name in item_names])
        for i in range(0, len(message), 4096):
            await update.message.reply_text(message[i:i+4096], parse_mode='Markdown')
    except requests.exceptions.RequestException as e:
        await update.message.reply_text(f"无法获取 {resource_type} 列表。错误: {e}")

async def list_models(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None: await list_resources(update, context, 'models')
async def list_vaes(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None: await list_resources(update, context, 'vaes')

async def use_resource(update: Update, context: ContextTypes.DEFAULT_TYPE, resource_type: str) -> None:
    if update.effective_user.id not in ADMIN_USER_IDS:
        await update.message.reply_text("抱歉，此为管理员命令。")
        return
    if not context.args:
        await update.message.reply_text(f"用法: /use_{resource_type[:-1]} <名称>")
        return
    resource_name = " ".join(context.args)
    payload_map = {'models': {'sd_model_checkpoint': resource_name}, 'vaes': {'sd_vae': resource_name}}
    await update.message.reply_text(f"正在切换 {resource_type[:-1]} 到 `{resource_name}`...", parse_mode='Markdown')
    try:
        response = requests.post(url=f"{config.get('sd_api_url', '')}/sdapi/v1/options", json=payload_map[resource_type], timeout=120)
        response.raise_for_status()
        await update.message.reply_text(f"✅ 成功切换为 `{resource_name}`！", parse_mode='Markdown')
    except requests.exceptions.RequestException as e:
        await update.message.reply_text(f"❌ 切换失败！错误: {e}", parse_mode='Markdown')

async def use_model(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None: await use_resource(update, context, 'models')
async def use_vae(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None: await use_resource(update, context, 'vaes')

async def set_neg_prompt(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """快捷设置默认的负面提示词。"""
    if update.effective_user.id not in ADMIN_USER_IDS:
        await update.message.reply_text("抱歉，此为管理员命令。")
        return
    if not context.args:
        current_neg = config.get("default_settings", {}).get("negative_prompt", "未设置")
        await update.message.reply_text(f"用法: /set_neg <新的负面提示词>\n\n当前默认值是:\n`{current_neg}`", parse_mode='Markdown')
        return
    config["default_settings"]["negative_prompt"] = " ".join(context.args)
    save_config(config)
    await update.message.reply_text(f"✅ 默认负面提示词已更新！", parse_mode='Markdown')

def main() -> None:
    """启动机器人。"""
    if not config:
        logger.critical(f"配置文件 {CONFIG_FILE} 加载失败，机器人无法启动。请检查文件是否存在且格式正确。")
        return

    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    
    handlers = {
        "start": start, "help": help_command, "draw": draw, "config": config_command,
        "status": get_current_status, "list_models": list_models, "list_vaes": list_vaes,
        "use_model": use_model, "use_vae": use_vae,
        "set_neg": set_neg_prompt
    }
    for command, handler_func in handlers.items():
        application.add_handler(CommandHandler(command, handler_func))

    logger.info("机器人已启动，开始轮询...")
    application.run_polling()

if __name__ == "__main__":
    main()

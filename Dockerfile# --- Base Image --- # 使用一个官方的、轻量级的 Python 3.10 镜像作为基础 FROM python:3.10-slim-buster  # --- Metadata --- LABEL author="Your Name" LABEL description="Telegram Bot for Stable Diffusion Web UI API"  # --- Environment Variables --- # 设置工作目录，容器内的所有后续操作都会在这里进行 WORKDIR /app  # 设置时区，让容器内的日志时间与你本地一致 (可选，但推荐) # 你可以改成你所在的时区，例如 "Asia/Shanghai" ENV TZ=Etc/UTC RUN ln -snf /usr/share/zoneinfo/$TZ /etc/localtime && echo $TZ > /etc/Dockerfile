# --- Base Image ---
# 使用一个官方的、轻量级的 Python 3.10 镜像作为基础
FROM python:3.10-slim-buster

# --- Metadata ---
LABEL author="Your Name"
LABEL description="Telegram Bot for Stable Diffusion Web UI API"

# --- Environment Variables ---
# 设置工作目录，容器内的所有后续操作都会在这里进行
WORKDIR /app

# 设置时区，让容器内的日志时间与你本地一致 (可选，但推荐)
# 你可以改成你所在的时区，例如 "Asia/Shanghai"
ENV TZ=Etc/UTC
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

# --- Dependency Installation ---
# 仅复制 requirements.txt 文件，这样可以利用 Docker 的缓存机制。
# 只有当这个文件改变时，才会重新安装依赖，从而加快构建速度。
COPY requirements.txt .

# 安装依赖。--no-cache-dir 减少镜像大小。
RUN pip install --no-cache-dir -r requirements.txt

# --- Application Code ---
# 将项目目录下的所有其他文件 (主要是 sd_tg_bot.py) 复制到容器的工作目录
COPY . .

# --- Run Command ---
# 当容器启动时，执行这个命令来运行你的机器人
CMD ["python", "sd_tg_bot.py"]

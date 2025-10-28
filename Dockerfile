FROM python:3.10.11-alpine

LABEL maintainer="dydydd" \
      description="RaisBot - Emby & Jellyfin管理机器人" \
      version="1.2.1"

WORKDIR /app

# 设置环境变量
ENV TZ=Asia/Shanghai \
    DOCKER_MODE=1 \
    PYTHONUNBUFFERED=1

# 复制依赖文件
COPY requirements.txt requirements.txt

# 安装系统依赖和Python包
RUN apk add --no-cache \
    mysql-client \
    mariadb-connector-c \
    tzdata \
    gcc \
    musl-dev \
    libffi-dev \
    && pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt \
    && apk del gcc musl-dev libffi-dev

# 复制应用代码
COPY bot ./bot
COPY *.py ./
COPY config_example.json ./

# 创建必要的目录
RUN mkdir -p ./log ./db_backup

# 设置工作目录权限
RUN chmod -R 755 /app

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD python -c "import sys; sys.exit(0)" || exit 1

# 启动应用
ENTRYPOINT ["python3"]
CMD ["main.py"]
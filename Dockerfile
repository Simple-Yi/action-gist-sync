FROM python:3-slim

# 在非交互式环境中使用 apt-get
ARG DEBIAN_FRONTEND="noninteractive"

# 更新包列表、安装 git，并清理缓存以减小镜像体积
RUN apt-get update \
    && apt-get install --yes --no-install-recommends git \
    && rm -rf /var/lib/apt/lists/*

# 使用 COPY，并且分离依赖文件复制与安装，以利用 Docker 缓存
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

# 复制所有剩余的源代码
COPY . .

# 使用 ENTRYPOINT 定义 Action 的入口
ENTRYPOINT ["python", "/app/main.py"]
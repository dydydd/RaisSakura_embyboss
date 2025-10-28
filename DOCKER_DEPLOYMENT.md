# Docker 部署指南

## 📦 Docker 镜像信息

- **镜像名称**: `dydydd/raisbot`
- **初始版本**: `v1.2.1`
- **支持架构**: `linux/amd64`, `linux/arm64`

## 🚀 快速开始

### 1. 拉取镜像

```bash
# 拉取最新版本
docker pull dydydd/raisbot:latest

# 拉取指定版本
docker pull dydydd/raisbot:1.2.1
```

### 2. 准备配置文件

创建 `config.json` 文件（参考 `config_example.json`）：

```json
{
  "bot_token": "your_bot_token",
  "api_id": "your_api_id",
  "api_hash": "your_api_hash",
  "emby_api": "your_emby_api_key",
  "emby_url": "http://your-emby-server:8096",
  "jellyfin_api": "your_jellyfin_api_key",
  "jellyfin_url": "http://your-jellyfin-server:8096",
  ...
}
```

### 3. 运行容器

#### 使用 Docker 命令

```bash
docker run -d \
  --name raisbot \
  --restart unless-stopped \
  -v $(pwd)/config.json:/app/config.json \
  -v $(pwd)/log:/app/log \
  -v $(pwd)/db_backup:/app/db_backup \
  -e TZ=Asia/Shanghai \
  dydydd/raisbot:latest
```

#### 使用 Docker Compose

创建 `docker-compose.yml`:

```yaml
version: '3.8'

services:
  raisbot:
    image: dydydd/raisbot:latest
    container_name: raisbot
    restart: unless-stopped
    environment:
      - TZ=Asia/Shanghai
      - DOCKER_MODE=1
    volumes:
      - ./config.json:/app/config.json
      - ./log:/app/log
      - ./db_backup:/app/db_backup
    networks:
      - raisbot_network

networks:
  raisbot_network:
    driver: bridge
```

启动服务：

```bash
docker-compose up -d
```

## 🔧 配置说明

### 环境变量

| 变量 | 说明 | 默认值 |
|------|------|--------|
| `TZ` | 时区设置 | `Asia/Shanghai` |
| `DOCKER_MODE` | Docker模式标识 | `1` |
| `PYTHONUNBUFFERED` | Python输出不缓冲 | `1` |

### 挂载目录

| 容器路径 | 说明 | 是否必需 |
|---------|------|----------|
| `/app/config.json` | 配置文件 | ✅ 必需 |
| `/app/log` | 日志目录 | 推荐 |
| `/app/db_backup` | 数据库备份目录 | 推荐 |

## 📝 版本管理

### 自动构建触发条件

1. **推送到主分支** - 自动构建并推送 `latest` 标签
2. **创建版本标签** - 推送 `v*.*.*` 格式标签，自动构建对应版本
3. **手动触发** - 在 GitHub Actions 中手动指定版本号

### 标签说明

- `latest` - 最新版本
- `1.2.1` - 具体版本号
- `20231028` - 日期标签（主分支自动构建）

### 创建新版本

```bash
# 创建并推送版本标签
git tag v1.2.2
git push origin v1.2.2
```

## 🔐 GitHub Secrets 配置

在 GitHub 仓库设置中添加以下 Secrets：

| Secret Name | 说明 |
|-------------|------|
| `DOCKER_USERNAME` | Docker Hub 用户名 |
| `DOCKER_PASSWORD` | Docker Hub 访问令牌 |

### 获取 Docker Hub 访问令牌

1. 登录 [Docker Hub](https://hub.docker.com/)
2. 进入 Account Settings > Security
3. 点击 "New Access Token"
4. 创建一个新的访问令牌并保存

## 📊 查看日志

```bash
# 查看实时日志
docker logs -f raisbot

# 查看最近100行日志
docker logs --tail 100 raisbot
```

## 🔄 更新容器

```bash
# 停止并删除旧容器
docker stop raisbot
docker rm raisbot

# 拉取最新镜像
docker pull dydydd/raisbot:latest

# 重新运行容器
docker run -d \
  --name raisbot \
  --restart unless-stopped \
  -v $(pwd)/config.json:/app/config.json \
  -v $(pwd)/log:/app/log \
  -v $(pwd)/db_backup:/app/db_backup \
  -e TZ=Asia/Shanghai \
  dydydd/raisbot:latest
```

或使用 Docker Compose：

```bash
docker-compose pull
docker-compose up -d
```

## 🐛 故障排查

### 容器无法启动

1. 检查配置文件是否正确挂载
2. 查看容器日志：`docker logs raisbot`
3. 检查配置文件格式是否正确

### 连接数据库失败

1. 确保数据库服务正常运行
2. 检查网络连接配置
3. 验证数据库凭据是否正确

### 权限问题

```bash
# 修改日志目录权限
sudo chmod -R 755 ./log ./db_backup
```

## 📚 更多信息

- [项目主页](https://github.com/FeiyueSakura/embyboss)
- [Docker Hub](https://hub.docker.com/r/dydydd/raisbot)
- [问题反馈](https://github.com/FeiyueSakura/embyboss/issues)

## 🆕 新功能

### v1.2.1 更新内容

- ✅ 添加 Jellyfin 完整支持
- ✅ Jellyfin API 与 Emby API 完全独立
- ✅ 新增 Jellyfin 媒体库管理命令
- ✅ 服务器面板支持同时显示 Emby 和 Jellyfin
- ✅ 优化 Docker 镜像构建
- ✅ 支持多架构（amd64/arm64）自动构建

### Jellyfin 配置示例

```json
{
  "jellyfin_api": "your_jellyfin_api_key",
  "jellyfin_url": "http://your-jellyfin-server:8096",
  "jellyfin_line": "Jellyfin服务器",
  "jellyfin_lib_ids": ["library_id_1", "library_id_2"],
  "jellyfin_hidden": ["hidden_lib_id"]
}
```

### 新增命令

- `/jfall` - 全开Jellyfin媒体库权限
- `/jfnone` - 全关Jellyfin媒体库权限
- `/jfon` - 开启指定Jellyfin媒体库
- `/jfoff` - 关闭指定Jellyfin媒体库

## 📄 许可证

本项目采用 MIT 许可证
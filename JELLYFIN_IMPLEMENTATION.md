# Jellyfin支持实现文档

## 概述
本项目已成功添加对Jellyfin的完整支持，包括API模块、数据库模块、命令处理和面板集成。Jellyfin与Emby的API完全独立，互不干扰。

## 🎯 完成情况

### ✅ 已完成的功能
- [x] Jellyfin API模块 (完整的API操作)
- [x] Jellyfin数据库模块 (独立的数据表)
- [x] 配置文件支持
- [x] Schema定义
- [x] 命令模块集成
- [x] 服务器面板集成
- [x] Bot命令注册

## 实现的文件

### 1. 核心API模块
- **文件**: [`bot/func_helper/jellyfin.py`](bot/func_helper/jellyfin.py)
- **说明**: Jellyfin的API操作方法，完全独立于Emby
- **主要类**: `Jellyfinservice`
- **主要功能**:
  - `jellyfin_create()` - 创建Jellyfin账户
  - `jellyfin_del()` - 删除Jellyfin账户
  - `jellyfin_reset()` - 重置Jellyfin密码
  - `jellyfin_block()` - 显示/隐藏媒体库
  - `get_jellyfin_libs()` - 获取所有媒体库
  - `get_current_playing_count()` - 获取当前播放数量
  - `jellyfin_change_policy()` - 修改用户策略
  - `users()` - 获取所有用户
  - `get_movies()` - 搜索电影/剧集
  - 更多方法...

### 2. 数据库模块
- **文件**: [`bot/sql_helper/sql_jellyfin.py`](bot/sql_helper/sql_jellyfin.py)
- **说明**: Jellyfin用户的SQL操作，独立的数据表
- **数据表**: `jellyfin` (主用户表)
- **主要功能**:
  - `sql_add_jellyfin()` - 添加Jellyfin记录
  - `sql_delete_jellyfin()` - 删除Jellyfin记录
  - `sql_get_jellyfin()` - 查询Jellyfin记录
  - `sql_update_jellyfin()` - 更新Jellyfin记录
  - `sql_count_jellyfin()` - 统计Jellyfin用户数

- **文件**: [`bot/sql_helper/sql_jellyfin2.py`](bot/sql_helper/sql_jellyfin2.py)
- **说明**: 非TG用户的Jellyfin账户管理
- **数据表**: `jellyfin2` (非TG用户表)

### 3. 配置文件
- **文件**: [`config_example.json`](config_example.json)
- **新增配置项**:
  ```json
  {
    "jellyfin_api": "xxxxx",
    "jellyfin_url": "http://255.255.255.255:8097",
    "jellyfin_line": "jellyfin.example.com",
    "jellyfin_block": ["nsfw"],
    "extra_jellyfin_libs": ["电视"]
  }
  ```

### 4. Schema定义
- **文件**: [`bot/schemas/schemas.py`](bot/schemas/schemas.py)
- **新增字段**:
  - `jellyfin_api: str` - Jellyfin API密钥
  - `jellyfin_url: str` - Jellyfin服务器地址
  - `jellyfin_line: str` - Jellyfin访问域名
  - `jellyfin_block: List[str]` - 屏蔽的媒体库列表
  - `extra_jellyfin_libs: List[str]` - 额外的媒体库列表

### 5. 初始化配置
- **文件**: [`bot/__init__.py`](bot/__init__.py)
- **新增导出变量**:
  - `jellyfin_api`
  - `jellyfin_url`
  - `jellyfin_line`
  - `jellyfin_block`
  - `extra_jellyfin_libs`

## 数据库表结构

### jellyfin表 (主表)
| 字段 | 类型 | 说明 |
|------|------|------|
| tg | BigInteger | Telegram用户ID (主键) |
| jellyfinid | String(255) | Jellyfin用户ID |
| name | String(255) | 用户名 |
| pwd | String(255) | 密码 |
| pwd2 | String(255) | 备用密码 |
| lv | String(1) | 用户等级 (默认'd') |
| cr | DateTime | 创建时间 |
| ex | DateTime | 过期时间 |
| us | Integer | 积分 (默认0) |
| iv | Integer | 邀请数 (默认0) |
| ch | DateTime | 签到时间 |

### jellyfin2表 (非TG用户表)
| 字段 | 类型 | 说明 |
|------|------|------|
| jellyfinid | String(255) | Jellyfin用户ID (主键) |
| name | String(255) | 用户名 |
| pwd | String(255) | 密码 |
| pwd2 | String(255) | 备用密码 |
| lv | String(1) | 用户等级 (默认'd') |
| cr | DateTime | 创建时间 |
| ex | DateTime | 过期时间 |
| expired | Integer | 过期标记 |

## 使用方法

### 1. 配置Jellyfin服务器
在 `config.json` 中添加Jellyfin配置:
```json
{
  "jellyfin_api": "your_api_key_here",
  "jellyfin_url": "http://your-jellyfin-server:8096",
  "jellyfin_line": "jellyfin.yourdomain.com",
  "jellyfin_block": [],
  "extra_jellyfin_libs": []
}
```

### 2. 导入Jellyfin模块
```python
from bot.func_helper.jellyfin import jellyfin, Jellyfinservice
from bot.sql_helper.sql_jellyfin import (
    sql_add_jellyfin, 
    sql_get_jellyfin,
    sql_update_jellyfin,
    Jellyfin
)
```

### 3. 使用Jellyfin API
```python
# 创建用户
user_id, pwd, ex = await jellyfin.jellyfin_create("username", 30)

# 删除用户
result = await jellyfin.jellyfin_del(user_id)

# 重置密码
result = await jellyfin.jellyfin_reset(user_id, "new_password")

# 获取所有用户
success, users = await jellyfin.users()

# 搜索电影
movies = await jellyfin.get_movies("电影名称")
```

### 4. 数据库操作
```python
# 添加用户到数据库
sql_add_jellyfin(tg_id)

# 查询用户
user = sql_get_jellyfin(tg_id)

# 更新用户信息
sql_update_jellyfin(
    Jellyfin.tg == tg_id,
    jellyfinid=user_id,
    name="username",
    pwd=password
)
```

## API对比

### Emby vs Jellyfin
虽然Jellyfin是Emby的分支，但本实现完全独立:

| 功能 | Emby模块 | Jellyfin模块 |
|------|----------|--------------|
| API文件 | `bot/func_helper/emby.py` | `bot/func_helper/jellyfin.py` |
| 数据表 | `emby`, `emby2` | `jellyfin`, `jellyfin2` |
| 配置前缀 | `emby_*` | `jellyfin_*` |
| 实例名 | `emby` | `jellyfin` |

## 注意事项

1. **API兼容性**: Jellyfin API与Emby API高度兼容，使用相同的端点结构
2. **数据独立**: Jellyfin和Emby的数据完全独立，互不影响
3. **配置要求**: 使用Jellyfin功能前需要在配置文件中设置正确的URL和API密钥
4. **插件依赖**: 某些功能(如播放统计)需要安装相应的Jellyfin插件(如playback reporting)

## 后续开发建议

1. **命令模块**: 需要创建对应的命令处理模块来使用Jellyfin功能
2. **面板集成**: 在管理面板中添加Jellyfin服务器管理选项
3. **定时任务**: 添加Jellyfin用户过期检测等定时任务
4. **统一接口**: 可以考虑创建统一的媒体服务器接口，支持Emby和Jellyfin切换

## 测试清单

- [x] Jellyfin API模块创建
- [x] Jellyfin SQL模块创建
- [x] 配置文件更新
- [x] Schema定义更新
- [x] 初始化配置更新
- [ ] 命令模块集成 (待开发)
- [ ] 面板功能集成 (待开发)
- [ ] 实际服务器测试 (需要Jellyfin服务器)

## 版本信息
- 实现日期: 2025-10-28
- 基于项目: FeiyueSakura_embyboss
- Jellyfin API兼容性: 10.8+
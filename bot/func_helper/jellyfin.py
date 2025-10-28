#! /usr/bin/python3
# -*- coding:utf-8 -*-
"""
jellyfin的api操作方法
与emby的api保持独立，避免混淆
"""
from datetime import datetime, timedelta, timezone

import requests as r
from bot import LOGGER
from bot.sql_helper.sql_jellyfin import sql_update_jellyfin, Jellyfin
from bot.sql_helper.sql_jellyfin2 import sql_delete_jellyfin2
from bot.func_helper.utils import pwd_create, convert_runtime, cache


def create_policy(admin=False, disable=False, limit: int = 2, block: list = None):
    """
    创建Jellyfin用户策略
    :param admin: bool 是否开启管理员
    :param disable: bool 是否禁用
    :param limit: int 同时播放流的默认值
    :param block: list 默认将 播放列表 屏蔽
    :return: policy 用户策略
    """
    if block is None:
        from bot import extra_jellyfin_libs
        block = ['播放列表'] + extra_jellyfin_libs
    
    policy = {
        "IsAdministrator": admin,
        "IsHidden": True,
        "IsHiddenRemotely": True,
        "IsDisabled": disable,
        "EnableRemoteControlOfOtherUsers": False,
        "EnableSharedDeviceControl": False,
        "EnableRemoteAccess": True,
        "EnableLiveTvManagement": False,
        "EnableLiveTvAccess": True,
        "EnableMediaPlayback": True,
        "EnableAudioPlaybackTranscoding": False,
        "EnableVideoPlaybackTranscoding": False,
        "EnablePlaybackRemuxing": False,
        "EnableContentDeletion": False,
        "EnableContentDownloading": False,
        "EnableSubtitleDownloading": False,
        "EnableSubtitleManagement": False,
        "EnableSyncTranscoding": False,
        "EnableMediaConversion": False,
        "EnableAllDevices": True,
        "SimultaneousStreamLimit": limit,
        "BlockedMediaFolders": block,
        "EnablePublicSharing": False
    }
    return policy


def pwd_policy(jellyfinid, stats=False, new=None):
    """
    Jellyfin密码策略
    :param jellyfinid: str 修改的jellyfin_id
    :param stats: bool 是否重置密码
    :param new: str 新密码
    :return: policy 密码策略
    """
    if new is None:
        policy = {
            "Id": f"{jellyfinid}",
            "ResetPassword": stats,
        }
    else:
        policy = {
            "Id": f"{jellyfinid}",
            "NewPw": f"{new}",
        }
    return policy


class Jellyfinservice:
    """
    Jellyfin API服务类
    与Emby API完全独立
    """

    def __init__(self, url, api_key):
        """
        初始化Jellyfin服务
        :param url: Jellyfin服务器地址
        :param api_key: Jellyfin API密钥
        """
        self.url = url
        self.api_key = api_key
        self.headers = {
            'accept': 'application/json',
            'content-type': 'application/json',
            'X-Emby-Token': self.api_key,  # Jellyfin兼容Emby的token头
            'X-Emby-Client': 'Sakura BOT Jellyfin',
            'X-Emby-Device-Name': 'Sakura BOT Jellyfin',
            'X-Emby-Client-Version': '1.0.0',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36 Edg/114.0.1823.82'
        }

    async def jellyfin_create(self, name, us: int):
        """
        创建Jellyfin账户
        :param name: jellyfin用户名
        :param us: 天数
        :return: bool or tuple
        """
        ex = (datetime.now() + timedelta(days=us))
        name_data = ({"Name": name})
        new_user = r.post(f'{self.url}/Users/New',
                          headers=self.headers,
                          json=name_data)
        if new_user.status_code == 200 or new_user.status_code == 204:
            try:
                user_id = new_user.json()["Id"]
                pwd = await pwd_create(8)
                pwd_data = pwd_policy(user_id, new=pwd)
                _pwd = r.post(f'{self.url}/Users/{user_id}/Password',
                              headers=self.headers,
                              json=pwd_data)
            except:
                return False
            else:
                policy = create_policy(False, False)
                _policy = r.post(f'{self.url}/Users/{user_id}/Policy',
                                 headers=self.headers,
                                 json=policy)
                return user_id, pwd, ex if _policy.status_code == 200 or _policy.status_code == 204 else False
        else:
            return False

    async def jellyfin_del(self, user_id, stats=None):
        """
        删除Jellyfin账户
        :param user_id: jellyfin用户ID
        :param stats: 删除状态
        :return: bool
        """
        res = r.delete(f'{self.url}/Users/{user_id}', headers=self.headers)
        if res.status_code == 200 or res.status_code == 204:
            if stats is None:
                if sql_update_jellyfin(Jellyfin.jellyfinid == user_id, jellyfinid=None, name=None, pwd=None, 
                                      pwd2=None, lv='d', cr=None, ex=None):
                    return True
                else:
                    return False
            else:
                if sql_delete_jellyfin2(jellyfinid=user_id):
                    return True
                else:
                    return False
        else:
            return False

    async def jellyfin_reset(self, user_id, new=None):
        """
        重置Jellyfin密码
        :param user_id: jellyfin用户ID
        :param new: 新密码
        :return: bool
        """
        pwd = pwd_policy(jellyfinid=user_id, stats=True, new=None)
        _pwd = r.post(f'{self.url}/Users/{user_id}/Password',
                      headers=self.headers,
                      json=pwd)
        if _pwd.status_code == 200 or _pwd.status_code == 204:
            if new is None:
                if sql_update_jellyfin(Jellyfin.jellyfinid == user_id, pwd=None) is True:
                    return True
                return False
            else:
                pwd2 = pwd_policy(user_id, new=new)
                new_pwd = r.post(f'{self.url}/Users/{user_id}/Password',
                                 headers=self.headers,
                                 json=pwd2)
                if new_pwd.status_code == 200 or new_pwd.status_code == 204:
                    if sql_update_jellyfin(Jellyfin.jellyfinid == user_id, pwd=new) is True:
                        return True
                    return False
        else:
            return False

    async def jellyfin_block(self, user_id, stats=0, block=None):
        """
        Jellyfin显示、隐藏媒体库
        :param user_id: jellyfin用户ID
        :param stats: 策略状态
        :param block: 屏蔽列表
        :return: bool
        """
        if block is None:
            from bot import jellyfin_block as jf_block
            block = jf_block
            
        if stats == 0:
            policy = create_policy(False, False, block=block)
        else:
            policy = create_policy(False, False)
        _policy = r.post(f'{self.url}/Users/{user_id}/Policy',
                         headers=self.headers,
                         json=policy)
        if _policy.status_code == 200 or _policy.status_code == 204:
            return True
        return False

    async def get_jellyfin_libs(self):
        """
        获取所有Jellyfin媒体库
        :return: list
        """
        response = r.get(f"{self.url}/Library/VirtualFolders?api_key={self.api_key}", headers=self.headers)
        if response.status_code == 200:
            tmp = []
            for lib in response.json():
                tmp.append(lib['Name'])
            return tmp
        else:
            return None

    @cache.memoize(ttl=120)
    def get_current_playing_count(self) -> int:
        """
        获取Jellyfin当前播放数量
        :return: int
        """
        response = r.get(f"{self.url}/Sessions", headers=self.headers)
        sessions = response.json()
        count = 0
        for session in sessions:
            try:
                if session["NowPlayingItem"]:
                    count += 1
            except KeyError:
                pass
        return count

    async def jellyfin_change_policy(self, user_id, admin=False, method=False):
        """
        修改Jellyfin用户策略
        :param user_id: 用户ID
        :param admin: 是否管理员
        :param method: 是否禁用
        :return: bool
        """
        policy = create_policy(admin=admin, disable=method)
        _policy = r.post(self.url + f'/Users/{user_id}/Policy',
                         headers=self.headers,
                         json=policy)
        if _policy.status_code == 200 or _policy.status_code == 204:
            return True
        return False

    async def authority_account(self, tg, username, password=None):
        """
        验证Jellyfin账户
        """
        data = {"Username": username, "Pw": password, }
        if password == 'None':
            data = {"Username": username}
        res = r.post(self.url + '/Users/AuthenticateByName', headers=self.headers, json=data)
        if res.status_code == 200:
            jellyfinid = res.json()["User"]["Id"]
            return True, jellyfinid
        return False, 0

    async def jellyfin_cust_commit(self, user_id=None, days=7, method=None):
        """
        Jellyfin自定义查询 - 需要playback reporting插件
        """
        _url = f'{self.url}/user_usage_stats/submit_custom_query'
        sub_time = datetime.now(timezone(timedelta(hours=8)))
        start_time = (sub_time - timedelta(days=days)).strftime("%Y-%m-%d %H:%M:%S")
        end_time = sub_time.strftime("%Y-%m-%d %H:%M:%S")
        sql = ''
        if method == 'sp':
            sql += "SELECT UserId, SUM(PlayDuration - PauseDuration) AS WatchTime FROM PlaybackActivity "
            sql += f"WHERE DateCreated >= '{start_time}' AND DateCreated < '{end_time}' GROUP BY UserId ORDER BY WatchTime DESC"
        elif user_id != 'None':
            sql += "SELECT MAX(DateCreated) AS LastLogin,SUM(PlayDuration - PauseDuration) / 60 AS WatchTime FROM PlaybackActivity "
            sql += f"WHERE UserId = '{user_id}' AND DateCreated >= '{start_time}' AND DateCreated < '{end_time}' GROUP BY UserId"
        data = {"CustomQueryString": sql, "ReplaceUserId": True}
        resp = r.post(_url, headers=self.headers, json=data, timeout=30)
        if resp.status_code == 200:
            rst = resp.json()["results"]
            return rst
        else:
            return None

    async def users(self):
        """
        获取Jellyfin所有用户
        """
        try:
            _url = f"{self.url}/Users"
            resp = r.get(_url, headers=self.headers)
            if resp.status_code != 204 and resp.status_code != 200:
                return False, {'error': "🤕Jellyfin 服务器连接失败!"}
            return True, resp.json()
        except Exception as e:
            return False, {'error': e}

    def user(self, jellyfinid):
        """
        通过ID查看Jellyfin账户配置信息
        :param jellyfinid: 用户ID
        :return: tuple
        """
        try:
            _url = f"{self.url}/Users/{jellyfinid}"
            resp = r.get(_url, headers=self.headers)
            if resp.status_code != 204 and resp.status_code != 200:
                return False, {'error': "🤕Jellyfin 服务器连接失败!"}
            return True, resp.json()
        except Exception as e:
            return False, {'error': e}

    async def add_favotire_items(self, user_id, item_id):
        """添加收藏"""
        try:
            _url = f"{self.url}/Users/{user_id}/FavoriteItems/{item_id}"
            resp = r.post(_url, headers=self.headers)
            if resp.status_code != 204 and resp.status_code != 200:
                return False
            return True
        except Exception as e:
            LOGGER.error(f'Jellyfin添加收藏失败 {e}')
            return False

    async def item_id_namme(self, user_id, item_id):
        """获取项目名称"""
        try:
            req = f"{self.url}/Users/{user_id}/Items/{item_id}"
            reqs = r.get(req, headers=self.headers, timeout=3)
            if reqs.status_code != 204 and reqs.status_code != 200:
                return ''
            title = reqs.json().get("Name")
            return title
        except Exception as e:
            LOGGER.error(f'Jellyfin获取title失败 {e}')
            return ''

    async def primary(self, item_id, width=200, height=300, quality=90):
        """获取主图"""
        try:
            _url = f"{self.url}/Items/{item_id}/Images/Primary?maxHeight={height}&maxWidth={width}&quality={quality}"
            resp = r.get(_url, headers=self.headers)
            if resp.status_code != 204 and resp.status_code != 200:
                return False, {'error': "🤕Jellyfin 服务器连接失败!"}
            return True, resp.content
        except Exception as e:
            return False, {'error': e}

    async def backdrop(self, item_id, width=300, quality=90):
        """获取背景图"""
        try:
            _url = f"{self.url}/Items/{item_id}/Images/Backdrop?maxWidth={width}&quality={quality}"
            resp = r.get(_url, headers=self.headers)
            if resp.status_code != 204 and resp.status_code != 200:
                return False, {'error': "🤕Jellyfin 服务器连接失败!"}
            return True, resp.content
        except Exception as e:
            return False, {'error': e}

    async def items(self, user_id, item_id):
        """获取项目信息"""
        try:
            _url = f"{self.url}/Users/{user_id}/Items/{item_id}"
            resp = r.get(_url, headers=self.headers)
            if resp.status_code != 204 and resp.status_code != 200:
                return False, {'error': "🤕Jellyfin 服务器连接失败!"}
            return True, resp.json()
        except Exception as e:
            return False, {'error': e}

    async def get_jellyfin_report(self, types='Movie', user_id=None, days=7, end_date=None, limit=10):
        """
        获取Jellyfin报告数据
        """
        try:
            if not end_date:
                end_date = datetime.now(timezone(timedelta(hours=8)))
            start_time = (end_date - timedelta(days=days)).strftime("%Y-%m-%d %H:%M:%S")
            end_time = end_date.strftime('%Y-%m-%d %H:%M:%S')
            sql = "SELECT UserId, ItemId, ItemType, "
            if types == 'Episode':
                sql += " substr(ItemName,0, instr(ItemName, ' - ')) AS name, "
            else:
                sql += "ItemName AS name, "
            sql += "COUNT(1) AS play_count, "
            sql += "SUM(PlayDuration - PauseDuration) AS total_duarion "
            sql += "FROM PlaybackActivity "
            sql += f"WHERE ItemType = '{types}' "
            sql += f"AND DateCreated >= '{start_time}' AND DateCreated <= '{end_time}' "
            sql += "AND UserId not IN (select UserId from UserList) "
            if user_id:
                sql += f"AND UserId = '{user_id}' "
            sql += "GROUP BY name "
            sql += "ORDER BY total_duarion DESC "
            sql += "LIMIT " + str(limit)
            _url = f'{self.url}/user_usage_stats/submit_custom_query'
            data = {
                "CustomQueryString": sql,
                "ReplaceUserId": False
            }
            resp = r.post(_url, headers=self.headers, json=data)
            if resp.status_code != 204 and resp.status_code != 200:
                return False, {'error': "🤕Jellyfin 服务器连接失败!"}
            ret = resp.json()
            if len(ret["colums"]) == 0:
                return False, ret["message"]
            return True, ret["results"]
        except Exception as e:
            return False, {'error': e}

    async def get_jellyfin_userip(self, user_id):
        """
        获取指定用户播放过的不同IP和设备
        """
        sql = f"SELECT DISTINCT RemoteAddress,DeviceName FROM PlaybackActivity " \
              f"WHERE RemoteAddress NOT IN ('127.0.0.1', '172.17.0.1') and UserId = '{user_id}'"
        data = {
            "CustomQueryString": sql,
            "ReplaceUserId": True
        }
        _url = f'{self.url}/user_usage_stats/submit_custom_query?api_key={self.api_key}'
        resp = r.post(_url, json=data)
        if resp.status_code != 204 and resp.status_code != 200:
            return False, {'error': "🤕Jellyfin 服务器连接失败!"}
        ret = resp.json()
        if len(ret["colums"]) == 0:
            return False, ret["message"]
        return True, ret["results"]

    def get_medias_count(self):
        """
        获得电影、电视剧、音乐媒体数量
        :return: str 媒体统计文本
        """
        req_url = f"{self.url}/Items/Counts?api_key={self.api_key}"
        try:
            res = r.get(url=req_url)
            if res:
                result = res.json()
                movie_count = result.get("MovieCount") or 0
                tv_count = result.get("SeriesCount") or 0
                episode_count = result.get("EpisodeCount") or 0
                music_count = result.get("SongCount") or 0
                txt = f'🎬 电影数量：{movie_count}\n' \
                      f'📽️ 剧集数量：{tv_count}\n' \
                      f'🎵 音乐数量：{music_count}\n' \
                      f'🎞️ 总集数：{episode_count}\n'
                return txt
            else:
                LOGGER.error(f"Jellyfin Items/Counts 未获取到返回数据")
                return None
        except Exception as e:
            LOGGER.error(f"连接Jellyfin Items/Counts出错：" + str(e))
            return e

    async def get_movies(self, title: str, start: int = 0, limit: int = 5):
        """
        根据标题搜索Jellyfin中的电影/剧集
        :param limit: 限制条目
        :param title: 标题
        :param start: 从何处开始
        :return: 返回信息列表
        """
        if start != 0: start = start
        req_url = f"{self.url}/Items?IncludeItemTypes=Movie,Series&Fields=ProductionYear,Overview,OriginalTitle,Taglines,ProviderIds,Genres,RunTimeTicks,ProductionLocations,DateCreated,Studios" \
                  f"&StartIndex={start}&Recursive=true&SearchTerm={title}&Limit={limit}&IncludeSearchTypes=false"
        try:
            res = r.get(url=req_url, headers=self.headers, timeout=3)
            if res:
                res_items = res.json().get("Items")
                if res_items:
                    ret_movies = []
                    for res_item in res_items:
                        title = res_item.get("Name") if res_item.get("Name") == res_item.get(
                            "OriginalTitle") else f'{res_item.get("Name")} - {res_item.get("OriginalTitle")}'
                        od = ", ".join(res_item.get("ProductionLocations", ["普""遍"]))
                        ns = ", ".join(res_item.get("Genres", "未知"))
                        runtime = convert_runtime(res_item.get("RunTimeTicks")) if res_item.get(
                            "RunTimeTicks") else '数据缺失'
                        item_tmdbid = res_item.get("ProviderIds", {}).get("Tmdb", None)
                        mediaserver_item = dict(item_type=res_item.get("Type"), item_id=res_item.get("Id"), title=title,
                                                year=res_item.get("ProductionYear", '缺失'),
                                                od=od, genres=ns,
                                                photo=f'{self.url}/Items/{res_item.get("Id")}/Images/Primary?maxHeight=400&maxWidth=600&quality=90',
                                                runtime=runtime,
                                                overview=res_item.get("Overview", "暂无更多信息"),
                                                taglines='简介：' if not res_item.get("Taglines") else
                                                res_item.get("Taglines")[0],
                                                tmdbid=item_tmdbid,
                                                add=res_item.get("DateCreated", "None.").split('.')[0],
                                                )
                        ret_movies.append(mediaserver_item)
                    return ret_movies
        except Exception as e:
            LOGGER.error(f"连接Jellyfin Items出错：" + str(e))
            return []

# 实例化Jellyfin服务 - 在导入时自动创建
# 注意：需要在bot/__init__.py中导入jellyfin相关配置后才能使用
try:
    from bot import jellyfin_url, jellyfin_api
    if jellyfin_url and jellyfin_api:
        jellyfin = Jellyfinservice(jellyfin_url, jellyfin_api)
    else:
        jellyfin = None
        LOGGER.warning("Jellyfin配置未设置，Jellyfin功能将不可用")
except ImportError:
    jellyfin = None
    LOGGER.warning("无法导入Jellyfin配置")
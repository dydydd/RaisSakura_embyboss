"""
服务器讯息打印
支持Emby和Jellyfin
"""
from datetime import datetime, timezone, timedelta
from pyrogram import filters
from bot import bot, emby_line, jellyfin_line, jellyfin_url
from bot.func_helper.emby import emby
from bot.func_helper.jellyfin import jellyfin
from bot.func_helper.filters import user_in_group_on_filter
from bot.sql_helper.sql_emby import sql_get_emby
from bot.sql_helper.sql_jellyfin import sql_get_jellyfin
from bot.func_helper.fix_bottons import cr_page_server
from bot.func_helper.msg_utils import callAnswer, editMessage


@bot.on_callback_query(filters.regex('server') & user_in_group_on_filter)
async def server(_, call):
    # 先检查Emby数据
    emby_data = sql_get_emby(tg=call.from_user.id)
    jellyfin_data = sql_get_jellyfin(tg=call.from_user.id)
    
    if not emby_data and not jellyfin_data:
        return await editMessage(call, '⚠️ 数据库没有你，请重新 /start录入')
    
    await callAnswer(call, '🌐查询中...')
    try:
        j = int(call.data.split(':')[1])
    except IndexError:
        # 第一次查看
        send = await editMessage(call, "**▎🌐查询中...\n\nο(=•ω＜=)ρ⌒☆ 发送bibo电波~bibo~ \n⚡ 点击按钮查看相应服务器状态**")
        if send is False:
            return

        keyboard, sever = await cr_page_server()
        server_info = sever[0]['server'] if sever == '' else ''
    else:
        keyboard, sever = await cr_page_server()
        server_info = ''.join([item['server'] for item in sever if item['id'] == j])

    # 构建服务器信息文本
    text_parts = []
    
    # Emby信息
    if emby_data:
        pwd = '空' if not emby_data.pwd else emby_data.pwd
        line = f'{emby_line}' if emby_data.lv in ['a', 'b'] else ' - **无权查看**'
        try:
            online = emby.get_current_playing_count()
        except:
            online = 'Emby服务器断连 ·0'
        text_parts.append(f'**▎📺 Emby服务器**\n'
                         f'**· 线路：**{line}\n'
                         f'**· 密码：**`{pwd}`\n'
                         f'· 🎬 在线 | **{online}** 人')
    
    # Jellyfin信息
    if jellyfin_data and jellyfin_url:
        jf_pwd = '空' if not jellyfin_data.pwd else jellyfin_data.pwd
        jf_line = f'{jellyfin_line}' if jellyfin_data.lv in ['a', 'b'] else ' - **无权查看**'
        try:
            jf_online = jellyfin.get_current_playing_count()
        except:
            jf_online = 'Jellyfin服务器断连 ·0'
        text_parts.append(f'**▎🎞️ Jellyfin服务器**\n'
                         f'**· 线路：**{jf_line}\n'
                         f'**· 密码：**`{jf_pwd}`\n'
                         f'· 🎬 在线 | **{jf_online}** 人')
    
    # 组合文本
    text = '\n\n'.join(text_parts)
    text += f'\n\n{server_info}' if server_info else '\n\n'
    text += f'**· 🌏 [{(datetime.now(timezone(timedelta(hours=8)))).strftime("%Y-%m-%d %H:%M:%S")}]**'
    
    await editMessage(call, text, buttons=keyboard)

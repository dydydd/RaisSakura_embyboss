from pyrogram import filters
from bot import bot
from bot.func_helper.filters import admins_on_filter
from bot.func_helper.msg_utils import editMessage
from bot.func_helper.fix_bottons import whitelist_page_ikb, normaluser_page_ikb
from bot.sql_helper.sql_emby import get_all_emby, Emby
from bot.func_helper.msg_utils import callAnswer
import math


@bot.on_callback_query(filters.regex('^whitelist$') & admins_on_filter)
async def list_whitelist(_, call):
    await callAnswer(call, '🔍 白名单用户列表')
    page = 1
    whitelist_users = get_all_emby(Emby.lv == 'a')
    total_users = len(whitelist_users)
    total_pages = math.ceil(total_users / 20)

    text = await create_whitelist_text(whitelist_users, page)
    keyboard = await whitelist_page_ikb(total_pages, page)

    await editMessage(call, text, buttons=keyboard)
@bot.on_callback_query(filters.regex('^normaluser$') & admins_on_filter)
async def list_normaluser(_, call):
    await callAnswer(call, '🔍 普通用户列表')
    page = 1
    normal_users = get_all_emby(Emby.lv == 'b')
    total_users = len(normal_users)
    total_pages = math.ceil(total_users / 20)

    text = await create_normaluser_text(normal_users, page)
    keyboard = await normaluser_page_ikb(total_pages, page)
    await editMessage(call, text, buttons=keyboard)


@bot.on_callback_query(filters.regex('^whitelist:') & admins_on_filter)
async def whitelist_page(_, call):
    page = int(call.data.split(':')[1])
    await callAnswer(call, f'🔍 打开第{page}页')
    whitelist_users = get_all_emby(Emby.lv == 'a')
    total_users = len(whitelist_users)
    total_pages = math.ceil(total_users / 20)

    text = await create_whitelist_text(whitelist_users, page)
    keyboard = await whitelist_page_ikb(total_pages, page)

    await editMessage(call, text, buttons=keyboard)

@bot.on_callback_query(filters.regex('^normaluser:') & admins_on_filter)
async def normaluser_page(_, call):
    page = int(call.data.split(':')[1])
    await callAnswer(call, f'🔍 打开第{page}页')
    normal_users = get_all_emby(Emby.lv == 'b')
    total_users = len(normal_users)
    total_pages = math.ceil(total_users / 20)

    text = await create_normaluser_text(normal_users, page)
    keyboard = await normaluser_page_ikb(total_pages, page)

    await editMessage(call, text, buttons=keyboard)

async def create_whitelist_text(users, page):
    start = (page - 1) * 20
    end = start + 20
    text = "**白名单用户列表**\n\n"
    for user in users[start:end]:
        
        text += f"TGID: `{user.tg}` | Emby用户名: `{user.name}` | 到期时间: 永久\n"
    text += f"第 {page} 页,共 {math.ceil(len(users) / 20)} 页, 共 {len(users)} 人"
    return text

async def create_normaluser_text(users, page):
    start = (page - 1) * 20
    end = start + 20
    text = "**普通用户列表**\n\n"
    for user in users[start:end]:
        text += f"TGID: `{user.tg}` | Emby用户名: `{user.name}` | 到期时间: `{user.ex.strftime('%Y-%m-%d')}`\n"
    text += f"第 {page} 页,共 {math.ceil(len(users) / 20)} 页, 共 {len(users)} 人"
    return text

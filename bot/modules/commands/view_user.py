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
    total_pages = math.ceil(total_users / 10)

    text = await create_whitelist_text(whitelist_users, page)
    keyboard = await whitelist_page_ikb(total_pages, page)

    await editMessage(call, text, buttons=keyboard)
@bot.on_callback_query(filters.regex('^normaluser$') & admins_on_filter)
async def list_normaluser(_, call):
    await callAnswer(call, '🔍 普通用户列表')
    page = 1
    normal_users = get_all_emby(Emby.lv == 'b')
    total_users = len(normal_users)
    total_pages = math.ceil(total_users / 10)

    text = await create_normaluser_text(normal_users, page)
    keyboard = await normaluser_page_ikb(total_pages, page)
    await editMessage(call, text, buttons=keyboard)


@bot.on_callback_query(filters.regex('^whitelist:') & admins_on_filter)
async def whitelist_page(_, call):
    page = int(call.data.split(':')[1])
    await callAnswer(call, f'🔍 打开第{page}页')
    whitelist_users = get_all_emby(Emby.lv == 'a')
    total_users = len(whitelist_users)
    total_pages = math.ceil(total_users / 10)

    text = await create_whitelist_text(whitelist_users, page)
    keyboard = await whitelist_page_ikb(total_pages, page)

    await editMessage(call, text, buttons=keyboard)

@bot.on_callback_query(filters.regex('^normaluser:') & admins_on_filter)
async def normaluser_page(_, call):
    page = int(call.data.split(':')[1])
    await callAnswer(call, f'🔍 打开第{page}页')
    normal_users = get_all_emby(Emby.lv == 'b')
    total_users = len(normal_users)
    total_pages = math.ceil(total_users / 10)

    text = await create_normaluser_text(normal_users, page)
    keyboard = await normaluser_page_ikb(total_pages, page)

    await editMessage(call, text, buttons=keyboard)

async def create_whitelist_text(users, page):
    start = (page - 1) * 10
    end = start + 10
    text = "**白名单用户列表**\n\n"
    for user in users[start:end]:
        expire_date = "永久" if user.iv == 'a' else user.ex.strftime("%m-%d %H:%M") if user.ex else "未设置"
        text += f"`{user.tg}` | `{user.name}` | `{expire_date}`\n"
    text += f"\n第 {page} 页,共 {math.ceil(len(users) / 10)} 页, 共 {len(users)} 人"
    return text

async def create_normaluser_text(users, page):
    start = (page - 1) * 10
    end = start + 10
    text = "**普通用户列表**\n\n"
    for user in users[start:end]:
        expire_date = "永久" if user.iv == 'b' else user.ex.strftime("%m-%d %H:%M") if user.ex else "未设置"
        text += f"`{user.tg}` | `{user.name}` | `{expire_date}`\n"
    text += f"\n第 {page} 页,共 {math.ceil(len(users) / 10)} 页, 共 {len(users)} 人"
    return text

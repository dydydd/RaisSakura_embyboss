import time

from pyrogram import filters

from bot import bot, owner, prefixes, extra_jellyfin_libs, LOGGER, Now
from bot.func_helper.msg_utils import sendMessage, deleteMessage
from bot.sql_helper.sql_jellyfin import get_all_jellyfin, Jellyfin
from bot.func_helper.jellyfin import jellyfin

# jellyfinlibs_block
@bot.on_message(filters.command('jellyfinlibs_blockall', prefixes) & filters.user(owner))
async def jellyfinlibs_blockall(_, msg):
    await deleteMessage(msg)
    reply = await msg.reply(f"🍓 正在处理ing····, 正在更新所有用户的Jellyfin媒体库访问权限")
    rst = get_all_jellyfin(Jellyfin.jellyfinid is not None)
    if rst is None:
        LOGGER.info(
            f"【关闭Jellyfin媒体库任务】 -{msg.from_user.first_name}({msg.from_user.id}) 没有检测到任何jellyfin账户，结束")
        return await reply.edit("⚡【关闭Jellyfin媒体库任务】\n\n结束，没有一个有号的")
    allcount = 0
    successcount = 0
    start = time.perf_counter()
    text = ''
    all_libs = await jellyfin.get_jellyfin_libs()
    for i in rst:
        success, rep = jellyfin.user(jellyfinid=i.jellyfinid)
        if success:
            allcount += 1
            currentblock = ['播放列表'] + all_libs
            # 去除相同的元素
            currentblock = list(set(currentblock))
            re = await jellyfin.jellyfin_block(i.jellyfinid, 0, block=currentblock)
            if re is True:
                successcount += 1
                text += f'已关闭了 [{i.name}](tg://user?id={i.tg}) 的Jellyfin媒体库权限\n'
            else:
                text += f'🌧️ 关闭失败 [{i.name}](tg://user?id={i.tg}) 的Jellyfin媒体库权限\n'
    # 防止触发 MESSAGE_TOO_LONG 异常
    n = 1000
    chunks = [text[i:i + n] for i in range(0, len(text), n)]
    for c in chunks:
        await msg.reply(c + f'\n**{Now.strftime("%Y-%m-%d %H:%M:%S")}**')
    end = time.perf_counter()
    times = end - start
    if allcount != 0:
        await sendMessage(msg,
                          text=f"⚡#关闭Jellyfin媒体库任务 done\n  共检索出 {allcount} 个账户，成功关闭 {successcount}个，耗时：{times:.3f}s")
    else:
        await sendMessage(msg, text=f"**#关闭Jellyfin媒体库任务 结束！搞毛，没有人被干掉。**")
    LOGGER.info(
        f"【关闭Jellyfin媒体库任务结束】 - {msg.from_user.id} 共检索出 {allcount} 个账户，成功关闭 {successcount}个，耗时：{times:.3f}s")

# jellyfinlibs_unblock
@bot.on_message(filters.command('jellyfinlibs_unblockall', prefixes) & filters.user(owner))
async def jellyfinlibs_unblockall(_, msg):
    await deleteMessage(msg)
    reply = await msg.reply(f"🍓 正在处理ing····, 正在更新所有用户的Jellyfin媒体库访问权限")
    rst = get_all_jellyfin(Jellyfin.jellyfinid is not None)
    if rst is None:
        LOGGER.info(
            f"【开启Jellyfin媒体库任务】 -{msg.from_user.first_name}({msg.from_user.id}) 没有检测到任何jellyfin账户，结束")
        return await reply.edit("⚡【开启Jellyfin媒体库任务】\n\n结束，没有一个有号的")
    allcount = 0
    successcount = 0
    start = time.perf_counter()
    text = ''
    for i in rst:
        success, rep = jellyfin.user(jellyfinid=i.jellyfinid)
        if success:
            allcount += 1
            currentblock = ['播放列表']
            # 去除相同的元素
            re = await jellyfin.jellyfin_block(i.jellyfinid, 0, block=currentblock)
            if re is True:
                successcount += 1
                text += f'已开启了 [{i.name}](tg://user?id={i.tg}) 的Jellyfin媒体库权限\n'
            else:
                text += f'🌧️ 开启失败 [{i.name}](tg://user?id={i.tg}) 的Jellyfin媒体库权限\n'
    # 防止触发 MESSAGE_TOO_LONG 异常
    n = 1000
    chunks = [text[i:i + n] for i in range(0, len(text), n)]
    for c in chunks:
        await msg.reply(c + f'\n**{Now.strftime("%Y-%m-%d %H:%M:%S")}**')
    end = time.perf_counter()
    times = end - start
    if allcount != 0:
        await sendMessage(msg,
                          text=f"⚡#开启Jellyfin媒体库任务 done\n  共检索出 {allcount} 个账户，成功开启 {successcount}个，耗时：{times:.3f}s")
    else:
        await sendMessage(msg, text=f"**#开启Jellyfin媒体库任务 结束！搞毛，没有人被干掉。**")
    LOGGER.info(
        f"【开启Jellyfin媒体库任务结束】 - {msg.from_user.id} 共检索出 {allcount} 个账户，成功开启 {successcount}个，耗时：{times:.3f}s")

@bot.on_message(filters.command('extrajellyfinlibs_blockall', prefixes) & filters.user(owner))
async def extrajellyfinlibs_blockall(_, msg):
    await deleteMessage(msg)
    reply = await msg.reply(f"🍓 正在处理ing····, 正在更新所有用户的Jellyfin额外媒体库访问权限")

    rst = get_all_jellyfin(Jellyfin.jellyfinid is not None)
    if rst is None:
        LOGGER.info(
            f"【关闭Jellyfin额外媒体库任务】 -{msg.from_user.first_name}({msg.from_user.id}) 没有检测到任何jellyfin账户，结束")
        return await reply.edit("⚡【关闭Jellyfin额外媒体库任务】\n\n结束，没有一个有号的")

    allcount = 0
    successcount = 0
    start = time.perf_counter()
    text = ''
    for i in rst:
        success, rep = jellyfin.user(jellyfinid=i.jellyfinid)
        if success:
            allcount += 1
            try:
                currentblock = list(set(rep["Policy"]["BlockedMediaFolders"] + ['播放列表']))
            except KeyError:
                currentblock = ['播放列表'] + extra_jellyfin_libs
            if not set(extra_jellyfin_libs).issubset(set(currentblock)):
                # 去除相同的元素
                currentblock = list(set(currentblock + extra_jellyfin_libs))
                re = await jellyfin.jellyfin_block(i.jellyfinid, 0, block=currentblock)
                if re is True:
                    successcount += 1
                    text += f'已关闭了 [{i.name}](tg://user?id={i.tg}) 的Jellyfin额外媒体库权限\n'
                else:
                    text += f'🌧️ 关闭失败 [{i.name}](tg://user?id={i.tg}) 的Jellyfin额外媒体库权限\n'
            else:
                successcount += 1
                text += f'已关闭了 [{i.name}](tg://user?id={i.tg}) 的Jellyfin额外媒体库权限\n'
    # 防止触发 MESSAGE_TOO_LONG 异常
    n = 1000
    chunks = [text[i:i + n] for i in range(0, len(text), n)]
    for c in chunks:
        await msg.reply(c + f'\n**{Now.strftime("%Y-%m-%d %H:%M:%S")}**')
    end = time.perf_counter()
    times = end - start
    if allcount != 0:
        await sendMessage(msg,
                          text=f"⚡#关闭Jellyfin额外媒体库任务 done\n  共检索出 {allcount} 个账户，成功关闭 {successcount}个，耗时：{times:.3f}s")
    else:
        await sendMessage(msg, text=f"**#关闭Jellyfin额外媒体库任务 结束！搞毛，没有人被干掉。**")
    LOGGER.info(
        f"【关闭Jellyfin额外媒体库任务结束】 - {msg.from_user.id} 共检索出 {allcount} 个账户，成功关闭 {successcount}个，耗时：{times:.3f}s")


@bot.on_message(filters.command('extrajellyfinlibs_unblockall', prefixes) & filters.user(owner))
async def extrajellyfinlibs_unblockall(_, msg):
    await deleteMessage(msg)
    reply = await msg.reply(f"🍓 正在处理ing····, 正在更新所有用户的Jellyfin额外媒体库访问权限")

    rst = get_all_jellyfin(Jellyfin.jellyfinid is not None)
    if rst is None:
        LOGGER.info(
            f"【开启Jellyfin额外媒体库任务】 -{msg.from_user.first_name}({msg.from_user.id}) 没有检测到任何jellyfin账户，结束")
        return await reply.edit("⚡【开启Jellyfin额外媒体库任务】\n\n结束，没有一个有号的")

    allcount = 0
    successcount = 0
    start = time.perf_counter()
    text = ''
    for i in rst:
        success, rep = jellyfin.user(jellyfinid=i.jellyfinid)
        if success:
            allcount += 1
            try:
                currentblock = list(set(rep["Policy"]["BlockedMediaFolders"] + ['播放列表']))
                # 保留不同的元素
                currentblock = [x for x in currentblock if x not in extra_jellyfin_libs] + [x for x in extra_jellyfin_libs if
                                                                                        x not in currentblock]
            except KeyError:
                currentblock = ['播放列表']
            if not set(extra_jellyfin_libs).issubset(set(currentblock)):
                re = await jellyfin.jellyfin_block(i.jellyfinid, 0, block=currentblock)
                if re is True:
                    successcount += 1
                    text += f'已开启了 [{i.name}](tg://user?id={i.tg}) 的Jellyfin额外媒体库权限\n'
                else:
                    text += f'🌧️ 开启失败 [{i.name}](tg://user?id={i.tg}) 的Jellyfin额外媒体库权限\n'
            else:
                successcount += 1
                text += f'已开启了 [{i.name}](tg://user?id={i.tg}) 的Jellyfin额外媒体库权限\n'
    # 防止触发 MESSAGE_TOO_LONG 异常
    n = 1000
    chunks = [text[i:i + n] for i in range(0, len(text), n)]
    for c in chunks:
        await msg.reply(c + f'\n**{Now.strftime("%Y-%m-%d %H:%M:%S")}**')
    end = time.perf_counter()
    times = end - start
    if allcount != 0:
        await sendMessage(msg,
                          text=f"⚡#开启Jellyfin额外媒体库任务 done\n  共检索出 {allcount} 个账户，成功开启 {successcount}个，耗时：{times:.3f}s")
    else:
        await sendMessage(msg, text=f"**#开启Jellyfin额外媒体库任务 结束！搞毛，没有人被干掉。**")
    LOGGER.info(
        f"【开启Jellyfin额外媒体库任务结束】 - {msg.from_user.id} 共检索出 {allcount} 个账户，成功开启 {successcount}个，耗时：{times:.3f}s")
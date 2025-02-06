"""
兑换注册码exchange
"""
from datetime import timedelta, datetime

from bot import bot, _open, LOGGER, bot_photo
from bot.func_helper.emby import emby
from bot.func_helper.fix_bottons import register_code_ikb
from bot.func_helper.msg_utils import sendMessage, sendPhoto
from bot.sql_helper.sql_code import Code
from bot.sql_helper.sql_emby import sql_get_emby, Emby
from bot.sql_helper import Session


# def is_renew_code(input_string):
#     if "Renew" in input_string:
#         return True
#     else:
#         return False


async def rgs_code(_, msg, register_code):
    if _open.stat: return await sendMessage(msg, "🤧 自由注册开启下无法使用注册码。")

    data = sql_get_emby(tg=msg.from_user.id)
    if not data: return await sendMessage(msg, "出错了，不确定您是否有资格使用，请先 /start")
    embyid = data.embyid
    ex = data.ex
    lv = data.lv
    if embyid:
        # if not is_renew_code(register_code): return await sendMessage(msg,
        #                                                               "🔔 很遗憾，您使用的是注册码，无法启用续期功能，请悉知",
        #                                                               timer=60)
        with Session() as session:
            try:
                # 使用一次性查询和锁定
                r = session.query(Code).filter(Code.code == register_code).with_for_update().first()
                if not r:
                    return await sendMessage(msg, "⛔ **你输入了一个错误de续期码，请确认好重试。**", timer=60)
                    
                # 检查是否已使用
                if r.used:
                    return await sendMessage(msg, 
                        f'此 `{register_code}` \n续期码已被使用,是[{r.used}](tg://user?id={r.used})的形状了喔')
                
                # 更新使用状态
                r.used = msg.from_user.id
                r.usedtime = datetime.now()
                
                # 获取正确的基准时间
                base_time = max(datetime.now(), ex)
                ex_new = base_time + timedelta(days=r.us)
                
                # 更新用户到期时间
                emby_query = session.query(Emby).filter(Emby.tg == msg.from_user.id)
                if datetime.now() > ex:
                    await emby.emby_change_policy(id=embyid, method=False)
                    if lv == 'c':
                        emby_query.update({Emby.ex: ex_new, Emby.lv: 'b'})
                    else:
                        emby_query.update({Emby.ex: ex_new})
                else:
                    emby_query.update({Emby.ex: ex_new})
                
                # 提交事务
                session.commit()
                
                # ... 其余消息发送代码 ...
                first = await bot.get_chat(r.tg)
                msg_text = (
                    f'🎊 少年郎，恭喜你，已收到 [{first.first_name}](tg://user?id={r.tg}) 的{r.us}天🎁\n'
                    f'到期时间：{ex_new}'
                )
                await sendMessage(msg, msg_text)
                new_code = register_code[:-7] + "░" * 7
                await sendMessage(msg, 
                                  f'· 🎟️ 续期码使用 - [{msg.from_user.first_name}](tg://user?id={msg.chat.id}) [{msg.from_user.id}] 使用了 {new_code}\n· 📅 实时到期 - {ex_new}',
                                  send=True)
                LOGGER.info(f"【续期码】：{msg.from_user.first_name}[{msg.chat.id}] 使用了 {register_code}，到期时间：{ex_new}")
                
            except Exception as e:
                session.rollback()
                LOGGER.error(f"续期码使用失败: {str(e)}")
                return await sendMessage(msg, "续期操作失败，请重试或联系管理员")

    else:
        # if is_renew_code(register_code): return await sendMessage(msg,
        #                                                           "🔔 很遗憾，您使用的是续期码，无法启用注册功能，请悉知",
        #                                                           timer=60)
        if data.us > 0: return await sendMessage(msg, "已有注册资格，请先使用【注册】，勿重复其他注册码。")
        with Session() as session:
            # 我勒个豆，终于用 原子操作 + 排他锁 成功防止了并发更新
            # 在 UPDATE 语句中添加一个条件，只有当注册码未被使用时，才更新数据。这样，如果有两个用户同时尝试使用同一条注册码，只有一个用户的 UPDATE 语句会成功，因为另一个用户的 UPDATE 语句会发现注册码已经被使用。
            r = session.query(Code).filter(Code.code == register_code).with_for_update().first()
            if not r: return await sendMessage(msg, "⛔ **你输入了一个错误de注册码，请确认好重试。**")
            re = session.query(Code).filter(Code.code == register_code, Code.used.is_(None)).with_for_update().update(
                {Code.used: msg.from_user.id, Code.usedtime: datetime.now()})
            session.commit()  # 必要的提交。否则失效
            tg1 = r.tg
            us1 = r.us
            used = r.used
            if re == 0: return await sendMessage(msg,
                                                 f'此 `{register_code}` \n注册码已被使用,是 [{used}](tg://user?id={used}) 的形状了喔')
            first = await bot.get_chat(tg1)
            x = data.us + us1
            session.query(Emby).filter(Emby.tg == msg.from_user.id).update({Emby.us: x})
            session.commit()
            await sendPhoto(msg, photo=bot_photo,
                            caption=f'🎊 少年郎，恭喜你，已经收到了 [{first.first_name}](tg://user?id={tg1}) 发送的邀请注册资格\n\n请选择你的选项~',
                            buttons=register_code_ikb)
            new_code = register_code[:-7] + "░" * 7
            await sendMessage(msg,
                              f'· 🎟️ 注册码使用 - [{msg.from_user.first_name}](tg://user?id={msg.chat.id}) [{msg.from_user.id}] 使用了 {new_code} 可以创建{us1}天账户咯~',
                              send=True)
            LOGGER.info(
                f"【注册码】：{msg.from_user.first_name}[{msg.chat.id}] 使用了 {register_code} - 可创建 {us1}天账户")

# @bot.on_message(filters.regex('exchange') & filters.private & user_in_group_on_filter)
# async def exchange_buttons(_, call):
#
#     await rgs_code(_, msg)

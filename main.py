from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove, ChatPermissions
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters, ConversationHandler, ChatMemberHandler
from datetime import timedelta
from db_interact import *
import os
from dotenv import load_dotenv
from keep_alive import keep_alive


print("ПРИВЕТ, Я ЗАПУСТИЛСЯ!")
rules = 'Пока что у нас анархия...'


def get_admin_markup():
    reply_keyboard = [['/ban', '/set_rules'], ['/promote_to_admin']]
    markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=False)
    return markup


def get_user_markup():
    reply_keyboard = [['/report']]
    markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=False)
    return markup


async def retry(update, context):
    await update.message.reply_text('Запрос сброшен')
    return ConversationHandler.END


# 2. Логика модерации (например, команда /ban)
# async def ban_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
#     # Проверяем, является ли сообщение ответом на чье-то другое
#     if update.message.reply_to_message:
#         user_to_ban = update.message.reply_to_message.from_user
#         try:
#             await context.bot.ban_chat_member(chat_id=update.effective_chat.id, user_id=user_to_ban.id)
#             await update.message.reply_text(f"Пользователь {user_to_ban.first_name} изгнан из беседы.")
#         except Exception as e:
#             await update.message.reply_text(f"Ошибка: проверьте мои права администратора!")
#     else:
#         await update.message.reply_text("Ответьте этой командой на сообщение того, кого нужно забанить.")


async def greet_new_member(update, context):
    for new_user in update.message.new_chat_members:
        if new_user.id == context.bot.id:
            await update.message.reply_text("Амдусиас на связи!")
            continue
        await context.bot.send_message(chat_id=update.effective_chat.id,
                                       text=f'Привет, {new_user.first_name}.'
                                       )


async def check_message(update, context):
    global rules
    main_is_admin = False
    answered_is_admin = False
    admins = await context.bot.get_chat_administrators(update.effective_chat.id)
    main_user = update.effective_user
    answered_user = None
    effective_chat = update.effective_chat
    if not check_chat_existence(effective_chat.id):
        add_chat(effective_chat.id)
    if not check_user_existence(effective_chat.id, main_user):
        add_user_to_chat(effective_chat.id, main_user.id)
    else:
        add_message(effective_chat.id, main_user.id)
    if answered_user:
        if not check_user_existence(effective_chat.id, answered_user.id):
            add_user_to_chat(effective_chat.id, answered_user.id)
    if update.message.reply_to_message:
        answered_user = update.message.reply_to_message.from_user
        if answered_user.id in [admin.user.id for admin in list(admins)]:
            answered_is_admin = True
    if main_user.id in [admin.user.id for admin in list(admins)]:
        main_is_admin = True
    if update.message.text.lower() == 'правила':
        if main_is_admin:
            reply_markup = get_admin_markup()
        else:
            reply_markup = get_user_markup()
        await update.message.reply_text(rules, reply_markup=reply_markup)
    elif update.message.text.lower().split('\n')[0] == 'установить правила':
        rules = '\n'.join(update.message.text.split('\n')[1:])
        await context.bot.send_message(chat_id=update.effective_chat.id, text='Правила установлены')
    elif update.message.text.lower() == 'повысить':
        if main_is_admin:
            if update.message.reply_to_message:
                if answered_user.id == context.bot.id:
                    await update.message.reply_text('Мне кажется, что у меня уже достаточно прав)')
                else:
                    try:
                        await context.bot.promote_chat_member(
                            chat_id=update.effective_chat.id,
                            user_id=answered_user.id,
                            can_manage_chat=True,
                            can_delete_messages=True,
                            can_manage_video_chats=True,
                            can_restrict_members=True,
                            can_promote_members=False,
                            can_change_info=False,
                            can_invite_users=False,
                            can_pin_messages=True
                        )
                        await update.message.reply_text(
                            f"Пользователь {answered_user.username} успешно назначен администратором!")
                    except Exception as e:
                        await update.message.reply_text(f"Не удалось повысить: {e}")
        else:
            await update.message.reply_text('У вас недостаточно прав для назначения администраторов (в отличии от меня :3)')
    elif update.message.text.lower() == 'понизить':
        if main_is_admin:
            if update.message.reply_to_message:
                if answered_user.id == context.bot.id:
                    await update.message.reply_text('Так, погоди-ка... ДА КАК ТЫ ПОСМЕЛ!!!')
                    await update.message.reply_text('Дуэль')
                else:
                    try:
                        await context.bot.promote_chat_member(
                            chat_id=update.effective_chat.id,
                            user_id=answered_user.id,
                            can_manage_chat=False,
                            can_delete_messages=False,
                            can_manage_video_chats=False,
                            can_restrict_members=False,
                            can_promote_members=False,
                            can_change_info=False,
                            can_invite_users=False,
                            can_pin_messages=False
                        )
                        await update.message.reply_text(
                            f"Пользователь {answered_user.username} понижен!")
                    except Exception as e:
                        await update.message.reply_text(f"Не удалось снять: {e}")
        else:
            await update.message.reply_text('У вас недостаточно прав для снятия администраторов (в отличии от меня :3)')
    elif update.message.text.lower().split('\n')[0] in ['поставить префикс', 'префикс']:
        if main_is_admin:
            prefix = update.message.text.split('\n')[1]
            if answered_is_admin:
                if update.message.reply_to_message:
                    await context.bot.set_chat_administrator_custom_title(
                        chat_id=update.effective_chat.id,
                        user_id=answered_user.id,
                        custom_title=prefix
                    )
            else:
                await context.bot.promote_chat_member(
                    chat_id=update.effective_chat.id,
                    user_id=answered_user.id,
                    can_manage_chat=False,
                    can_delete_messages=False,
                    can_manage_video_chats=False,
                    can_restrict_members=False,
                    can_promote_members=False,
                    can_change_info=False,
                    can_invite_users=True,
                    can_pin_messages=False
                )
                if update.message.reply_to_message:
                    await context.bot.set_chat_administrator_custom_title(
                        chat_id=update.effective_chat.id,
                        user_id=answered_user.id,
                        custom_title=prefix
                    )
                await context.bot.promote_chat_member(
                    chat_id=update.effective_chat.id,
                    user_id=answered_user.id,
                    can_manage_chat=False,
                    can_delete_messages=False,
                    can_manage_video_chats=False,
                    can_restrict_members=False,
                    can_promote_members=False,
                    can_change_info=False,
                    can_invite_users=False,
                    can_pin_messages=False
                )
            await update.message.reply_text(
                f"Пользователь {answered_user.username} теперь обладает префиксом {prefix}!")
        else:
            await update.message.reply_text('У вас недостаточно прав для выдачи префиксов (в отличии от меня :3)')
    elif update.message.text.lower() in ['молчать', 'заткнуть', 'мут']:
        if main_is_admin:
            permissions = ChatPermissions(
                can_send_messages=False,
                can_send_polls=False,
                can_send_other_messages=False,
                can_add_web_page_previews=False,
                can_change_info=False,
                can_invite_users=False,
                can_pin_messages=False
            )
            until = update.message.date + timedelta(minutes=120)
            await context.bot.restrict_chat_member(
                chat_id=update.effective_chat.id,
                user_id=answered_user.id,
                permissions=permissions,
                until_date=until
            )
            await update.message.reply_text(f"Пользователь замучен на 2 часа.")
        else:
            await update.message.reply_text('У вас недостаточно прав для выдачи мута (в отличии от меня :3)')
    elif update.message.text.lower() in ['говори']:
        if main_is_admin:
            permissions = ChatPermissions(
                can_send_messages=True,
                can_send_polls=False,
                can_send_other_messages=True,
                can_add_web_page_previews=False,
                can_change_info=False,
                can_invite_users=False,
                can_pin_messages=False
            )
            await context.bot.restrict_chat_member(
                chat_id=update.effective_chat.id,
                user_id=answered_user.id,
                permissions=permissions
            )
            await update.message.reply_text(f"Пользователь снова может говорить.")
        else:
            await update.message.reply_text('У вас недостаточно прав для снятия мута (в отличии от меня :3)')


if __name__ == '__main__':
    load_dotenv()
    keep_alive()
    TOKEN = os.getenv("BOT_TOKEN")
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(ChatMemberHandler(delete_user_from_chat, ChatMemberHandler.CHAT_MEMBER))
    app.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, greet_new_member))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), check_message))
    app.run_polling(allowed_updates=["message", "chat_member", "inline_query"])

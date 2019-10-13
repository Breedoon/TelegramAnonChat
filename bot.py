# git push heroku master
import logging, time
import os
import random

from telegram import ParseMode
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters

from config import token, channel_id, admin_id, whitelist, channel_invite_link, admin_username, webhook_url

# Enable logging
logging.basicConfig(filename="anon_bot.log", format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

admins = []

BASE_ADMIN_PERMISSIONS = {
    'can_post_messages': True,
    'can_change_info': False,
    'can_delete_messages': False,
    'can_edit_messages': False,
    'can_invite_users': False,
    'can_promote_members': False,
    'can_restrict_members': False,
    # 'is_anonymous': True,  # group property, not allowed in channels
}


def update_admins(update, context):
    if len(admins) != 0:
        return
    admins.clear()
    for user in context.bot.get_chat_administrators(channel_id)[::-1]:
        if user.user.id in whitelist:
            continue
        admins.append(user.user.id)


def start(update, context):
    update_admins(update, context)

    # Find out who sent the request and whether they are in the channel
    try:
        user = context.bot.get_chat_member(channel_id, update.message.from_user.id)
        user_status = user['status']
    except:  # they might not be in the channel so mark them as left
        user_status = 'left'

    # Not int the channel, ask them to join first
    if user_status != 'member' and user_status != 'administrator' and user_status != 'creator':
        update.message.reply_text(f'You need to join the chat first: {channel_invite_link}')
        update.message.reply_text("And try again after you're done: /start")
        return

    # if they can't post yet, try giving them permissions
    elif user_status != 'administrator' or not user.can_post_messages:
        try:
            context.bot.promote_chat_member(channel_id, update.message.from_user.id, **BASE_ADMIN_PERMISSIONS)
            admins.append(update.message.from_user.id)
            update.message.reply_text(fr"Success\! You can now post in the [chat]({channel_invite_link})\!",
                                      parse_mode=ParseMode.MARKDOWN_V2)
        except Exception as e:
            if e.message == 'Admins_too_much':  # already over 50 admins
                # so, demote a random admin and try again (queueing admins didn't work)
                admin_to_replace = admins.pop(random.randint(0, len(admins) - 1))
                try:
                    context.bot.promote_chat_member(channel_id, admin_to_replace)  # Demoting
                    time.sleep(0.5)
                    context.bot.promote_chat_member(channel_id, update.message.from_user.id, **BASE_ADMIN_PERMISSIONS)
                    update.message.reply_text(fr"Success\! You can now post in the [chat]({channel_invite_link})\!",
                                              parse_mode=ParseMode.MARKDOWN_V2)
                    admins.append(update.message.from_user.id)

                except Exception as e:  # still something didn't work
                    context.error = e
                    error(update, context)
                    update.message.reply_text(
                        f"Sorry, there was an unknown error. You can contact {admin_username} for help.")
            else:
                context.error = e
                error(update, context)
                update.message.reply_text(
                    f"Sorry, there was an unknown error. You can contact {admin_username} for help.")

    else:  # they already can write in the chat
        update.message.reply_text(
            fr"Looks like you're already set up to post in the [chat]({channel_invite_link})\!",
            parse_mode=ParseMode.MARKDOWN_V2)


def help(update, context):
    update.message.reply_text('Command list:\n'
                              '/start - get posting rights in the chat\n'
                              '/help - show help message')


def error(update, context):
    """Log Errors caused by Updates."""
    logger.error('Update "%s" caused error "%s"', update, context.error)
    context.bot.send_message(admin_id, text=str(context.error))


def new_message(update, context):
    logger.info('New message: %s', update)
    if update.effective_chat['id'] == channel_id:  # ignore messages from the channel
        return
    if '/' not in update.message.text:  # forward message to the channel
        context.bot.send_message(channel_id, text=update.message.text)


def main():
    # Create the Updater and pass it the token.
    updater = Updater(token, use_context=True)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # on different commands - answer in Telegram
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", help))
    dp.add_handler(MessageHandler(Filters.all, new_message))

    # log all errors
    dp.add_error_handler(error)

    # updater.start_polling()  # for local debugging

    updater.start_webhook(listen="0.0.0.0",
                          port=int(os.environ.get('PORT', 5000)),
                          url_path=token,
                          webhook_url=webhook_url + token)

    updater.idle()


if __name__ == '__main__':
    main()

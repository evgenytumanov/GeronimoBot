#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""


"""

from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
import logging

# STATICS
TELEGRAM_API_TOKEN = '492982205:AAGsU3BSci1GV3OKaxcIyzDKGH5GY1Ciw1s'
ON_START_MESSAGE = "Привет, Маш. Меня зовут Джеронимо. "
ON_HELP_MESSAGE = "Спроси у Жени \n https://t.me/TumanovEvgeny"
ON_MESSAGE = "Пока что, я буду писать тебе в определенные часы. Я еще не умею поддерживать естественный диалог :)"
NON_FAMILY_REPLY = "Я покамест являюсь закрытым ботом. Извините :)"

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)


# Define a few command handlers. These usually take the two arguments bot and
# update. Error handlers also receive the raised TelegramError object in error.


def security_check(bot_update_handler):
    def a_wrapper_accepting_arguments(bot, update):
        if update.message.from_user.username in ['MariaTeryoshkina', "TumanovEvgeny"]:
            bot_update_handler(bot, update)
        else:
            update.message.reply_text(NON_FAMILY_REPLY)
    return a_wrapper_accepting_arguments

@security_check
def start(bot, update):
    """Send a message when the command /start is issued."""
    update.message.reply_text(ON_START_MESSAGE)

@security_check
def help(bot, update):
    """Send a message when the command /help is issued."""
    update.message.reply_text(ON_HELP_MESSAGE)

def error(bot, update, error):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, error)

@security_check
def message_handler(bot, update):
    """Geronimo reply"""
    update.message.reply_text(ON_MESSAGE)


def main():
    """Start the bot."""
    # Create the EventHandler and pass it your bot's token.
    updater = Updater(TELEGRAM_API_TOKEN)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # on different commands - answer in Telegram
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", help))

    # on noncommand i.e message - echo the message on Telegram
    dp.add_handler(MessageHandler(Filters.text, message_handler))

    # log all errors
    dp.add_error_handler(error)

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()


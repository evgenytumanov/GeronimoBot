#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
"""

from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
import logging
import telegram
from datetime import datetime
from threading import Timer
import pickle
import pandas as pd

# STATICS
with open('token.txt', 'r') as token_file:
    TELEGRAM_API_TOKEN = token_file.readline().strip()
BOT = telegram.Bot(TELEGRAM_API_TOKEN)


ON_START_MESSAGE = "Привет, Маш. Меня зовут Джеронимо. Я хочу помочь тебе стать писательницей! Я буду присылать тебе разные обучающие материалы, задания и, конечно, стараться давать тебе обратную связь. Давай попробуем стать супер писателями!"
ON_HELP_MESSAGE = "Спроси у Жени \n https://t.me/TumanovEvgeny"
ON_MESSAGE = "Пока что, я буду писать тебе в определенные часы. Я еще не умею поддерживать естественный диалог :)"
NON_FAMILY_REPLY = "Я покамест являюсь закрытым ботом. Извините :)."
CONTENT_PROVIDERS_USERNAMES = ["TumanovEvgeny"]
CONTENT_RECEIVERS_USERNAMES = ["MariaTeryoshkina"]


# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)


# Define a few command handlers. These usually take the two arguments bot and
# update. Error handlers also receive the raised TelegramError object in error.

def security_check(bot_update_handler):
    def a_wrapper_accepting_arguments(bot, update):
        if update.message.from_user.username in CONTENT_PROVIDERS_USERNAMES+CONTENT_RECEIVERS_USERNAMES:
            bot_update_handler(bot, update)
        else:
            update.message.reply_text(NON_FAMILY_REPLY)
    return a_wrapper_accepting_arguments

@security_check
def start(bot, update):
    """Send a message when the command /start is issued."""
    update.message.reply_text(ON_START_MESSAGE)
    print(update.message.from_user.username, update.message.chat.id)
    USERNAME_TO_CHAT_ID[update.message.from_user.username] = update.message.chat.id
    print(USERNAME_TO_CHAT_ID)
    #Geronimo dumps chat_id into local file
    with open('USERNAME_TO_CHAT_ID.pkl', 'wb') as handle:
        pickle.dump(USERNAME_TO_CHAT_ID, handle, protocol=pickle.HIGHEST_PROTOCOL)

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
    print('message_handler')
    if update.message.from_user.username in CONTENT_PROVIDERS_USERNAMES:
        message_from_cprovider_handler(bot, update)
    elif update.message.from_user.username in CONTENT_RECEIVERS_USERNAMES:
        print('Fot message from Maria')
        message_from_creceiver_handler(bot, update)

# security_check will be called on parent function message_handler
def message_from_cprovider_handler(bot, update):
    try:
        timestamp, message_text = update.message.text.strip().split('|')
        target_time = datetime.strptime(timestamp, '%Y-%m-%d %H:%M')
        print(target_time)
        now = datetime.today()
        delta_t=target_time-now
        secs=delta_t.seconds+1
        job = lambda bot, job:  BOT.send_message(chat_id=USERNAME_TO_CHAT_ID[CONTENT_RECEIVERS_USERNAMES[0]], text=message_text)
        updater.job_queue.run_once(job, target_time)
        logger.log(0, str(updater.job_queue))
        print(updater.job_queue)  
    except:
        logger.log(0, "Wrong format")
        print("Wrong format")
    

# security_check will be called on parent function message_handler
def message_from_creceiver_handler(bot, update):
    try:
        update.message.reply_text(ON_MESSAGE)
        BOT.send_message(chat_id=USERNAME_TO_CHAT_ID[CONTENT_PROVIDERS_USERNAMES[0]], text='Маша написала мне: {}'.format(update.message.text))
    except:
        logger.log(0, "Wrong format")
        print("Wrong format")

def shared_document_handler(bot, update):
    file_id = update.message.document.file_id
    file_info = bot.get_file(file_id)
    newFile = bot.get_file(file_id)
    newFile.download('./assignments/{}'.format(file_info.file_path.strip().split('/')[-1]))
    BOT.send_message(chat_id=USERNAME_TO_CHAT_ID[CONTENT_PROVIDERS_USERNAMES[0]], text='Маша выполнила задание!')


def main():
    """Start the bot."""
    # Create the EventHandler and pass it your bot's token.
    global updater
    updater = Updater(TELEGRAM_API_TOKEN)
    
    global USERNAME_TO_CHAT_ID
    USERNAME_TO_CHAT_ID = {}
    #Geronimo dumps chat_id into local file
    with open('USERNAME_TO_CHAT_ID.pkl', 'rb') as handle:
        USERNAME_TO_CHAT_ID = pickle.load(handle)

    # schedule all content by schedule.csv
    global SCHEDULE
    SCHEDULE = pd.read_csv('./schedule.csv', sep=';', parse_dates=True, index_col='timestamp')
    print(SCHEDULE)

    for t in SCHEDULE.index:        
        job = lambda bot, job:  BOT.send_document(chat_id=USERNAME_TO_CHAT_ID[CONTENT_RECEIVERS_USERNAMES[0]], document=open('./content/' + SCHEDULE['filename'].loc[t], 'rb'))
        updater.job_queue.run_once(job, t)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # on different commands - answer in Telegram
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", help))

    # on noncommand i.e message - echo the message on Telegram
    dp.add_handler(MessageHandler(Filters.text, message_handler))
    dp.add_handler(MessageHandler(Filters.document, shared_document_handler))

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

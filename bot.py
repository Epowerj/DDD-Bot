
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
import logging
from key import apikey
import datetime
import random

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)


def start(bot, update):
    bot.sendMessage(update.message.chat_id, text="Hey Tribow!")


def help(bot, update):
    bot.sendMessage(update.message.chat_id, text='Just ask @Epowerj')


def ping(bot, update):
    bot.sendMessage(update.message.chat_id, text='Pong')
    

def time(bot, update):
    bot.sendMessage(update.message.chat_id, text=str(datetime.datetime.now()))


def roll(bot, update):
    bot.sendMessage(update.message.chat_id, text=str(random.randint(1, 20))


def error(bot, update, error):
    print('Update "%s" caused error "%s"' % (update, error))


def main():
    updater = Updater(apikey)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", help))
    dp.add_handler(CommandHandler("ping", ping))
    dp.add_handler(CommandHandler("time", time))

    dp.add_error_handler(error)

    updater.start_polling(timeout=5)

    # Run the bot until the user presses Ctrl-C or the process receives SIGINT, SIGTERM or SIGABRT
    updater.idle()


if __name__ == '__main__':
    main()


from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
import logging
from key import apikey
import datetime, random, json

#tribow_id = 106890603
#adventure_id = -1001030866550

admin_id = 83218061
chatroom_id = -146928430

savepath = "info.dict"
info = {}

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)


def load_info():
    global info

    save = open(savepath, 'r')
    info = json.load(save)

def save_info():
    save = open(savepath, 'w')
    json.dump(info, save)


def start(bot, update):
    bot.sendMessage(update.message.chat_id, text="Hey!")


def help(bot, update):
    bot.sendMessage(update.message.chat_id, text='Just ask @Epowerj')


def ping(bot, update):
    bot.sendMessage(update.message.chat_id, text='Pong')
    

def time(bot, update):
    bot.sendMessage(update.message.chat_id, text=str(datetime.datetime.now()))


def roll(bot, update):
    bot.sendMessage(update.message.chat_id, reply_to_message_id=update.message.message_id, text=str(random.randint(1, 20)))


def chatinfo(bot, update):
    bot.sendMessage(update.message.chat_id, text="chat_id is "+str(update.message.chat_id))
    bot.sendMessage(update.message.chat_id, text="user id is "+str(update.message.from_user.id))


def error(bot, update, error):
    print('Update "%s" caused error "%s"' % (update, error))


def say(bot, update):
    if update.message.from_user.id == admin_id:
        commandtext = update.message.text.split(' ', 1)
        bot.sendMessage(chatroom_id, text=commandtext[1])
    else:
        bot.sendMessage(update.message.chat_id, text="You are not authorized")


def info(bot, update):
    global info

    commandtext = update.message.text.split(' ', 1)[1]

    if commandtext in info:
        global info
        bot.sendMessage(update.message.chat_id, text=info[commandtext])
    else:
        bot.sendMessage(update.message.chat_id, text="No info found on '"+commandtext+"'")


def setinfo(bot, update):
    global info

    if update.message.from_user.id == admin_id:
        commandtext = update.message.text.split(' ', 2)
        info[commandtext[1]] = commandtext[2]

        save_info()
    else:
        bot.sendMessage(update.message.chat_id, text="You are not authorized")


def main():
    global info

    print(info)
    load_info()
    print(info)

    updater = Updater(apikey)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", help))
    dp.add_handler(CommandHandler("ping", ping))
    dp.add_handler(CommandHandler("time", time))
    dp.add_handler(CommandHandler("roll", roll))
    dp.add_handler(CommandHandler("chatinfo", chatinfo))
    dp.add_handler(CommandHandler("say", say))
    dp.add_handler(CommandHandler("info", info))
    dp.add_handler(CommandHandler("setinfo", setinfo))

    dp.add_error_handler(error)

    updater.start_polling(timeout=5)

    # Run the bot until the user presses Ctrl-C or the process receives SIGINT, SIGTERM or SIGABRT
    updater.idle()


if __name__ == '__main__':
    main()


from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackQueryHandler
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from key import apikey, admin_id, chatroom_id
from urllib.parse import urlparse
import os, logging, datetime, json, random, time, psycopg2

conn = False
cur = False

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)


def db_connect():
    #connect to the database
    #urlparse.uses_netloc.append("postgres")
    url = urlparse(os.environ["DATABASE_URL"])

    global conn
    conn = psycopg2.connect(
        database=url.path[1:],
        user=url.username,
        password=url.password,
        host=url.hostname,
        port=url.port
    )

    global cur
    cur = conn.cursor()

    #check if table for the app exists or not
    cur.execute("SELECT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = '" + str(os.environ.get("APPNAME")) + "');")

    if not (bool(cur.rowcount)): #if it doesn't exist
        print("Table not found, creating new one")
        cur.execute("CREATE TABLE " + str(os.environ.get("APPNAME") + " (id serial PRIMARY KEY, info varchar, data varchar);"))


def db_disconnect():
    cur.close()
    conn.close()


def add_info():
    cur.execute("INSERT INTO ")


def start(bot, update):
    bot.sendMessage(update.message.chat_id, text="Hey!")


def help(bot, update):
    bot.sendMessage(update.message.chat_id, text='Just ask @Epowerj')


def ping(bot, update):
    bot.sendMessage(update.message.chat_id, text='Pong')


def time(bot, update):
    bot.sendMessage(update.message.chat_id, text=str(datetime.datetime.now()))


def roll(bot, update):
   action(bot, update, random.randint(1, 20))


def qroll(bot, update):
    roll = random.randint(1, 20)
    bot.sendMessage(update.message.chat_id, reply_to_message_id=update.message.message_id, text="Your roll was " + str(roll))


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


def parse(bot, update):
    print("Message from " + update.message.from_user.first_name + "(" + str(update.message.from_user.id) + "): " + update.message.text + " (" + str(update.message.message_id) + ")")


def info(bot, update):
    global char_info

    commandtext = update.message.text.split(' ')

    if len(commandtext) >= 2:
        commandtext = commandtext[1].lower()

        if commandtext in char_info:
            bot.sendMessage(update.message.chat_id, text=char_info[commandtext])
        else:
            bot.sendMessage(update.message.chat_id, text="No info found on '"+commandtext+"'")
    else:
        bot.sendMessage(update.message.chat_id, text="Usage: /info <topic>")


def action(bot, update, roll=-1):
    global next_action

    commandtext = update.message.text.split(' ')

    if len(commandtext) >= 2:
        commandtext = update.message.text.split(' ', 1)[1]

        if roll == -1:
            next_action[str(update.message.from_user.id)] = update.message.from_user.first_name + ' - ' + commandtext
        else:
            next_action[str(update.message.from_user.id)] = update.message.from_user.first_name + ' - ' + str(roll) + ' - ' + commandtext

        save_info()

        if roll == -1:
            bot.sendMessage(update.message.chat_id, reply_to_message_id=update.message.message_id, text="Action saved")
        else:
            if roll == 1:
                bot.sendMessage(update.message.chat_id, reply_to_message_id=update.message.message_id, text="Your roll was " + str(roll) + "\nGood luck, lol")
            else:
                bot.sendMessage(update.message.chat_id, reply_to_message_id=update.message.message_id, text="Your roll was " + str(roll))
    else:
        bot.sendMessage(update.message.chat_id, reply_to_message_id=update.message.message_id, text="Your current action is: '" + next_action[str(update.message.from_user.id)] + "' \n Do /action <your next move> to update")


def setinfo(bot, update):
    global char_info

    if update.message.from_user.id == admin_id:
        commandtext = update.message.text.split(' ', 2)
        char_info[commandtext[1].lower()] = commandtext[2]

        save_info()

        bot.sendMessage(update.message.chat_id, text="Info saved")
    else:
        bot.sendMessage(update.message.chat_id, text="You are not authorized")


def listactions(bot, update):
    global next_action

    if update.message.from_user.id == admin_id:
        for action in next_action:
            bot.sendMessage(update.message.chat_id, text=next_action[action])
    else:
        bot.sendMessage(update.message.chat_id, text="You are not authorized")


def clearactions(bot, update):
    global next_action

    if update.message.from_user.id == admin_id:
        for action in next_action:
            next_action[action] = ''
    else:
        bot.sendMessage(update.message.chat_id, text="You are not authorized")


def main():
    db_connect()

    TOKEN = apikey
    PORT = int(os.environ.get('PORT', '5000'))
    updater = Updater(TOKEN)
    dp = updater.dispatcher
    # add handlers
    updater.start_webhook(listen="0.0.0.0",
                      port=PORT,
                      url_path=TOKEN)
    updater.bot.setWebhook("https://" + str(os.environ.get("APPNAME")) + ".herokuapp.com/" + TOKEN)

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", help))
    dp.add_handler(CommandHandler("ping", ping))
    dp.add_handler(CommandHandler("time", time))
    dp.add_handler(CommandHandler("roll", roll))
    dp.add_handler(CommandHandler("qroll", qroll))
    dp.add_handler(CommandHandler("chatinfo", chatinfo))
    dp.add_handler(CommandHandler("say", say))
    dp.add_handler(CommandHandler("info", info))
    dp.add_handler(CommandHandler("action", action))
    dp.add_handler(CommandHandler("setinfo", setinfo))
    dp.add_handler(CommandHandler("listactions", listactions))
    dp.add_handler(CommandHandler("clearactions", clearactions))

    dp.add_handler(MessageHandler([Filters.text], parse))

    dp.add_error_handler(error)

    updater.idle()

    db_disconnect()


if __name__ == '__main__':
    main()

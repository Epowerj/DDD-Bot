
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackQueryHandler
#from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from key import apikey, admin_id, chatroom_id, table_name
from urllib.parse import urlparse
import os, logging, datetime, json, random, time
from pymongo import MongoClient

db = 0
char_info = {}
next_action = {}
char_stats = {}
char_equips = {}
char_inventory = {}

waiting_for_music=False

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)


def load_info():
    global char_info
    global next_action
    global char_stats
    global char_equips
    global char_inventory
    global db

    client = MongoClient(str(os.environ["MONGODB_URI"]))  # connect to the server
    db = client[str(os.environ["MONGODB_DATABASE"])]  # connect to database

    char_collection = db.charinfo  # select collection
    action_collection = db.actions
    stats_collection = db.stats
    equips_collection = db.equips
    inventory_collection = db.inventory

    char_info = char_collection.find_one()
    print(char_info)
    next_action = action_collection.find_one()
    print(next_action)
    char_stats = stats_collection.find_one()
    print(char_stats)
    char_equips = equips_collection.find_one()
    print(char_equips)
    char_inventory = equips_collection.find_one()
    print(char_inventory)

    if char_info is None:
        char_info = {}

    if next_action is None:
        next_action = {}

    if char_stats is None:
        char_stats = {}

    if char_equips is None:
        char_equips = {}

    if char_inventory is None:
        char_inventory = {}


def save_info():
    global char_info
    global next_action
    global char_stats
    global char_equips
    global char_inventory
    global db

    db.charinfo.update({}, char_info, upsert=True)
    db.actions.update({}, next_action, upsert=True)
    db.stats.update({}, char_stats, upsert=True)
    db.equips.update({}, char_equips, upsert=True)
    db.inventory.update({}, char_inventory, upsert=True)


def start(bot, update):
    bot.sendMessage(update.message.chat_id, text="Hey!")


def help(bot, update):
    bot.sendMessage(update.message.chat_id, text='Just ask @Epowerj. This bot currently uses a dev build.')


def adminhelp(bot, update):
    bot.sendMessage(update.message.chat_id, text='Admin commands: /say <message> /qsay <message> /listactions /clearactions /setinfo <indexword> <description>')


def ping(bot, update):
    bot.sendMessage(update.message.chat_id, text='Pong')


def time(bot, update):
    bot.sendMessage(update.message.chat_id, text=str(datetime.datetime.now()))


# TODO remake the rolls

def parse_roll(toparse):
    toparse.lower()

    # count the number of 'd' characters
    if (toparse.count('d') != 1):
        return False

    toparse = toparse.split('d')

    # check if characters after the 'd' are an integer
    try:
        die = int(toparse[1])
    except ValueError:
        return False  # it was a string, not an int.

    # check if number is 0 or less
    if (int(toparse[1]) < 1):
        return False

    if (toparse[0] != ''):
        # check if characters before the 'd' are an integer
        try:
            die_amount = int(toparse[0])
        except ValueError:
            return False  # it was a string, not an int.

        # check if number is 0 or less
        if (int(toparse[0]) < 1):
            return False

        result_rolls = []

        for i in range(die_amount):
            result_rolls.append(random.randint(1, die))

        result = ""
        total_sum = 0

        for value in result_rolls:
            total_sum += value

            if (result == ""):
                result += (str(value) + " ")
            else:
                result += (" + " + str(value))

        result += (" = " + str(total_sum))

        return result

    else:
        return random.randint(1, die)


def roll(bot, update):
    commandtext = update.message.text.split(' ')

    if len(commandtext) >= 2:
        roll = parse_roll(commandtext[1])

        if (roll == False):
            bot.sendMessage(update.message.chat_id, text="Incorrect Usage \nUsage: /roll d<die size>")
        else:
            bot.sendMessage(update.message.chat_id, reply_to_message_id=update.message.message_id, text="Your roll was " + str(roll))
            send_to_admin(bot, update.message.from_user.first_name + "\n[Roll " + commandtext[1] + "]\n> " + str(roll))

    else:
        bot.sendMessage(update.message.chat_id, text="Usage: /roll d<die size>")


def chatinfo(bot, update):
    bot.sendMessage(update.message.chat_id, text="chat_id is "+str(update.message.chat_id))
    bot.sendMessage(update.message.chat_id, text="user id is "+str(update.message.from_user.id))


def error(bot, update, error):
    print('Update "%s" caused error "%s"' % (update, error))

def qsay(bot, update):
    if update.message.from_user.id == admin_id:
        commandtext = update.message.text.split(' ', 1)
        bot.sendMessage(chatroom_id, text=commandtext[1])
        #bot.sendMessage(int(os.environ["DDDCHANNEL"]), text=commandtext[1])
    else:
        bot.sendMessage(update.message.chat_id, text="You are not authorized")

def say(bot, update): #TODO add photo and file support
    if update.message.from_user.id == admin_id:
        commandtext = update.message.text.split(' ', 1)
        bot.sendMessage(chatroom_id, text=commandtext[1])
        bot.sendMessage(int(os.environ["DDDCHANNEL"]), text=commandtext[1])
    else:
        bot.sendMessage(update.message.chat_id, text="You are not authorized")


def parse(bot, update):
    #print(str(update.channel_post.chat_id))
    print("file: " + str(update.message.document.file_id))
    print("Message from " + update.message.from_user.first_name + "(" + str(update.message.from_user.id) + "): " +
          update.message.text + " (" + str(update.message.message_id) + ")")


def info(bot, update): #TODO add automatic indexing an inline buttons
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


def stats(bot, update): #TODO automatic indexing and inline buttons
    global char_stats

    commandtext = update.message.text.split(' ')

    if len(commandtext) >= 2:
        commandtext = commandtext[1].lower()

        if commandtext in char_stats:
            bot.sendMessage(update.message.chat_id, text=char_stats[commandtext])
        else:
            bot.sendMessage(update.message.chat_id, text="No info found on '"+commandtext+"'")
    else:
        bot.sendMessage(update.message.chat_id, text="Usage: /stats <topic>")


def equips(bot, update): #TODO automatic indexing and inline buttons
    global char_equips

    commandtext = update.message.text.split(' ')

    if len(commandtext) >= 2:
        commandtext = commandtext[1].lower()

        if commandtext in char_equips:
            bot.sendMessage(update.message.chat_id, text=char_equips[commandtext])
        else:
            bot.sendMessage(update.message.chat_id, text="No info found on '"+commandtext+"'")
    else:
        bot.sendMessage(update.message.chat_id, text="Usage: /equips <topic>")


def inventory(bot, update): #TODO automatic indexing and inline buttons
    global char_inventory

	#commandtext = update.message.text.split(' ')

    #if len(commandtext) >= 2:
    commandtext = str(update.message.from_user.id)

    if commandtext in char_inventory:
        bot.sendMessage(update.message.chat_id, text=char_inventory[commandtext])
    else:
        bot.sendMessage(update.message.chat_id, text="No info found on '"+commandtext+"'")
    #else:
        #bot.sendMessage(update.message.chat_id, text="Usage: /inventory")


def send_to_admin(bot, message):
    bot.sendMessage(admin_id, text=message)


def action(bot, update): #TODO add support for multiple actions
    global next_action

    commandtext = update.message.text.split(' ')

    if len(commandtext) >= 2:
        commandtext = update.message.text.split(' ', 1)[1]

        send_to_admin(bot, update.message.from_user.first_name + "\n[Action]\n> " + commandtext)

        bot.sendMessage(update.message.chat_id, reply_to_message_id=update.message.message_id, text="Action saved")

    else:
        bot.sendMessage(update.message.chat_id, reply_to_message_id=update.message.message_id, text="Usage: /action <your action>")


def setinfo(bot, update):
    global char_info

    if update.message.from_user.id == admin_id:  # if admin
        commandtext = update.message.text.split(' ', 2)

        char_info[commandtext[1].lower()] = commandtext[2]

        save_info()

        bot.sendMessage(update.message.chat_id, text="Info saved")
    else:
        bot.sendMessage(update.message.chat_id, text="You are not authorized")


def setstats(bot, update):
    global char_stats

    if update.message.from_user.id == admin_id:  # if admin
        commandtext = update.message.text.split(' ', 2)

        char_stats[commandtext[1].lower()] = commandtext[2]

        save_info()

        bot.sendMessage(update.message.chat_id, text="Info saved")
    else:
        bot.sendMessage(update.message.chat_id, text="You are not authorized")


def setequips(bot, update):
    global char_equips

    if update.message.from_user.id == admin_id:  # if admin
        commandtext = update.message.text.split(' ', 2)

        char_equips[commandtext[1].lower()] = commandtext[2]

        save_info()

        bot.sendMessage(update.message.chat_id, text="Info saved")
    else:
        bot.sendMessage(update.message.chat_id, text="You are not authorized")


def setinventory(bot, update):
    global char_inventory

    commandtext = update.message.text.split(' ', 1)

    char_equips[str(update.message.from_user.id)] = commandtext[1]

    save_info()

    bot.sendMessage(update.message.chat_id, text="Inventory saved")


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
    global char_info
    global next_action

    load_info()
    print(char_info)
    print(next_action)

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
    dp.add_handler(CommandHandler("adminhelp", adminhelp))
    dp.add_handler(CommandHandler("ping", ping))
    dp.add_handler(CommandHandler("time", time))
    dp.add_handler(CommandHandler("roll", roll))
    #dp.add_handler(CommandHandler("qroll", qroll))
    dp.add_handler(CommandHandler("chatinfo", chatinfo))
    dp.add_handler(CommandHandler("say", say))
    dp.add_handler(CommandHandler("qsay", qsay))
    dp.add_handler(CommandHandler("info", info))
    dp.add_handler(CommandHandler("stats", stats))
    dp.add_handler(CommandHandler("equips", equips))
    dp.add_handler(CommandHandler("inventory", inventory))
    dp.add_handler(CommandHandler("action", action))
    dp.add_handler(CommandHandler("setinfo", setinfo))
    dp.add_handler(CommandHandler("setstats", setstats))
    dp.add_handler(CommandHandler("setequips", setequips))
    dp.add_handler(CommandHandler("setinventory", setinventory))
    dp.add_handler(CommandHandler("listactions", listactions))
    dp.add_handler(CommandHandler("clearactions", clearactions))

    dp.add_handler(MessageHandler([Filters.text], parse))

    dp.add_error_handler(error)

    updater.idle()


if __name__ == '__main__':
    main()

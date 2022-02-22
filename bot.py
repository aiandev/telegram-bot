from telegram.ext import updater, MessageHandler, Updater, CommandHandler
from telegram.ext.filters import Filters
import requests,json
import os
import redis
from datetime import date

redcon = redis.StrictRedis(host='localhost', port=6379, db=2)

config = json.load(open('config.json','r'))
TOKEN = config['token']
print(TOKEN)

DEV = False
updater = Updater(TOKEN, use_context=True)
dp = updater.dispatcher



stabila_group = config['stabilagroup']

webhook_url = 'https://stabilascan.org/api/utils/telegram-webhooks/'
PORT = int(os.environ.get('PORT','8443'))

def new_user(update):
    new_members = update.message.new_chat_members
    print(new_members)
    # do your stuff here:
    for member in new_members:
        print(member)
        #print('1',member['username'])
        redcon.hset(member['username'],'id',member['id'])
        redcon.hset(member['username'],'isbot', "False")
        redcon.hset(member['username'],'joined', "True")
        times = redcon.hget(member['username'],'jtimes')
        if times!=None:
            times=int(times)+1
            redcon.hset(member['username'], 'jtimes', times)
        else:
            redcon.hset(member['username'],'jtimes', 1)


    update.message.reply_text("Welcome "+member['username'])

def left_user(update):
    left_member = update.message.left_chat_member
    # do your stuff here:
    print(left_member)
        #print('1',member['username'])

    redcon.hset(left_member['username'],'joined', "False")
    times = redcon.hget(left_member['username'], 'ltimes')
    if times != None:
        times = int(times) + 1
        redcon.hset(left_member['username'], 'ltimes', times)
    else:
        redcon.hset(left_member['username'], 'ltimes', 1)
    update.message.reply_text("Bye "+left_member['username'])

def start(update, context):
    if update.message.chat.type == 'private':
        user = str(update.message.chat.username)
        print(user)

def main():

    print("1")
    dp.add_handler(MessageHandler(Filters.status_update.new_chat_members, new_user))
    print("2")
    dp.add_handler(MessageHandler(Filters.status_update.left_chat_member, left_user))
    dp.add_handler(MessageHandler(Filters.regex("start"), start))


if __name__ == '__main__':

    main()
    if DEV is not True:
        print(webhook_url+TOKEN)
        updater.start_webhook(listen="0.0.0.0",port=PORT,url_path=TOKEN)
        updater.bot.set_webhook(webhook_url + TOKEN)
    else:
        print("4")
        updater.start_polling(clean=True)
    print("Bot Started")
    updater.idle()

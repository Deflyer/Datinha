import json
from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext

with open('config.json', 'r') as config_file:
    config = json.load(config_file)
    TOKEN = config['key']

def start(update: Update, context: CallbackContext) -> None:
    update.message.reply_text('Eu consigo falar!')

def help(update: Update, context: CallbackContext) -> None:
    update.message.reply_text('Aqui estão os meus comandos')
def main():
    updater = Updater(TOKEN)

    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))

    dp.add_handler(CommandHandler("help", help))

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
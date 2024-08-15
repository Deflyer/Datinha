import json
from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext

# Fiz o bot seguindo um tutorial da biblioteca do telegram mais antiga, 13.13, não funciona na mais nova
# Vi algo sobre colocar async nas funções, dá pra deixar assim também ou atualizar, vc que sabe

# O que falta fazer: Uma função para mexer com a api do kaggle pelo menos e printar as competições
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
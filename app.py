import json
from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext
import kaggle
from kaggle.rest import ApiException
from kaggle.api.kaggle_api_extended import KaggleApi

def start(update: Update, context: CallbackContext):
    '''
    Core Telegram command to a bot (same as help()).
    '''

    msg = 'Hello, I am here to help you find cool Data Science Competitions!'
    msg += '\n\nYou can control me by using these commands:\n\n'
    msg += '/kaggle - List 5 Kaggle competitions and their information'

    update.message.reply_text(msg)

def help(update: Update, context: CallbackContext):
    '''
    Core Telegram command to a bot (same as start()).
    '''

    msg = 'Hello, I am here to help you find cool Data Science Competitions!'
    msg += '\n\nYou can control me by using these commands:\n\n'
    msg += '/kaggle - List 5 Kaggle competitions and their information'

    update.message.reply_text(msg)

def get_competitions(group = "general", category = "all", sort_by="latestDeadline", page = 1, search=''):
    '''
    Uses the Kaggle API to get a list of current competitions.
    '''

    try:
        return api.competitions_list()
    except ApiException as e:
        print("Exception when calling KaggleApi->competitions_list: %s\n" % e)

def create_competition_print(c, n_comp, total_comp):
    '''
    Formats a string with the competition information. Used to get a more beautiful Telegram message.
    '''
    
    response = 'Title: ' + c.title + '\nDescription: ' + c.description + '\nCategory: ' + c.category + '\nReward: ' + c.reward
    response += '\nMax Team Size: ' + str(c.maxTeamSize) + '\nDeadline: ' + str(c.deadline) + '\n' + c.url

    if n_comp+1 < total_comp:
        response = response + '\n\n----------------------------------------------------\n\n'
        
    return response

def kaggle(update: Update, context: CallbackContext):
    '''
    Telegram command to list 5 Kaggle competitions and their information.
    '''

    competitions = get_competitions()

    response = ''
    number_comp = 5

    for i, comp in enumerate(competitions[:number_comp]):
        response += create_competition_print(comp, i, number_comp)

    update.message.reply_text(response, disable_web_page_preview=True)

# Loading configuration file to get the key of our Telegram bot.
with open('config.json', 'r') as config_file:
    config = json.load(config_file)
    TOKEN = config['key']

# Linking this code to our Telegram bot.
updater = Updater(TOKEN)
dp = updater.dispatcher
print('Bot linked!')

# Accessing Kaggle API.
api = KaggleApi()
api.authenticate()
print('Kaggle API accessed!')

# Adding commands to the bot.
dp.add_handler(CommandHandler("start", start))
dp.add_handler(CommandHandler("help", help))
dp.add_handler(CommandHandler("kaggle", kaggle))
print('Functionalities linked!')

updater.start_polling()
updater.idle()
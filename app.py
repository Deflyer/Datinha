import json
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackContext, CallbackQueryHandler
import sys
import os
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import kaggle
from kaggle.rest import ApiException
from kaggle.api.kaggle_api_extended import KaggleApi

PAGE_SIZE = 5
competitions = []  # Armazena todas as competições
competitions_kaggle = [] 
# Accessing Kaggle API.
api = KaggleApi()
api.authenticate()
print('Kaggle API accessed!')
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
    Webscrap https://mlcontests.com/#list to get a list of current competitions.
    '''
    chrome_driver_path = '/usr/lib/chromium-browser/chromedriver'
    chrome_bin_path = '/usr/bin/chromium-browser'

    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.binary_location = chrome_bin_path

    service = Service(executable_path=chrome_driver_path)
    driver = webdriver.Chrome(service=service, options=chrome_options)

    url = 'https://mlcontests.com'
    driver.get(url)
    driver.implicitly_wait(2)
    html = driver.page_source

    soup = BeautifulSoup(html, 'html.parser')
    contests_div = soup.find(id='contests-cards')
    competitions = contests_div.find_all(class_='card')

    competition_list = []
    for competition in competitions:
        card_body = competition.find(class_='card-body')
        card_footer = competition.find(class_='card-footer')

        title = card_body.find(class_='card-title').get_text(strip=True)
        prize = card_body.find(class_='card-subtitle').get_text(strip=True)
        organizers = card_body.find(class_='card-text').get_text(strip=True)
        link = card_body.find(class_='btn-link')['href']

        category = card_footer.find('span').get_text(strip=True)
        deadline = card_footer.find(class_='text-muted').get_text(strip=True)
        palavras = deadline.split()
        deadline = int(palavras[1])

        competition_list.append({
            'title': title,
            'prize': prize,
            'organizers': organizers,
            'link': link,
            'category': category,
            'deadline': deadline
        })
    competition_list.sort(key=lambda x: x['deadline'])

    driver.quit()

    return competition_list
def get_competitions_kaggle(group = "general", category = "all", sort_by="latestDeadline", page = 1, search=''):
    '''
    Uses the Kaggle API to get a list of current competitions.
    '''

    try:
        return api.competitions_list()
    except ApiException as e:
        print("Exception when calling KaggleApi->competitions_list: %s\n" % e)

# Função para exibir competições
def kaggle_func(update: Update, context: CallbackContext):
    if not update.callback_query:
        # Se foi chamada via comando, zera a página
        context.user_data['current_page_k'] = 0
    competitions_kaggle = get_competitions_kaggle()

    # Pega a página atual ou inicializa
    current_page = context.user_data.get('current_page_k', 0)
    print(current_page)

    # Limita o current page para não sair dos limites
    tam_comp = len(competitions_kaggle)
    if current_page > tam_comp / PAGE_SIZE:
        current_page = tam_comp / PAGE_SIZE
        context.user_data['current_page_k'] = current_page

    if current_page < 0:
        current_page = 0
        context.user_data['current_page_k'] = 0
    start_index = current_page * PAGE_SIZE
    end_index = min(start_index + PAGE_SIZE, tam_comp)
    
    message = ''
    for c in competitions_kaggle[start_index:end_index]:
            message += 'Title: ' + c.title + '\nDescription: ' + c.description + '\nCategory: ' + c.category + '\nReward: ' + c.reward
            message += '\nMax Team Size: ' + str(c.maxTeamSize) + '\nDeadline: ' + str(c.deadline) + '\n' + c.url
            message += '\n----------------------------------------------------\n\n'

    
    
    keyboard = []
    if start_index > 0:
        keyboard.append([InlineKeyboardButton("⬅️ Previous", callback_data=f'kaggle_prev_{current_page}')])
    if end_index < len(competitions_kaggle):
        keyboard.append([InlineKeyboardButton("➡️ Next", callback_data=f'kaggle_next_{current_page}')])
    
    reply_markup = InlineKeyboardMarkup(keyboard)

    if update.callback_query:
        update.callback_query.message.edit_text(message, disable_web_page_preview=True, reply_markup=reply_markup)
    else:
        update.message.reply_text(message, disable_web_page_preview=True, reply_markup=reply_markup)


def create_competition_print_all(c):
    '''
    Formats a string with the competition information. Used to get a more beautiful Telegram message.
    '''
    
    response = 'Title: ' + c['title'] + '\nOrganizers: ' + c['organizers'] + '\nCategory: ' + c['category'] + '\nReward: ' + c['prize']
    response += '\nDeadline: ' + str(c['deadline']) + 'days\n' + c['link']
        
    return response

def send_competitions(update: Update, context: CallbackContext):
    if not update.callback_query:
        # Se foi chamada via comando, zera a página
        context.user_data['current_page_a'] = 0
    current_page = context.user_data.get('current_page_a', 0)
    start_index = current_page * PAGE_SIZE

    competitions = get_competitions()

    # Limita o current page para não sair dos limites
    tam_comp = len(competitions)
    if current_page > tam_comp / PAGE_SIZE:
        current_page = tam_comp / PAGE_SIZE
        context.user_data['current_page_a'] = current_page

    if current_page < 0:
        current_page = 0
        context.user_data['current_page_a'] = 0

    end_index = min(start_index + PAGE_SIZE, len(competitions))
    
    message = ''
    for comp in competitions[start_index:end_index]:
        message += create_competition_print_all(comp) + '\n'
        message += '----------------------------------------------------\n\n'
    
    keyboard = []
    if start_index > 0:
        keyboard.append([InlineKeyboardButton("⬅️ Previous", callback_data=f'all_prev_{current_page}')])
    if end_index < len(competitions):
        keyboard.append([InlineKeyboardButton("➡️ Next", callback_data=f'all_next_{current_page}')])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    if update.callback_query:
        update.callback_query.message.edit_text(message, disable_web_page_preview=True, reply_markup=reply_markup)
    else:
        update.message.reply_text(message, disable_web_page_preview=True, reply_markup=reply_markup)

def upcoming(update: Update, context: CallbackContext):
    '''
    Telegram command to list all upcoming Kaggle competitions with pagination.
    '''
    global competitions
    competitions = get_competitions()

    send_competitions(update, context)

# Função para lidar com a navegação
def button(update: Update, context: CallbackContext):
    query = update.callback_query

    # Armazenar o tempo da última interação do usuário
    last_interaction = context.user_data.get('last_interaction', 0)
    print(last_interaction)
    current_time = time.time()

    # Define um cooldown de 1 segundo
    cooldown = 1  
    if current_time - last_interaction < cooldown:
        query.answer(text="Aguarde um momento antes de tentar novamente.")
        return
    context.user_data['last_interaction'] = current_time

    data = query.data.split('_')
    print(data)
    type = data[0]
    direction = data[1]
    current_page = int(data[2])

    # Atualiza a página
    if type == "all":
        if direction == 'prev':
            current_page = max(current_page - 1, 0)
        elif direction == 'next':
            current_page += 1  # Apenas incrementa aqui
    
        context.user_data['current_page_a'] = current_page

        # Envia as competições da nova página
        send_competitions(update, context)
    if type == "kaggle":
        if direction == 'prev':
            current_page = max(current_page - 1, 0)
        elif direction == 'next':
            current_page += 1  # Apenas incrementa aqui
    
        context.user_data['current_page_k'] = current_page

        # Envia as competições da nova página
        kaggle_func(update, context)

    query.answer()

# Configuração do bot
def main():
    # Loading configuration file to get the key of our Telegram bot.
    with open('config.json', 'r') as config_file:
        config = json.load(config_file)
        TOKEN = config['key']

    # Linking this code to our Telegram bot.
    updater = Updater(TOKEN)
    dp = updater.dispatcher
    print('Bot linked!')
    dp.add_handler(CallbackQueryHandler(button))

    # Adding commands to the bot.
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", help))
    dp.add_handler(CommandHandler("kaggle", kaggle_func))
    dp.add_handler(CommandHandler("upcoming", upcoming))
    dp.add_handler(CallbackQueryHandler(button))
    print('Functionalities linked!')

    updater.start_polling()
    updater.idle()
    
if __name__ == '__main__':
    main()
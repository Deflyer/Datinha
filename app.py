import json
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackContext
import sys
import os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup

PAGE_SIZE = 5
competitions = []  # Armazena todas as competições
current_page = 0  # Página atual

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
    # Configurar o ambiente para o Selenium
    chrome_driver_path = '/usr/lib/chromium-browser/chromedriver'
    chrome_bin_path = '/usr/bin/chromium-browser'

    # Configurar o Selenium para usar o Chrome
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.binary_location = chrome_bin_path

    # Iniciar o WebDriver
    service = Service(executable_path=chrome_driver_path)
    driver = webdriver.Chrome(service=service, options=chrome_options)

    # Navegar para a URL
    url = 'https://mlcontests.com'
    driver.get(url)

    # Esperar que os elementos sejam carregados (ajuste o tempo se necessário)
    driver.implicitly_wait(2)

    # Obtém o HTML da página
    html = driver.page_source

    # Cria o objeto BeautifulSoup com o HTML obtido
    soup = BeautifulSoup(html, 'html.parser')

    # Encontrar o elemento que contém as competições
    contests_div = soup.find(id='contests-cards')

    # Encontrar todas as competições dentro de contests_div
    competitions = contests_div.find_all(class_='card')

    competition_list = []
    # Extrair informações de cada competição
    for competition in competitions:
        card_body = competition.find(class_='card-body')
        card_footer = competition.find(class_='card-footer')

        # Extrair o título, prêmio, organizadores e link
        title = card_body.find(class_='card-title').get_text(strip=True)
        prize = card_body.find(class_='card-subtitle').get_text(strip=True)
        organizers = card_body.find(class_='card-text').get_text(strip=True)
        link = card_body.find(class_='btn-link')['href']

        # Extrair a categoria e o prazo
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
    # Ordenar a lista pela deadline
    competition_list.sort(key=lambda x: x['deadline'])

    # Fechar o WebDriver
    driver.quit()

    return competition_list

def create_competition_print_kaggle(c, n_comp, total_comp):
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
        response += create_competition_print_kaggle(comp, i, number_comp)

    update.message.reply_text(response, disable_web_page_preview=True)

def create_competition_print_all(c):
    '''
    Formats a string with the competition information. Used to get a more beautiful Telegram message.
    '''
    
    response = 'Title: ' + c['title'] + '\nOrganizers: ' + c['organizers'] + '\nCategory: ' + c['category'] + '\nReward: ' + c['prize']
    response += '\nDeadline: ' + str(c['deadline']) + 'days\n' + c['link']
        
    return response

def send_competitions(update: Update, page: int):
    global competitions
    start_index = page * PAGE_SIZE
    end_index = min(start_index + PAGE_SIZE, len(competitions))
    print('hora de pegar')
    competitions = get_competitions()
    print('de alguma forma passei')
    
    message = ''
    for comp in competitions[start_index:end_index]:
        print(comp)
        message += create_competition_print_all(comp) + '\n\n'
    
    message += '----------------------------------------------------\n\n'
    keyboard = []
    print('ue, sai')
    if start_index > 0:
        keyboard.append([InlineKeyboardButton("⬅️ Previous", callback_data=f'prev_{page}')])
    if end_index < len(competitions):
        keyboard.append([InlineKeyboardButton("➡️ Next", callback_data=f'next_{page}')])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text(message, disable_web_page_preview=True, reply_markup=reply_markup)
    #update.message.reply_text(message, parse_mode='Markdown', reply_markup=reply_markup)

def upcoming(update: Update, context: CallbackContext):
    '''
    Telegram command to list all upcoming Kaggle competitions with pagination.
    '''
    global competitions, current_page
    competitions = get_competitions()
    current_page = 0

    send_competitions(update, current_page)

def button(update: Update, context: CallbackContext):
    '''
    Navigate through the competitions with emotes buttons peguei do chat, nao funciona ainda
    '''
    global current_page
    query = update.callback_query
    query.answer()
    
    data = query.data.split('_')
    direction = data[0]
    page = int(data[1])
    
    if direction == 'prev':
        current_page = max(page - 1, 0)
    elif direction == 'next':
        current_page = min(page + 1, len(competitions) // PAGE_SIZE)
    
    send_competitions(update, current_page)

# Loading configuration file to get the key of our Telegram bot.
with open('config.json', 'r') as config_file:
    config = json.load(config_file)
    TOKEN = config['key']

# Linking this code to our Telegram bot.
updater = Updater(TOKEN)
dp = updater.dispatcher
print('Bot linked!')

# Accessing Kaggle API.

print('Kaggle API accessed!')

# Adding commands to the bot.
dp.add_handler(CommandHandler("start", start))
dp.add_handler(CommandHandler("help", help))
dp.add_handler(CommandHandler("kaggle", kaggle))
dp.add_handler(CommandHandler("upcoming", upcoming))
print('Functionalities linked!')

updater.start_polling()
updater.idle()
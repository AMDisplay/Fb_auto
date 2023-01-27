import logging
import csv
from telegram import Bot
from telegram.ext import Updater


API_TOKEN = "5873293011:AAF5wTCYfL-4W24drzARmSohNFn8ZlWF3tA"
updater = Updater(token='<token>') 
bot = Bot(token=API_TOKEN)

chat_id = <me>
text = 'Вам телеграмма!'
# Отправка сообщения
bot.send_message(chat_id, text) 
# бот не работает

import config
import gspread
import re
from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.utils import executor
from telethon.sync import TelegramClient
from telethon import connection
from telethon.tl.functions.messages import GetHistoryRequest

gs = gspread.service_account(filename='google_key.json')  # подключаем файл с ключами и пр.
sh = gs.open_by_key(config.google_base_id)  # подключаем таблицу по ID
worksheet = sh.sheet1  # получаем первый лист

bot = Bot(token=config.bot_token)
dp = Dispatcher(bot)

post_id = ''
url = ''
# client = TelegramClient(config.username, config.api_id, config.api_hash)
# client.start()

@dp.message_handler(commands=['start'])
async def start(msg: types.Message):
    await msg.reply_to_message('Авторизация успешна! Чтобы добавить пост, введи команду /add')

@dp.message_handler(commands=['add'])
async def add(msg: types.Message):
    await msg.reply_to_message('Введите ссылку на пост')


@dp.message_handler(content_types=['text'])
async def get_text_messages(msg: types.Message):
    if re.fullmatch(r'^https://t\.me/.+/.+$', msg.text):
        input_url = msg.text
        if add_post(input_url):
            await msg.answer("Пост уже отслеживается.")
        else:
            await msg.answer("Пост успешно добавлен к отслеживанию. Собираю комментарии...")
    else:
        await msg.answer("Я тебя не понимаю. Напиши /start.")

def add_post(input_url):
    global post_id, url
    post_id_to_compare = input_url.split('/')[-1]
    post_id = int(post_id_to_compare)           # возвращает номер поста в канале
    url = input_url.split('/')
    del url[-1]
    url = '/'.join(url) + '/'
    was_added = False
    newRec = [url, post_id_to_compare]
    oldRec = worksheet.get_all_values()
    for i in range(len(oldRec)):                # проверяет пост на наличие в базе
        if newRec[0] == oldRec[i][0] and newRec[1] == oldRec[i][1]:
            was_added = True
            break
    if not was_added:
        worksheet.append_row(newRec)
    return was_added


executor.start_polling(dp)

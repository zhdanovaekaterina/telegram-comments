import telebot
from telebot import types
import config
import gspread
import re

gs = gspread.service_account(filename='google_key.json')     # подключаем файл с ключами и пр.
sh = gs.open_by_key(config.google_sheet)                     # подключаем таблицу по ID
worksheet = sh.sheet1                                        # получаем первый лист

bot = telebot.TeleBot(config.bot_token)
bot.delete_webhook()

post_id = ''
url = ''

@bot.message_handler(commands=['start'])
def start_command(message):
    bot.send_message(message.chat.id, 'Чтобы посмотреть список доступных команд, нажмите /help. Чтобы добавить пост к отслеживанию, пришлите ссылку.')


@bot.message_handler(commands=['help'])
def help_command(message):
    markup_inline = types.InlineKeyboardMarkup()                                # клавиатура со списком доступных команд
    button1 = types.InlineKeyboardButton(text='Добавить пост', callback_data = '/add')
    button2 = types.InlineKeyboardButton(text='Список постов', callback_data = '/posts')
    button3 = types.InlineKeyboardButton(text='Архив', callback_data = '/removed')
    markup_inline.add(button1, button2, button3)
    bot.send_message(message.chat.id, 'Вот что вы можете сделать:', reply_markup=markup_inline)


# Обработчик инлайн-кнопок
@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    if call.data == '/add':                                                     # вызов команды /add
        bot.answer_callback_query(call.id)
        bot.send_message(call.from_user.id, 'Введите ссылку на пост')
    elif call.data == "/posts":
        bot.answer_callback_query(call.id)
        list_of_posts(call)
    elif call.data == "/removed":
        bot.answer_callback_query(call.id)
        bot.send_message(call.from_user.id, "Вы запросили архив; к сожалению, этот функционал еще не реализован.")
    elif call.data == "/no":
        bot.answer_callback_query(call.id)
        bot.send_message(call.from_user.id, "Хорошо, если передумаете, просто пришлите мне ссылку.")
    elif call.data == '/post':
        bot.answer_callback_query(call.id)
        bot.send_message(call.from_user.id, "Вы нажали на пост; детальная информация по посту еще недоступна.")


@bot.message_handler(commands=['add'])
def add_command(message):
    bot.send_message(message.from_user.id, 'Введите ссылку на пост')


# TODO: Прописать ввод названия поста перед добавлением в базу
@bot.message_handler(content_types=['text'])
def get_text_messages(message):
    if re.fullmatch(r'^https://t\.me/.+/.+$', message.text):
        input_url = message.text
        if add_post(input_url):
            markup_inline = types.InlineKeyboardMarkup()
            button4 = types.InlineKeyboardButton(text='Да', callback_data = '/add')
            button5 = types.InlineKeyboardButton(text='Нет', callback_data = '/no')
            markup_inline.add(button4, button5)
            bot.send_message(message.chat.id, "Пост уже отслеживается. Хотите добавить другой пост?", reply_markup=markup_inline)
        else:
            bot.send_message(message.from_user.id, "Пост успешно добавлен к отслеживанию.")
    else:
        bot.send_message(message.from_user.id, "Похоже, это не ссылка на пост в телеграм. Попробуйте еще раз.")


def add_post(input_url):
    global post_id, url
    post_id_to_compare = input_url.split('/')[-1]
    channel = input_url.split('/')[-2]					# возвращает название канала
    post_id = int(post_id_to_compare)                   # возвращает номер поста в канале
    was_added = False
    newRec = [channel, post_id_to_compare]
    oldRec = worksheet.get_all_values()
    for i in range(len(oldRec)):                        # проверяет пост на наличие в базе
        if newRec[0] == oldRec[i][0] and newRec[1] == oldRec[i][1]:
            was_added = True
            return was_added
    if not was_added:
        worksheet.append_row(newRec)
        return was_added


def list_of_posts(call):
    all_posts = worksheet.get_all_values()
    for i in range(len(all_posts)):
        del all_posts[i][2]
    markup_inline = types.InlineKeyboardMarkup()
    for i in range(1, len(all_posts)):
        button = types.InlineKeyboardButton(text=f'{all_posts[i][0]}/{all_posts[i][1]}', callback_data = '/post')
        markup_inline.add(button)
    bot.send_message(call.from_user.id, "Ниже вы найдете список отслеживаемых постов.", reply_markup=markup_inline)


bot.polling()

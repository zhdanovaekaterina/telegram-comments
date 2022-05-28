import telebot
from telebot import types
from zmq import NULL
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
        bot.send_message(call.from_user.id, 'Введите название поста в кавычках (рекомендуется не длиннее 30 символов). Пожалуйста, не используйте в названии символ '/'.')
        bot.answer_callback_query(call.id)
    elif call.data == "/posts":
        list_of_posts(call)
        bot.answer_callback_query(call.id)
    elif call.data == "/removed":
        bot.send_message(call.from_user.id, "Вы запросили архив; к сожалению, этот функционал еще не реализован.")
        bot.answer_callback_query(call.id)
    elif call.data == "/no":
        bot.send_message(call.from_user.id, "Хорошо, если передумаете, просто пришлите мне название поста.")
        bot.answer_callback_query(call.id)
    elif re.fullmatch(r'^\/post\/.*', call.data):
        post_name = call.data[8:]
        post_row = int(call.data.split('/')[-2]) + 1
        post_data = worksheet.row_values(post_row)
        markup_inline = types.InlineKeyboardMarkup()
        button = types.InlineKeyboardButton(text='Перейти к посту', url = f'https://t.me/{post_data[0]}/{post_data[1]}')
        markup_inline.add(button)
        bot.send_message(call.from_user.id, f'Пост: {post_name}\nКанал: {post_data[0]}\nКомментариев: {post_data[2]}', reply_markup=markup_inline)
        bot.answer_callback_query(call.id)


@bot.message_handler(commands=['add'])
def add_command(message):
    bot.send_message(message.from_user.id, 'Введите название поста в кавычках (рекомендуется не длиннее 30 символов). Пожалуйста, не используйте в названии символ '/'.')


# TODO: Прописать ввод названия поста перед добавлением в базу
@bot.message_handler(content_types=['text'])
def get_text_messages(message):
    global input_name
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
    elif message.text[0] == '"':
        input_name = message.text[1:-2]
        bot.send_message(message.from_user.id, 'Введите ссылку на пост')
    else:
        markup_inline = types.InlineKeyboardMarkup()
        button6 = types.InlineKeyboardButton(text='Написать разработчику', url = 'https://t.me/zhdanovakaterina')
        markup_inline.add(button6)
        bot.send_message(message.chat.id, 'Вы ввели какой-то текст. К сожалению, я еще не такой умный, чтобы вас понять. Если у вас есть пожелания по функционалу или вопросы по моей работе, пожалуйста, напишите моему разработчику', reply_markup=markup_inline)


def add_post(input_url):
    # global post_id, url
    global input_name
    post_id_to_compare = input_url.split('/')[-1]
    channel = input_url.split('/')[-2]					# возвращает название канала
    post_id = int(post_id_to_compare)                   # возвращает номер поста в канале
    was_added = False
    newRec = [channel, post_id_to_compare, 'еще не собраны', 0, input_name]
    oldRec = worksheet.get_all_values()
    for i in range(len(oldRec)):                        # проверяет пост на наличие в базе
        if newRec[0] == oldRec[i][0] and newRec[1] == oldRec[i][1]:
            was_added = True
            return was_added
    if not was_added:
        worksheet.append_row(newRec)
        input_name = NULL
        return was_added


def list_of_posts(call):
    all_posts = worksheet.get_all_values()
    markup_inline = types.InlineKeyboardMarkup()
    for i in range(1, len(all_posts)):
        button = types.InlineKeyboardButton(text=f'{all_posts[i][4]} ({all_posts[i][2]})', callback_data = f'/post/{i}/{all_posts[i][4]}')
        markup_inline.add(button)
    bot.send_message(call.from_user.id, "Ниже вы найдете список отслеживаемых постов.", reply_markup=markup_inline)


bot.polling()

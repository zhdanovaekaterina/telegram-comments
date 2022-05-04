import telebot
import config
import gspread
import re

gs = gspread.service_account(filename='google_key.json')  # подключаем файл с ключами и пр.
sh = gs.open_by_key(config.google_base_id)  # подключаем таблицу по ID
worksheet = sh.sheet1  # получаем первый лист

bot = telebot.TeleBot(config.bot_token)
bot.delete_webhook()

post_id = ''
url = ''

@bot.message_handler(content_types=['text'])
def get_text_messages(message):
    if message.text == "/start":
        bot.send_message(message.from_user.id, 'Введите ссылку на пост')
    elif re.fullmatch(r'^https://t\.me/.+/.+$', message.text):
        input_url = message.text
        if add_post(input_url):
            bot.send_message(message.from_user.id, "Пост уже отслеживается.")
        else:
            bot.send_message(message.from_user.id, "Пост успешно добавлен к отслеживанию. Собираю комментарии...")
    else:
        bot.send_message(message.from_user.id, "Я тебя не понимаю. Напиши /start.")

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
    print(oldRec)
    for i in range(len(oldRec)):                # проверяет пост на наличие в базе
        if newRec[0] == oldRec[i][0] and newRec[1] == oldRec[i][1]:
            was_added = True
            break
    if not was_added:
        worksheet.append_row(newRec)
    return was_added


bot.polling()

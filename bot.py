import telebot
import config
import gspread

gs = gspread.service_account(filename='google_key.json')  # подключаем файл с ключами и пр.
sh = gs.open_by_key('1oLDTAczDRTUj7s2njIdkapOYoVEs4aw18G9ci2x9UC8')  # подключаем таблицу по ID
worksheet = sh.sheet1  # получаем первый лист

bot = telebot.TeleBot(config.bot_token)
bot.delete_webhook()

post_id = ''
url = ''

@bot.message_handler(content_types=['text'])
def get_text_messages(message):
    if message.text == "/start":
        bot.send_message(message.from_user.id, 'Введите ссылку на пост')
    elif message.text != ' ':
        input_url = message.text
        global post_id, url
        post_id = int(input_url.split('/')[-1])		# возвращает номер поста в канале
        url = input_url.split('/')
        del url[-1]
        url = '/'.join(url) + '/'
        newRec = [url, post_id]
        worksheet.append_row(newRec)
        bot.send_message(message.from_user.id, "Пост успешно добавлен к отслеживанию. Собираю комментарии...")
        
    else:
        bot.send_message(message.from_user.id, "Я тебя не понимаю. Напиши /start.")


bot.polling()

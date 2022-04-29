import config, dump_mess
import telethon
import json
import pprint
from datetime import date, datetime
from telethon.sync import TelegramClient
from telethon import connection
from telethon.tl.functions.messages import GetHistoryRequest

# with open(r"channel_messages.json", 'r') as f:
#     json_data = json.load(f)
    
# pprint.pprint(json_data)

client = TelegramClient(config.username, config.api_id, config.api_hash)
client.start()

data_json = open("channel_messages.json", encoding='cp1251')

data = json.load(data_json)

# Создаем словарь, в который кладем ID поста и кол-во комментариев к нему. Данные заносятся, если кол-во комментариев >0 и ID поста совпадает

data_id = {}
for i in range(len(data)):
    if data[i]['id'] == dump_mess.post_id:
        var1 = data[i]['id']
        try:
            var2 = data[i]['replies']['replies']
        except TypeError:
            pass
        data_id[var1] = var2

# Выводим сообщение с указанием времени отправки, отправителя и текст

def data_data():
    for i, v in data_id.items():
        if v > 0:
            try:
                for message in client.iter_messages('frontendlab', reply_to=i, reverse=True):
                    if isinstance(message.sender, telethon.tl.types.User):
                        print(message.date, message.sender.first_name, ':', message.text)
            except:
                print(i, v)


data_data()

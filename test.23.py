import telethon
import json
from datetime import date, datetime
from telethon.sync import TelegramClient
from telethon import connection
from telethon.tl.functions.messages import GetHistoryRequest


data_json = open("channel_messages.json", encoding='cp1251')

data = json.load(data_json)

data_id = {}
for i in range(len(data)):
    var1 = data[i]['id']
    try:
        var2 = data[i]['replies']['replies']
    except TypeError:
        pass
    data_id[var1] = var2

def data_data():
    for i, v in data_id.items():
        if v > 0:
            print(f"https://t.me/frontendlab/{i}")
            try:
                for message in client.iter_messages('frontendlab', reply_to=i, reverse=True):
                    if isinstance(message.sender, telethon.tl.types.User):
                        print(message.date, message.sender.first_name, ':', message.text)
            except:
                print(i, v)


data_data()





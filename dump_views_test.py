# import block
import config
import json
from datetime import date, datetime
from telethon.sync import TelegramClient
from telethon import connection
from telethon.tl.functions.messages import GetMessagesViewsRequest

client = TelegramClient(config.username, config.api_id, config.api_hash)
client.start()

async def dump_all_messages(channel):
	"""Записывает json-файл с информацией о всех сообщениях канала/чата"""
	offset_msg = 0    # номер записи, с которой начинается считывание
	limit_msg = 100   # максимальное число записей, передаваемых за один раз

	all_messages = []   # список всех сообщений
	total_messages = 0
	total_count_limit = 0  # поменяйте это значение, если вам нужны не все сообщения

	class DateTimeEncoder(json.JSONEncoder):
		'''Класс для сериализации записи дат в JSON'''
		def default(self, o):
			if isinstance(o, datetime):
				return o.isoformat()
			if isinstance(o, bytes):
				return list(o)
			return json.JSONEncoder.default(self, o)

	history = await client(GetMessagesViewsRequest(
        peer=channel,
        id=[78],
        increment=True))

	with open('channel_messages.json', 'w', encoding='utf8') as outfile:
		 json.dump(history, outfile, ensure_ascii=False, cls=DateTimeEncoder)


async def main():
	url = input("Введите ссылку на канал или чат: ")
	channel = await client.get_entity(url)
	await dump_all_messages(channel)


with client:
	client.loop.run_until_complete(main())
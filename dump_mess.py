# import block
from distutils import dist
from requests import post
import config
import json
from datetime import date, datetime
from telethon.sync import TelegramClient
from telethon import connection
from telethon.tl.functions.messages import GetHistoryRequest

client = TelegramClient(config.username, config.api_id, config.api_hash)
client.start()

async def dump_all_messages(channel):
	"""Записывает json-файл с информацией о всех сообщениях канала/чата"""
	offset_msg = 0
	limit_msg = 100  					 # максимальное число записей, передаваемых за один раз

	all_messages = []  					 # список всех сообщений
	total_messages = 0
	total_count_limit = 0  			     # поменяйте это значение, если вам нужны не все сообщения
	
	class DateTimeEncoder(json.JSONEncoder):
		'''Класс для сериализации записи дат в JSON'''
		def default(self, o):
			if isinstance(o, datetime):
				return o.isoformat()
			if isinstance(o, bytes):
				return list(o)
			return json.JSONEncoder.default(self, o)

	while True:
		history = await client(GetHistoryRequest(
			peer=channel,
			offset_id = offset_msg,
			offset_date = None, add_offset=0,
			limit=limit_msg, max_id=0, min_id=0,
			hash=0))
		if not history.messages:
			break
		messages = history.messages
		for message in messages:
			all_messages.append(message.to_dict())
		offset_msg = messages[len(messages) - 1].id
		total_messages = len(all_messages)
		if total_count_limit != 0 and total_messages >= total_count_limit:
			break

	with open('channel_messages.json', 'w', encoding='utf8') as outfile:
		 json.dump(all_messages, outfile, ensure_ascii=False, cls=DateTimeEncoder)

def input_url():
	'''Принимает ссылку на пост и извлекает из нее ссылку на канал и номер поста'''
	global post_id, url
	post_input = input("Введите ссылку на пост: ")
	post_id = int(post_input.split('/')[-1])			# возвращает номер поста в канале
	url = post_input.split('/')
	del url[-1]
	url = '/'.join(url) + '/'							# возвращает ссылку на канал


async def main():
	input_url()
	channel = await client.get_entity(url)
	await dump_all_messages(channel)
	print('Done!')


with client:
	client.loop.run_until_complete(main())

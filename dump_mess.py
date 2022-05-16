from distutils import dist
from requests import post
import config
import json
import telethon
from datetime import date, datetime
from telethon.sync import TelegramClient
from telethon import connection
from telethon.tl.functions.messages import GetHistoryRequest
import gspread

client = TelegramClient(config.username, config.api_id, config.api_hash)
client.start()

gs = gspread.service_account(filename='google_key.json')     # подключаем файл с ключами и пр.
sh = gs.open_by_key(config.google_sheet)                     # подключаем таблицу по ID
worksheet = sh.sheet1                                        # получаем первый лист


async def dump_all_messages(channel:str, post_id:int):
	'''Принимает название канала и id поста. Записывает в Google таблицу комментарии.'''
	async for message in client.iter_messages(channel, reply_to=post_id, reverse=True):
		if isinstance(message.sender, telethon.tl.types.User):
			mess_date = message.date.isoformat()
			newRec = [channel, post_id, mess_date, message.sender.first_name, message.text]
			print(newRec)
			# worksheet.append_row(newRec)


def input_url(worksheet):
	'''Принимает ссылку на лист в Google таблицах. Возвращает список списков.'''
	all_posts = worksheet.get_all_values()
	for i in range(1, len(all_posts)):
		all_posts[i][1] = int(all_posts[i][1])
	return all_posts
	

async def main():
	params = input_url(worksheet)
	for i in range(1, len(params)):
		await dump_all_messages(*params[i])


with client:
	client.loop.run_until_complete(main())
	
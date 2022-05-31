from distutils import dist
from hashlib import new
from operator import ne
from requests import post
import config
import json
import telethon
from datetime import date, datetime
from telethon.sync import TelegramClient
from telethon import connection
from telethon.tl.functions.messages import GetHistoryRequest
import gspread
import time
from telethon import functions

start_time = time.time()

client = TelegramClient(config.username, config.api_id, config.api_hash)
client.start()

gs = gspread.service_account(filename='google_key.json')     	# подключаем файл с ключами и пр.
sh = gs.open_by_key(config.google_sheet)                     	# подключаем таблицу по ID
worksheet1 = sh.sheet1                                       	# получаем первый лист
worksheet2 = sh.worksheet(config.sheet_2)					 	# получаем второй лист


async def dump_comments(channel:str, post_id:int):
	'''Принимает название канала и id поста. Возвращает количество комментариев к посту.'''
	k = 0
	async for message in client.iter_messages(channel, reply_to=post_id, reverse=True):
		if isinstance(message.sender, telethon.tl.types.User):
			mess_date = message.date.isoformat()
			message_toRec = message.text[:30] + '...'
			newRec = [channel, str(post_id), mess_date, message.sender.first_name, message_toRec]
			oldRec = worksheet2.get_all_values()				# проверяет комментарий на наличие в базе
			points_max = 0
			for i in range(len(oldRec)):
				points = 0
				for v in range(len(oldRec[i])):
					if newRec[v] == oldRec[i][v]:
						points += 1
				if points > points_max:
					points_max = points
			if points_max != len(newRec):
				worksheet2.append_row(newRec)
		k += 1
	current_comments = k
	return current_comments


# TODO: разобраться, как вытащить из объекта корутины значение
async def dump_views(channel:str, post_id:int):
	'''Принимает название канала и id поста. Возвращает количество просмотров поста.'''
	views = client(functions.messages.GetMessagesViewsRequest(
        peer = channel,
        id = [post_id],
        increment = False))
	# all_views = json.dumps(views)
	# print(all_views)
	# return views

				
def comments_count_update(comments: list, worksheet):
	'''Обновляет данные о посте в google таблицах. Пока что обновляет только кол-во комментариев.'''
	for i in range(len(comments)):
		worksheet.update_cell((i + 2), 3, comments[i])


# TODO: скорректировать импорт из google sheets так, чтобы загружались только первые два столбца вместо worksheet.get_all_values(). После этого убрать из функции comments_count() удаление лишних значений.
def input_url(worksheet):
	'''Принимает ссылку на лист в Google таблицах. Возвращает список списков каналов и id отслеживаемых постов.'''
	all_posts = worksheet.get_all_values()
	for i in range(1, len(all_posts)):
		all_posts[i][1] = int(all_posts[i][1])
	return all_posts


async def main():
	params = input_url(worksheet1)
	comments_count = []
	for i in range(1, len(params)):
		comments = await dump_comments(params[i][0], params[i][1])
		comments_count.append(comments)
		# await dump_views(params[i][0], params[i][1])
	comments_count_update(comments_count, worksheet1)
	

with client:
	client.loop.run_until_complete(main())

# Замер и вывод времени работы модуля в секундах
end_time = time.time()
total_time = end_time - start_time
print('Total time: ', '%.3f' % total_time, ' s.')

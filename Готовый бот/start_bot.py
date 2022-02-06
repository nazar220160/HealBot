from aiogram.utils import executor
from create_bot import dp
from handlers import client, admin, other, qiwi, translate
from data_base import sqlite_db
import logging

async def on_startup(_):
	logging.basicConfig(
		format=u'#%(levelname)-8s [%(asctime)s] %(message)s',
		level=logging.INFO)
	print('Бот вышел в онлайн')
	sqlite_db.sql_start()


client.register_handlers_client(dp)
qiwi.register_handlers_qiwi(dp)
translate.register_handlers_translate(dp)
admin.register_handlers_admin(dp)
other.register_handlers_other(dp)



executor.start_polling(dp, skip_updates=True, on_startup=on_startup)
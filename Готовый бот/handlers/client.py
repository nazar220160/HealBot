from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.types import ReplyKeyboardRemove
from data_base import sqlite_db
from keyboards import kb_client



async def command_start(message: types.Message, state: FSMContext):
	await bot_set_commands()
	global people_id
	global token
	people_id = message.from_user.id
	token = sqlite_db.cursor.execute('SELECT api FROM database WHERE id == ?', (people_id,)).fetchone()
	try:
		await sqlite_db.sql_add_command(state)
		if sqlite_db.data is None:
			await message.answer(f'Привет <b><a href="t.me/{message.from_user.username}">{message.from_user.first_name}</a></b>, новая регистрация!\n'
						f'Чтобы посмотреть все функции напиши <i>/help</i>', reply_markup=kb_client, parse_mode="HTML", disable_web_page_preview=True)
		else:
			await message.answer(f'Привет <b><a href="t.me/{message.from_user.username}">{message.from_user.first_name}</a></b>, вы уже были зарегистрированы!\n'
						f'Чтобы посмотреть все функции напиши <i>/help</i>', reply_markup=kb_client, parse_mode="HTML", disable_web_page_preview=True)
	except:
		await message.reply('Неудача', reply_markup=ReplyKeyboardRemove())



# устанавливаем команды бота
async def bot_set_commands():
	commands_ru = [  # команды с описанием на русском языке
		types.BotCommand("start", "Перезапустить бота"),
		types.BotCommand("translate", "Режим перевода текста"),
	]
	commands_en = [  # команды с описанием на английском языке
		types.BotCommand("start", "Restart the bot"),
		types.BotCommand("translate", "Change the translation language"),
	]
	#await dp.bot.set_my_commands(commands_ru, language_code='ru')  # language_code='ru' устанавливает описание команд на русском языке, пользователям у кого язык стемы указан русский
	#await dp.bot.set_my_commands(commands_en)  # для всех других языков, описание на английском




#Выход из состояния
async def cancel_handler(message: types.Message, state: FSMContext):
	current_state = await state.get_state()
	if current_state is None:
		return
	await state.finish()
	await message.reply('OK', reply_markup=kb_client)




def register_handlers_client(dp : Dispatcher):
	dp.register_message_handler(command_start, commands=['start', 'help'])
	dp.register_message_handler(cancel_handler, state="*", text=['В главное меню', '/start'])
	dp.register_message_handler(cancel_handler, Text(equals='В главное меню', ignore_case=True), state="*")


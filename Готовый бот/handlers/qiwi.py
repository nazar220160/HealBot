import re
from SimpleQIWI import *
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
import config
from create_bot import dp
from data_base import sqlite_db
from keyboards import kb_qiwi, qiwi_api, qiwi_number_i, qiwi_number_api
from aiogram import Dispatcher, types
from filters import MyFilter
import asyncio

dp.filters_factory.bind(MyFilter)
on_payments = False

async def start_qiwi(message: types.Message, state: FSMContext):
	await state.set_state('qiwi_on')
	await message.answer('Вы авторизовались в киви панель', reply_markup=kb_qiwi)


# noinspection PyTypeChecker
async def start_qiwi_push(message: types.Message):
	global people_id
	global token
	people_id = message.from_user.id
	token = sqlite_db.cursor.execute('SELECT api FROM database WHERE id == ?', (people_id,)).fetchone()
	phone2 = sqlite_db.cursor.execute('SELECT number FROM database WHERE id == ?', (people_id,)).fetchone()
	if token[0] != '0' and phone2[0] != '0':
		try:
			if not on_payments:
				await in_payments(message)
			if on_payments:
				if not message.from_user.id in [id[0] for id in on_payments]:
					await in_payments(message)
				# noinspection PyTypeChecker
				if message.from_user.id in [id[0] for id in on_payments]:
					await message.answer('Проверка платежей уже запущена')
		except:
			await message.answer('Проблема с API или номером\n'
								 'Проверьте номер киви и API')
	if token[0] == '0' and phone2[0] != '0':
		await message.answer('У вас нету API добавьте его!', reply_markup=qiwi_api)
	if phone2[0] == '0' and token[0] != '0':
		await message.answer('У вас нету телефона', reply_markup=qiwi_number_i)
	if phone2[0] == '0' and token[0] == '0':
		await message.answer('Вы не добавили номер и API', reply_markup=qiwi_number_api)

class FSMAdmin(StatesGroup):
	number_qiwi = State()
	comment_qiwi = State()
	summ_qiwi = State()

#Начало записи
async def send_money_qiwi(message: types.Message):
		global token
		global people_id
		people_id = message.from_user.id
		token = sqlite_db.cursor.execute('SELECT api FROM database WHERE id == ?', (people_id,)).fetchone()
		phone2 = sqlite_db.cursor.execute('SELECT number FROM database WHERE id == ?', (people_id,)).fetchone()
		api = QApi(token=token[0], phone=phone2)
		try:
			if message.chat.type == 'private':
				people_id = message.from_user.id
				token = sqlite_db.cursor.execute('SELECT api FROM database WHERE id == ?', (people_id,)).fetchone()
				if token[0] != '0':
					print(api.balance)
					await FSMAdmin.number_qiwi.set()
					await message.answer('Напишите номер киви кошелька на который будет перевод!', reply_markup=ReplyKeyboardMarkup(resize_keyboard=True).add(KeyboardButton('Назад')))
				if token[0] == '0':
					await message.answer('Вы не добавили токен', reply_markup=kb_qiwi)
			else:
				await message.answer('Отправлять можно только в личном чате с ботом @ItsHealBot')
		except requests.exceptions.JSONDecodeError:
			await message.answer('Токен не правильный')
		except Errors.QIWIAPIError as e:
			if e.args[0]["errorCode"] == 'request.blocked':
				await message.answer('Ошибка: QIWIAPIError\n'
									 'У вас брокировка API\n'
									 'Вас разблокируют в течении 15 минут', reply_markup=kb_qiwi)
			else:
				await message.answer('Ошибка: QIWIAPIError\n'
									 'Какая-то другая', reply_markup=kb_qiwi)
				print(e)
		except:
			await message.answer('Проблема с токеном', reply_markup=kb_qiwi)

#Ловим ответ 1
async def qiwi_number(message: types.Message, state: FSMContext):
	try:
		pattern = re.compile("^38\d{10}$")
		if pattern.search(message.text):
			async with state.proxy() as data:
				data['number_qiwi'] = message.text
			await FSMAdmin.next()
			await message.reply('Введи комантарий к переводу', reply_markup=ReplyKeyboardMarkup(resize_keyboard=True).add(KeyboardButton('Назад')).add(KeyboardButton('Пропустить')))
		else:
			await message.answer('Номер введен неверно!')
	except:
		await message.answer('Ошибка')


#Ловим ответ 2
async def qiwi_comment(message: types.Message, state: FSMContext):
	async with state.proxy() as data:
		if message.text != 'Пропустить':
			data['comment_qiwi'] = message.text
		if message.text == 'Пропустить':
			data['comment_qiwi'] = ''
	await FSMAdmin.next()
	await message.reply('Введите сумму перевода!', reply_markup=ReplyKeyboardMarkup(resize_keyboard=True).add(KeyboardButton('Назад')))


#Ловим последний ответ и используем данные
async def qiwi_summ(message: types.Message, state: FSMContext):
	token = sqlite_db.cursor.execute('SELECT api FROM database WHERE id == ?', (people_id,)).fetchone()
	api = QApi(token=token[0], phone=config.phone)
	async with state.proxy() as data:
		data['summ_qiwi'] = message.text
	if int(message.text) <= api.balance[0]:
		await paying_qiwi(message, state)
		await state.finish()
		await state.set_state('qiwi_on')
	if int(message.text) >= api.balance[0]:
		await message.answer('Недостаточно средст\n'
							 f'Ваш баланс - {api.balance[0]}')


async def paying_qiwi(message, state):
	await state.set_state('qiwi_on')
	token = sqlite_db.cursor.execute('SELECT api FROM database WHERE id == ?', (people_id,)).fetchone()
	api = QApi(token=token[0], phone=config.phone)
	async with state.proxy() as data:
		global number_qiwi
		global summ_qiwi
		global comment_qiwi
		number_qiwi = data['number_qiwi']
		summ_qiwi = data['summ_qiwi']
		comment_qiwi = data['comment_qiwi']
		try:
			api.pay(account=number_qiwi, amount=summ_qiwi, comment=comment_qiwi)
			await output_payments(message)
		except Errors.QIWIAPIError as e:
			if e.args[0] == "errorCode" and e.args[0]["errorCode"] == 'request.blocked':
				await message.answer('Ошибка: QIWIAPIError\n'
									 'У вас брокировка API\n'
									 'Вас разблокируют в течении 15 минут')
			if e.args[0]['code'] and e.args[0]['code'] == 'QWPRC-319':
				await message.answer('Вы отправляете платеж самому себе!', reply_markup=kb_qiwi)
			else:
				await message.answer('Ошибка: QIWIAPIError\n'
									 'Какая-то другая', reply_markup=kb_qiwi)
		except:
			await message.answer('Какая-то проблема с отправкой платежка', reply_markup=kb_qiwi)



async def output_payments(message: types.Message):
	await message.answer(f'⬇️Платеж успешен, информация о платеже⬇️\n'
										  f'🔥Сумма платежа - {summ_qiwi}🔥\n'
										  f'🔥Номер телефона - {number_qiwi}🔥\n'
										  f'🔥Коментарий - {comment_qiwi}🔥\n', reply_markup=kb_qiwi)


async def balance_qiwi(message: types.Message):
	people_id = message.from_user.id
	token = sqlite_db.cursor.execute('SELECT api FROM database WHERE id == ?', (people_id,)).fetchone()
	api = QApi(token=token[0], phone=config.phone)
	if token[0] != '0':
		try:
			await message.answer(api.balance[0])
		except requests.exceptions.JSONDecodeError:
			await message.answer('Токен не правильный')
		except Errors.QIWIAPIError as e:
			if e.args[0]["errorCode"] == 'request.blocked':
				await message.answer('Ошибка: QIWIAPIError\n'
									 'У вас брокировка API\n'
									 'Вас разблокируют в течении 15 минут')
			else:
				await message.answer('Ошибка: QIWIAPIError\n'
									 'Какая-то другая')
				print(e)
		except UnicodeEncodeError:
			await message.answer('Ошибка: UnicodeEncodeError\n'
								 'Вы ввели API с неправильными символами\n'
								 f'Ваш API сейчас - {token[0]}')
		except:
			await message.answer('Неисвестная ошибка')
	else:
		await message.answer('Вы не добавли токен')


class FSMNumber(StatesGroup):
	api_number = State()

async def set_number_start(message: types.Message):
	people_id = message.from_user.id
	number2 = sqlite_db.cursor.execute('SELECT number FROM database WHERE id == ?', (people_id,)).fetchone()
	await FSMNumber.api_number.set()
	your_number = f'🔸Ваш номер сейчас - <i>{number2[0]}</i>🔸' if number2[0] != '0' else ''
	await message.answer(f'❗Введите номер телефона <b><a href="qiwi.com">КИВИ</a></b> кошелька❗\n'
						 f'{your_number}', reply_markup=ReplyKeyboardMarkup(resize_keyboard=True).add(KeyboardButton('Назад')), parse_mode="HTML", disable_web_page_preview=True)


async def set_number_start_callback(callback: types.CallbackQuery):
	people_id = callback.from_user.id
	number2 = sqlite_db.cursor.execute('SELECT number FROM database WHERE id == ?', (people_id,)).fetchone()
	await FSMNumber.api_number.set()
	your_number = f'🔸Ваш номер сейчас - <i>{number2[0]}</i>🔸' if number2[0] != '0' else ''
	await callback.message.delete()
	await callback.message.answer(f'❗Введите номер телефона <b><a href="qiwi.com">КИВИ</a></b> кошелька❗\n'
						 f'{your_number}', reply_markup=ReplyKeyboardMarkup(resize_keyboard=True).add(KeyboardButton('Назад')), parse_mode="HTML", disable_web_page_preview=True)


async def set_number(message: types.Message, state: FSMContext):
	global number_text
	number_text = message.text
	global people_id
	people_id = message.from_user.id
	pattern = re.compile("^38\d{10}$")
	if pattern.search(message.text):
		await sqlite_db.update_number()
		await state.finish()
		number2 = sqlite_db.cursor.execute('SELECT number FROM database WHERE id == ?', (people_id,)).fetchone()
		await message.reply(f'Ваш новый номер - ”{number2[0]}”', reply_markup=kb_qiwi)
		await state.set_state('qiwi_on')
	else:
		await message.answer('Номер введен неверно!')


class FSMApi(StatesGroup):
	api_token = State()

async def set_api_start(message: types.Message):
	if message.chat.type == 'private':
		people_id = message.from_user.id
		token = sqlite_db.cursor.execute('SELECT api FROM database WHERE id == ?', (people_id,)).fetchone()
		await FSMApi.api_token.set()
		your_token = f'🔸<i>{token[0]}</i>🔸' if token[0] != '0' else ''
		await message.answer(f'❗Введите <b><a href="qiwi.com/api">ТОКЕН</a></b> киви кошелька❗\n'
							 f'{your_token}', reply_markup=ReplyKeyboardMarkup(resize_keyboard=True).add(KeyboardButton('Назад')), parse_mode="HTML", disable_web_page_preview=True)
	else:
		await message.answer('Изменять API можно только в личном чате с ботом - @ItsHealBot')


async def set_api_start_callback(callback: types.CallbackQuery):
	if callback.message.chat.type == 'private':
		await callback.message.delete()
		people_id = callback.from_user.id
		token = sqlite_db.cursor.execute('SELECT api FROM database WHERE id == ?', (people_id,)).fetchone()
		await FSMApi.api_token.set()
		your_token = f'🔸<i>{token[0]}</i>🔸' if token[0] != '0' else ''
		await callback.message.answer(f'❗Введите <b><a href="qiwi.com/api">ТОКЕН</a></b> киви кошелька❗\n'
							 f'{your_token}',
							 reply_markup=ReplyKeyboardMarkup(resize_keyboard=True).add(KeyboardButton('Назад')),
							 parse_mode="HTML", disable_web_page_preview=True)


async def set_api(message: types.Message, state: FSMContext):
	global api_text
	api_text = message.text
	global people_id
	people_id = message.from_user.id
	api = QApi(token=api_text, phone=config.phone)
	try:
		balance = api.balance
		await sqlite_db.update_api()
		await state.finish()
		token = sqlite_db.cursor.execute('SELECT api FROM database WHERE id == ?', (people_id,)).fetchone()
		await message.reply(f'Ваш новый токен - ”{token[0]}”', reply_markup=kb_qiwi)
		await state.set_state('qiwi_on')
	except:
		await message.answer('Токен не правильный!')


async def in_payments(message):
	global on_payments
	global people_id
	global token
	people_id = message.from_user.id
	token = sqlite_db.cursor.execute('SELECT api FROM database WHERE id == ?', (people_id,)).fetchone()
	phone2 = sqlite_db.cursor.execute('SELECT number FROM database WHERE id == ?', (people_id,)).fetchone()
	api = QApi(token=token[0], phone=phone2)
	payment_data = api.payments
	if on_payments == False:
		on_payments = []
	if not message.from_user.id in [id[0] for id in on_payments]:
		on_payments.append(sqlite_db.cursor.execute('SELECT id FROM database WHERE id == ?', (people_id,)).fetchone())
	data_in = payment_data['data'][0]['date']
	print(f'{data_in} цикл запущен')
	await message.answer('Уведомления о входящих платежах запущены')
	while True:
		try:
			payment_data = api.payments
			if payment_data['data'][0]['type'] == 'IN':
				new1 = payment_data['data'][0]['account']
				new2 = payment_data['data'][0]['sum']['amount']
				new3 = payment_data['data'][0]['date']
				print(data_in)
				if new3 != data_in:
					data_in = new3
					payment_data['data'][0]['account'] = new1
					payment_data['data'][0]['sum']['amount'] = new2
					print(new1, new2, new3)
					await message.answer(f'К вам пришел платеж от номера {new1} и на сумму {new2}')
			await asyncio.sleep(10)
		except:
			await message.answer('Проблема с токеном')


async def previous_handler_number_qiwi(message: types.Message, state: FSMContext):
	current_state = await state.get_state()
	if current_state is None:
		return
	await FSMAdmin.previous()
	await state.set_state('qiwi_on')
	await message.answer('ОК', reply_markup=kb_qiwi)

async def previous_handler_comment_qiwi(message: types.Message, state: FSMContext):
	current_state = await state.get_state()
	if current_state is None:
		return
	await FSMAdmin.previous()
	await message.answer('Напишите номер киви кошелька на который будет перевод!', reply_markup=ReplyKeyboardMarkup(resize_keyboard=True).add(KeyboardButton('Назад')))

async def previous_handler_summ_qiwi(message: types.Message, state: FSMContext):
	current_state = await state.get_state()
	if current_state is None:
		return
	await FSMAdmin.previous()
	await message.answer('Введи комантарий к переводу', reply_markup=ReplyKeyboardMarkup(resize_keyboard=True).add(KeyboardButton('Назад')).add(KeyboardButton('Пропустить')))

async def previous_handler_set_api(message: types.Message, state: FSMContext):
	current_state = await state.get_state()
	if current_state is None:
		return
	await FSMApi.previous()
	await state.set_state('qiwi_on')
	await message.answer('ОК', reply_markup=kb_qiwi)

async def previous_handler_set_number(message: types.Message, state: FSMContext):
	current_state = await state.get_state()
	if current_state is None:
		return
	await FSMApi.previous()
	await state.set_state('qiwi_on')
	await message.answer('ОК', reply_markup=kb_qiwi)

def register_handlers_qiwi(dp : Dispatcher):
	dp.register_message_handler(start_qiwi, text=['Киви'])
	dp.register_message_handler(start_qiwi_push, text=['Уведомления'], state='qiwi_on')
	dp.register_message_handler(previous_handler_number_qiwi, state=FSMAdmin.number_qiwi, text=['Назад'])
	dp.register_message_handler(previous_handler_comment_qiwi, state=FSMAdmin.comment_qiwi, text=['Назад'])
	dp.register_message_handler(previous_handler_summ_qiwi, state=FSMAdmin.summ_qiwi, text=['Назад'])
	dp.register_message_handler(previous_handler_set_api, state=FSMApi.api_token, text=['Назад'])
	dp.register_message_handler(previous_handler_set_number, state=FSMNumber.api_number, text=['Назад'])
	dp.register_message_handler(send_money_qiwi, text='Отправить', state='qiwi_on')
	dp.register_message_handler(qiwi_number, content_types=['text'], state=FSMAdmin.number_qiwi)
	dp.register_message_handler(qiwi_comment, state=FSMAdmin.comment_qiwi)
	dp.register_message_handler(qiwi_summ, state=FSMAdmin.summ_qiwi)
	dp.register_message_handler(balance_qiwi, text='Баланс', state='qiwi_on')
	dp.register_message_handler(set_api_start, text='Изменить API', state='qiwi_on')
	dp.register_callback_query_handler(set_api_start_callback, text='add_api', state='qiwi_on')
	dp.register_message_handler(set_api, state=FSMApi.api_token)
	dp.register_message_handler(set_number_start, text='Изменить номер', state='qiwi_on')
	dp.register_callback_query_handler(set_number_start_callback, text='add_number', state='qiwi_on')
	dp.register_message_handler(set_number, state=FSMNumber.api_number)


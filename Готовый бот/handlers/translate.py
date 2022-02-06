from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
import translators
from gtts import gTTS



language = {
    'Русский': 'ru',
    'English': 'en',
    'Украинский': 'uk',
	'Польский': 'pl'
}


# отправлка сообщения и клавиатуры выбора языка пользователю
async def choose_language(message: types.Message, state: FSMContext):
	markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)  # создаем клавиатуру
	markup.add(*language.keys()).add(KeyboardButton('В главное меню'))  # добавляем кнопки по ключам словаря language
	text = 'Выбери, на какой язык перевести:' if message.from_user.language_code == 'ru' \
		else 'Choose which language to translate:'  # если язык системы русский, отправляем сообщение на русском языке. Если нет, на английском
	await message.answer(
		text=text,  # отправляем текст
		reply_markup=markup  # отправляем клавиатуру
	)
	await state.set_state('choose_language')  # устанавливаем состояние на choose_language


# сохранение выбранного языка
async def save_language(message: types.Message, state: FSMContext):

	if message.text in language.keys():  # если пользователь нажал на кнопку в клавиатуре
		text = 'Отправь мне текст:' if message.from_user.language_code == 'ru' \
			else 'Send me a text'
		await message.answer(
			text=text,  # отправляем текст
			reply_markup=ReplyKeyboardMarkup(resize_keyboard=True).add(KeyboardButton('В главное меню'))  # удаляем клавиатуру
		)
		await state.set_state('save_language')
		await state.update_data(language=language.get(message.text))  # получаем код языка по ключу и сохраняем в хранилище
	else:  # если отправил другой текст, не тот что на клавиатуре. отправлеям сообщение об ошибке
		text = 'Выбери кнопку ниже.' if message.from_user.language_code == 'ru' \
			else 'Select the button below.'
		await message.answer(
			text=text
		)


async def translate_text(message: types.Message, state: FSMContext):
	try:  # пробуем отправить перевод
		user_data = await state.get_data()  # получаем данные сохраненные в хранилище
		await message.answer_chat_action(
			action=types.ChatActions.TYPING
		)  # answer_chat_action TYPING - создает видимость того, что бот печатает сообщение
		voice_path = f'{message.from_user.id}.ogg'
		to_language = user_data['language']  # передаем язык пользователя в переменную
		text = translators.google(  # вызываем модуль перевода текста
			query_text=message.text,  # передаем текст пользователя
			to_language=to_language  # передаем выбраный язык пользователя
		)
		gTTS(text=text, lang=user_data['language'])  # записываем произношение перевода
		await message.answer(text)
	except KeyError:  # если бот был перезагружен, то значение в user_data пропадет, так как данные хранились в ОЗУ
		await message.answer('Вы не выбрали язык перевода /language')



def register_handlers_translate(dp : Dispatcher):
	dp.register_message_handler(choose_language, commands='translate', content_types='text', state='*')
	dp.register_message_handler(choose_language, text='Переводчик', content_types='text', state='*')
	dp.register_message_handler(save_language, content_types='text', state='choose_language')
	dp.register_message_handler(translate_text, content_types='text', state='save_language')
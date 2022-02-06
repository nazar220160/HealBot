from aiogram.types import ReplyKeyboardMarkup, KeyboardButton#, ReplyKeyboardRemove

b1 = KeyboardButton('Киви')
b2 = KeyboardButton('Переводчик')
b3 = KeyboardButton('ТУТ ХЗ')
b4 = KeyboardButton('Поделится номером', request_contact=True)
b5 = KeyboardButton('Отправить где я', request_location=True)

kb_client = ReplyKeyboardMarkup(resize_keyboard=True)

kb_client.add(b1).insert(b2)
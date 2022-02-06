from aiogram.types import ReplyKeyboardMarkup, KeyboardButton#, ReplyKeyboardRemove

b1 = KeyboardButton('Посмотреть базу данных')
b2 = KeyboardButton('Изменить API другому пользователю')
b3 = KeyboardButton('Посмотреть баланс другого пользователя')
b4 = KeyboardButton('Поделится номером', request_contact=True)
b5 = KeyboardButton('Отправить где я', request_location=True)

kb_admin = ReplyKeyboardMarkup(resize_keyboard=True)

kb_admin.add(b1).add(b2).insert(b3)
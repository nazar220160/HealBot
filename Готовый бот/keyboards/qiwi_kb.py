from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

# Обычная клавиатура

b1 = KeyboardButton('Отправить')
b2 = KeyboardButton('Баланс')
b3 = KeyboardButton('Изменить API')
b4 = KeyboardButton('Поделится номером', request_contact=True)
b5 = KeyboardButton('Отправить где я', request_location=True)
b6 = KeyboardButton('В главное меню')
b7 = KeyboardButton('Изменить номер')
b8 = KeyboardButton('Уведомления')

kb_qiwi = ReplyKeyboardMarkup(resize_keyboard=True)

kb_qiwi.add(b1).insert(b2).insert(b8).add(b3).insert(b7).add(b6)


# Inline клавиатура!

qiwi_api = InlineKeyboardMarkup(row_width=1)
qiwi_number_i = InlineKeyboardMarkup(row_width=1)
qiwi_number_api = InlineKeyboardMarkup(row_width=1)

i1 = InlineKeyboardButton(text='Добавить номер', callback_data='add_number')
i2 = InlineKeyboardButton(text='Добавить API', callback_data='add_api')

qiwi_api.add(i2)
qiwi_number_i.add(i1)
qiwi_number_api.add(i1, i2)

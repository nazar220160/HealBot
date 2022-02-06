from aiogram import Dispatcher, types
import config
from create_bot import dp
from filters import MyFilter
from keyboards import kb_admin
from data_base import sqlite_db

dp.filters_factory.bind(MyFilter)

async def cmd_ban(message: types.Message):
    if not message.reply_to_message:
        await message.reply('Команда должна быть ответом на сообщение')
        return

    await message.bot.kick_chat_member(chat_id=config.GROUP_ID, user_id=message.reply_to_message.from_user.id)

    await message.reply_to_message.reply(
        f'Пользоватесь <b><a href="t.me/{message.reply_to_message.from_user.username}">{message.reply_to_message.from_user.first_name}</a></b> забанен',
        parse_mode="HTML", disable_web_page_preview=True)


async def start_admin(message: types.Message, state):
    people_id = message.from_user.id
    ID = sqlite_db.cursor.execute('SELECT admin FROM database WHERE id == ?', (people_id,)).fetchone()
    if ID[0] == '1':
        await state.set_state('admin_on')
        await message.answer('Вы авторизовались в админ панель!', reply_markup=kb_admin)
    elif ID[0] == '0':
        await message.answer('Вы не админ')


async def admin_func(message: types.Message):
    await message.answer('У тебя есть доступ')



def register_handlers_admin(dp: Dispatcher):
    dp.register_message_handler(cmd_ban, is_admin=True, commands=['ban'], commands_prefix="!/")
    dp.register_message_handler(start_admin, commands=['admin'], commands_prefix="!/")
    dp.register_message_handler(admin_func, text='Посмотреть базу данных', state='admin_on')


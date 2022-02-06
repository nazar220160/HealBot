from aiogram import types, Dispatcher
from create_bot import bot


async def echo_send(message: types.Message):
    block_text = ['слово', 'мат', 'лох', 'пидр', 'сука']
    for block_text in block_text:
        if block_text in message.text.lower():
            if message.chat.type == 'supergroup':
                    await bot.send_message(427176025, f'Сообщение - "{message.text}" от пользователя @{message.from_user.username}')
                    await message.delete()


async def on_user_joined(message: types.Message):
    await message.delete()


def register_handlers_other(dp: Dispatcher):
    dp.register_message_handler(echo_send, content_types=['text'])
    dp.register_message_handler(on_user_joined, content_types=['new_chat_members', 'left_chat_member', 'pinned_message'])
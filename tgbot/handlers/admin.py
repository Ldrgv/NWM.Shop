from aiogram import Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.types import Message, ContentTypes
from aiogram.utils.exceptions import ChatNotFound

from tgbot.services import database as db
from contextlib import suppress


async def admin_start(message: Message):
    text = f'Привет, {message.from_user.first_name}! Команды:\n' \
           '/send_messages - разослать отправленное мне сообщение участникам, купившим полный курс\n' \
           '/cancel - выйти из текущей команды (если случайно нажмете команду для рассылки)\n' \
           '/get_members_emails - получить почты участников (для открытия доступа к лекциям на YouTube)'
    await message.answer(text=text)


async def admin_send_messages(message: Message, state: FSMContext):
    await message.answer(text='Отправьте сообщение, которое нужно всем разослать')
    await state.set_state('send_messages')


async def admin_receive_send_messages(message: Message, state: FSMContext):
    await state.finish()
    await message.answer('Отправляю сообщение участникам...')
    count = 0
    users = await db.get_full_pack_users_chat_id(message.bot)
    for chat_id in users:
        with suppress(ChatNotFound):
            message_id = await message.copy_to(chat_id=chat_id)
            await message.bot.pin_chat_message(chat_id=chat_id, message_id=message_id.message_id)
            count += 1
    await message.answer(f'Ваше сообщение разослано {count} участникам!')


async def admin_cancel(message: Message, state: FSMContext):
    await state.finish()
    await message.answer('Действие отменено!')


def register_admin(dp: Dispatcher):
    dp.register_message_handler(admin_start, commands=["start"], state="*", is_admin=True)
    dp.register_message_handler(admin_cancel, commands=['cancel'], state='*', is_admin=True)
    dp.register_message_handler(admin_send_messages, commands=["send_messages"], state="*", is_admin=True)
    dp.register_message_handler(admin_receive_send_messages, state='send_messages', content_types=ContentTypes.ANY,
                                is_admin=True)

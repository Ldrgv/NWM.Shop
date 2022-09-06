from aiogram import Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.types import Message, ContentTypes
from aiogram.utils.exceptions import ChatNotFound

from tgbot.misc.models import Product
from tgbot.services import database as db
from contextlib import suppress

from tgbot.misc.states import AddProduct


async def admin_cmd_start(message: Message):
    text = f'Привет, {message.from_user.first_name}! Команды:\n' \
           '/send_messages - разослать отправленное мне сообщение участникам, купившим полный курс\n' \
           '/cancel - выйти из текущей команды (если случайно нажмете команду для рассылки)\n' \
           '/get_members_emails - получить почты участников (для открытия доступа к лекциям на YouTube)'
    await message.answer(text=text)


async def admin_cmd_send_messages(message: Message, state: FSMContext):
    await message.answer(text='Отправьте сообщение, которое нужно всем разослать')
    await state.set_state('send_messages')


async def admin_cmd_create_product(message: Message, state: FSMContext):
    await message.answer(text="Придумайте ключ к продукту (слово из строчных английских букв):")
    await state.set_state(AddProduct.product_key)


async def admin_state_product_title(message: Message, state: FSMContext):
    await state.update_data(key=message.text)
    await message.answer(text='Название:')
    await AddProduct.next()


async def admin_state_product_description(message: Message, state: FSMContext):
    await state.update_data(title=message.text)
    await message.answer(text='Описание:')
    await AddProduct.next()


async def admin_state_product_price(message: Message, state: FSMContext):
    await state.update_data(description=message.text)
    await message.answer(text='Цена:')
    await AddProduct.next()


async def admin_state_product_photo(message: Message, state: FSMContext):
    await state.update_data(price=message.text)
    await message.answer(text='Ссылка на фото:')
    await AddProduct.next()


async def admin_state_product_need_name(message: Message, state: FSMContext):
    await state.update_data(photo_url=message.text)
    await message.answer(text='Требуется ввод имени?')
    await AddProduct.next()


async def admin_state_product_need_phone_number(message: Message, state: FSMContext):
    await state.update_data(need_name=(message.text == 'да'))
    await message.answer(text='Требуется ввод номера?')
    await AddProduct.next()


async def admin_state_product_need_email(message: Message, state: FSMContext):
    await state.update_data(need_phone_number=(message.text == 'да'))
    await message.answer(text='Требуется ввод email?')
    await AddProduct.next()


async def admin_state_product_need_shipping_address(message: Message, state: FSMContext):
    await state.update_data(need_email=(message.text == 'да'))
    await message.answer(text='Требуется ввод адреса доставки?')
    await AddProduct.next()


async def admin_state_finish_product_adding(message: Message, state: FSMContext):
    await state.update_data(need_shipping_address=(message.text == 'да'))
    prod = await state.get_data()
    await db.add_product(Product(
        key=prod['key'],
        title=prod['title'],
        description=prod['description'],
        price=int(prod['price']),
        photo_url=prod['photo_url'],
        need_name=prod['need_name'],
        need_phone_number=prod['need_phone_number'],
        need_email=prod['need_email'],
        need_shipping_address=prod['need_shipping_address']
    ), bot=message.bot)
    await state.finish()
    await message.answer(text='Продукт добавлен!')


async def admin_state_get_message(message: Message, state: FSMContext):
    await state.finish()
    await message.answer('Отправляю сообщение участникам...')
    count = 0
    users = await db.get_full_pack_users_id(message.bot)
    for user_id in users:
        with suppress(ChatNotFound):
            message_id = await message.copy_to(chat_id=user_id)
            await message.bot.pin_chat_message(chat_id=user_id, message_id=message_id.message_id)
            count += 1
    await message.answer(f'Ваше сообщение разослано {count} участникам!')


async def admin_cmd_cancel(message: Message, state: FSMContext):
    if await state.get_state() is not None:
        await state.finish()
        await message.answer('Действие отменено!')


async def cmd_set_this_chat_as_main(message: Message):
    await db.set_bss_chat(chat_id=message.chat.id, bot=message.bot)
    await message.answer("Отлично! Теперь этот чат выбран как основной для проведения Бюро счастливых семей!")


def register_admin(dp: Dispatcher):
    dp.register_message_handler(admin_cmd_start, commands=["start"], state="*", is_admin=True)
    dp.register_message_handler(admin_cmd_cancel, commands=['cancel'], state='*', is_admin=True)
    dp.register_message_handler(admin_cmd_send_messages, commands=["send_messages"], state="*", is_admin=True)
    dp.register_message_handler(admin_state_get_message, state='send_messages', content_types=ContentTypes.ANY,
                                is_admin=True)

    dp.register_message_handler(admin_cmd_create_product, commands=['create_product'], state='*', is_admin=True)
    dp.register_message_handler(admin_state_product_title, state=AddProduct.product_key, is_admin=True)
    dp.register_message_handler(admin_state_product_description, state=AddProduct.product_title, is_admin=True)
    dp.register_message_handler(admin_state_product_price, state=AddProduct.product_description, is_admin=True)
    dp.register_message_handler(admin_state_product_photo, state=AddProduct.product_price, is_admin=True)
    dp.register_message_handler(admin_state_product_need_name, state=AddProduct.product_photo, is_admin=True)
    dp.register_message_handler(admin_state_product_need_phone_number, state=AddProduct.product_need_name, is_admin=True)
    dp.register_message_handler(admin_state_product_need_email, state=AddProduct.product_need_phone_number, is_admin=True)
    dp.register_message_handler(admin_state_product_need_shipping_address, state=AddProduct.product_need_email, is_admin=True)
    dp.register_message_handler(admin_state_finish_product_adding, state=AddProduct.product_need_shipping_address, is_admin=True)
    dp.register_message_handler(
        cmd_set_this_chat_as_main,
        commands='set_this_chat_as_main',
        chat_type=('group', 'supergroup'),
        state='*',
        is_admin=True
    )


from aiogram import Dispatcher
from aiogram.types import Message, CallbackQuery, PreCheckoutQuery, ContentType, ChatJoinRequest
from tgbot.keyboards.inline import get_amount_selection_keyboard, get_specific_module_selection_keyboard
from aiogram.dispatcher.filters import Text
from tgbot.services import database as db


async def user_start(message: Message):
    await message.answer("Здравствуйте! Я - бот, принимающий оплату за Бюро Счастливых семей."
                         "Напишите /buy, чтобы купить курс.")


async def user_buy(message: Message):
    keyboard = await get_amount_selection_keyboard(member_id=message.from_user.id, bot=message.bot)
    await message.answer(text="Сколько модулей хотите купить?", reply_markup=keyboard)


async def user_call_one_module(callback: CallbackQuery):
    keyboard = await get_specific_module_selection_keyboard(member_id=callback.from_user.id, bot=callback.bot)
    await callback.message.edit_text(text='Какой модуль хотите купить?', reply_markup=keyboard)
    await callback.answer()


async def user_call_module_back(callback: CallbackQuery):
    keyboard = await get_amount_selection_keyboard(member_id=callback.from_user.id, bot=callback.bot)
    await callback.message.edit_text(text="Сколько модулей хотите купить?", reply_markup=keyboard)
    await callback.answer()


async def process_pre_checkout_query(pre_checkout_query: PreCheckoutQuery):
    await pre_checkout_query.bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True)


async def process_successful_payment(message: Message):
    invoice_payload = message.successful_payment.invoice_payload
    # Получаем чат из конфига
    chat_id = message.bot['config'].misc.module_chat
    user_id = message.from_user.id
    text = ''
    # Разбираем купленный товар
    if invoice_payload.endswith('module') or invoice_payload == 'full_module_pack':
        link = (await message.bot.create_chat_invite_link(
            chat_id=chat_id, creates_join_request=True, name=str(user_id)
        )).invite_link
        text = f'Ссылка на чат: {link}\n'
    await message.answer(text=text)
    await db.add_payment(user_id=user_id, product=invoice_payload, bot=message.bot)
    if invoice_payload == 'full_module_pack':
        await db.add_full_pack_user(user_id=user_id, user_name=message.from_user.first_name,
                                    chat_id=message.chat.id, bot=message.bot)


async def process_add_member_to_chat(chat_member: ChatJoinRequest):
    chat_id = chat_member.chat.id
    user_id = chat_member.from_user.id
    invite_link = chat_member.invite_link
    if invite_link.name == str(user_id):
        link = invite_link.invite_link
        await chat_member.approve()
        await chat_member.bot.revoke_chat_invite_link(chat_id=chat_id, invite_link=link)
    else:
        await chat_member.decline()


def register_user(dp: Dispatcher):
    dp.register_message_handler(user_start, commands=["start"])
    dp.register_message_handler(user_buy, commands='buy')
    dp.register_message_handler(process_successful_payment, content_types=ContentType.SUCCESSFUL_PAYMENT)
    dp.register_callback_query_handler(user_call_one_module, Text(equals='one_module'))
    dp.register_callback_query_handler(user_call_module_back, Text(equals='back_to_amount_selection'))
    dp.register_pre_checkout_query_handler(process_pre_checkout_query)
    dp.register_chat_join_request_handler(process_add_member_to_chat)

# TODO
# Если челик уже покупал что-то, то при /buy отображается только то, что он не купил
# Если он покупил фулл пак, то при /buy ему об этом говорится, а сразу после покупки,
# сообщение меняется на что-то типа: Вы купили полный курс!
# вставить после покупки в кнопки ссылки на чаты?
# добавление того кто пригласил человека

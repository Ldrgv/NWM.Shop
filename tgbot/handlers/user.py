from aiogram import Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.types import Message, PreCheckoutQuery, ContentType, ChatJoinRequest, LabeledPrice

from tgbot.keyboards import reply as keyboards
from tgbot.misc.states import BSS
from tgbot.services import database as db


async def cmd_start(message: Message, state: FSMContext):
    await message.answer(text="Салам! Я - New Wave Muslim BRO!")
    await set_default(message, state)


async def set_default(message: Message, state: FSMContext = None):
    await state.finish()
    keyboard = keyboards.get_start()
    await message.edit_reply_markup(reply_markup=keyboard)


async def send_invoice(product: str, message: Message):
    product_key = product
    bot = message.bot
    product = await db.get_product(user_id=message.from_user.id, product_key=product_key, bot=bot)
    await bot.send_invoice(
        chat_id=message.from_user.id,
        title=product.title,
        description=product.description,
        payload=product.key,
        provider_token=bot['config'].misc.payment_token,
        currency='rub',
        prices=[LabeledPrice(label='Бюро счастливых семей', amount=product.price*100)],
        photo_url=product.photo_url,
        photo_size=256,
        photo_width=256,
        photo_height=256,
        need_name=product.need_name,
        need_phone_number=product.need_phone_number,
        need_email=product.need_email,
        need_shipping_address=product.need_shipping_address
    )


async def send_pray_schedule(message: Message):
    await message.answer_photo(photo='https://dum-spb.ru/wp-content/uploads/2020/11/Расписание-молитв-Август-2022.png')


# msg.text = Бюро счастливых семей
async def msg_bss(message: Message):
    keyboard = keyboards.get_amount_selection()
    await message.answer(text="Сколько модулей хотите купить?", reply_markup=keyboard)
    await BSS.amount_selection.set()


async def state_module_amount_selection(message: Message, state: FSMContext):
    pass
    # text = message.text
    # match text:
    #     case '3':
    #         await send_invoice(product='full_module_pack', message=message)
    #     case '1':
    #         await message.answer('Какой модуль вам нужен?', reply_markup=keyboards.get_specific_module_selection())
    #         await BSS.next()
    #     case '<':
    #         await set_default(message, state)
    #     case unknown_command:
    #         await message.answer('Воспользуйтесь клавиатурой!')


# state = specific_module_selection
async def state_specific_module(message: Message, state: FSMContext):
    text = message.text
    if text in ['1', '2', '3']:
        await send_invoice(product=(text + '_module'), message=message)
    elif text == '<':
        await state.finish()
        await state_module_amount_selection(message, state)
    else:
        await message.answer('Воспользуйтесь клавиатурой!')


async def process_pre_checkout_query(pre_checkout_query: PreCheckoutQuery):
    await pre_checkout_query.bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True)


async def process_successful_payment(message: Message, state: FSMContext):
    invoice_payload = message.successful_payment.invoice_payload
    # Получаем чат из конфига
    chat_id = message.bot['config'].misc.module_chat
    user_id = message.from_user.id
    # Разбираем купленный товар
    if invoice_payload.endswith('module') or invoice_payload == 'full_module_pack':
        link = (await message.bot.create_chat_invite_link(
            chat_id=chat_id, creates_join_request=True, name=str(user_id)
        )).invite_link
        text = f'Ссылка на чат: {link}\n'
        await message.answer(text=text)
        # Попросим указать инвайтера
        await message.answer(text="Если вас пригласил друг, то отправьте ссылку на его telegram, "
                                  "иначе напишите `нет`", parse_mode='Markdown')
        await state.update_data(payment_amount=message.successful_payment.total_amount)
        await state.set_state('wait_for_inviter_friend')
    if invoice_payload == 'full_module_pack':
        await db.add_full_pack_user(user_id=user_id, user_name=message.from_user.first_name, bot=message.bot)
    # Добавим платеж в бд
    await db.add_payment(user_id=user_id, product=invoice_payload, bot=message.bot)


async def receive_inviter_friend(message: Message, state: FSMContext):
    await message.answer_photo(photo='https://downloader.disk.yandex.ru/preview/41db1dba2cb141621054c1a0c4ff9f685474e7003745cacccbdf4792a8bc07c3/63082289/Y5L9Od3ID0A48Ydi6g4hVBHCMnX9bL8U39x1IXZm6BmMuAibb69cjgE4QAl4SO0ewSSl_SapFBU6vX7Hrz8aFg%3D%3D?uid=0&filename=bhf2&disposition=inline&hash=&limit=0&content_type=image%2Fpng&owner_uid=0&tknv=v2&size=2048x2048',
                               reply_markup=keyboards.get_start())
    await state.finish()
    if message.text.lower() == 'нет':
        return
    admins = message.bot['config'].tg_bot.admin_ids
    for admin_id in admins:
        amount = (await state.get_data())['payment_amount'] / 100
        try:
            msg = await message.bot.send_message(chat_id=admin_id,
                                             text=f"{message.text} пригласил "
                                                  f"{message.from_user.get_mention()}, который оплатил "
                                                  f"{amount} рублей",
                                             parse_mode='Markdown')
            await msg.pin()
        except Exception:
            pass
    await message.answer('Я передал админам!')
    await set_default(message=message, state=state)


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
    dp.register_message_handler(cmd_start, commands="start")
    dp.register_message_handler(msg_bss, Text(equals='Бюро счастливых семей'))
    dp.register_message_handler(send_pray_schedule, Text(equals='Расписание молитв (СПб)'))
    dp.register_message_handler(state_module_amount_selection, state=BSS.amount_selection)
    dp.register_message_handler(state_specific_module, state=BSS.specific_module_selection)
    dp.register_message_handler(process_successful_payment, content_types=ContentType.SUCCESSFUL_PAYMENT)
    dp.register_message_handler(receive_inviter_friend, state='wait_for_inviter_friend')
    dp.register_pre_checkout_query_handler(process_pre_checkout_query)
    dp.register_chat_join_request_handler(process_add_member_to_chat)

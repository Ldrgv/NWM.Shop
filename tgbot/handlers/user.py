import datetime
import aiosmtplib

from aiogram import Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.types import Message, PreCheckoutQuery, ContentType, ChatJoinRequest, LabeledPrice, ChatMemberUpdated

from tgbot.keyboards import reply as keyboards
from tgbot.misc.states import BSS
from tgbot.services import database as db
from email.message import EmailMessage


async def cmd_start(message: Message, state: FSMContext):
    await message.answer(text="Добро пожаловать!")
    await set_default(message, state)


async def set_default(message: Message, state: FSMContext):
    await state.finish()
    await message.answer(text='Ниже представлено то, чем я могу быть полезен Вам!', reply_markup=keyboards.get_start())


async def send_invoice(product_key: str, message: Message):
    bot = message.bot
    product = await db.get_product(user_id=message.from_user.id, product_key=product_key, bot=bot)
    await bot.send_invoice(
        chat_id=message.from_user.id,
        title=product.title,
        description=product.description,
        payload=product.key,
        provider_token=bot['config'].misc.payment_token,
        currency='rub',
        prices=[LabeledPrice(label=product.title, amount=product.price * 100)],
        photo_url=product.photo_url,
        photo_size=512,
        photo_height=512,
        photo_width=512,
        need_name=product.need_name,
        need_phone_number=product.need_phone_number,
        need_email=product.need_email,
        need_shipping_address=product.need_shipping_address
    )


async def send_pray_schedule(message: Message):
    months = [
        'Январь', 'Февраль', 'Март',
        'Апрель', 'Май', 'Июнь',
        'Июль', 'Август', 'Сентябрь',
        'Октябрь', 'Ноябрь', 'Декабрь'
    ]
    today = datetime.date.today()
    await message.answer_photo(
        photo=f'https://dum-spb.ru/wp-content/uploads/2020/11/'
              f'Расписание-молитв-{months[today.month - 1]}-{today.year}.png'
    )


async def send_halal_map(message: Message):
    await message.answer('[Халяльный Петербург](https://yandex.ru/maps/?um=constructor%3Ae15b576cd4cdd60c6e80f46f5bb4f1236c9112dac78f6f3190646938326fd8d4&source=constructorLink)', parse_mode='Markdown')


# msg.text = Бюро счастливых семей
async def msg_bss(message: Message):
    keyboard = keyboards.get_amount_selection()
    await message.answer(text="Сколько модулей хотите купить?", reply_markup=keyboard)
    await BSS.amount_selection.set()


async def state_module_amount_selection(message: Message, state: FSMContext):
    text = message.text
    match text:
        case 'Полный цикл встреч':
            await send_invoice(product_key='full_module_pack', message=message)
        case 'Один из модулей':
            await message.answer('Какой модуль вам нужен?', reply_markup=keyboards.get_specific_module_selection())
            await BSS.next()
        case '<':
            await set_default(message, state)
        case unknown_command:
            await message.answer('Воспользуйтесь клавиатурой!')


# state = specific_module_selection
async def state_specific_module(message: Message):
    text = message.text
    match text:
        case '👩‍❤️‍👨 До супружество':
            await send_invoice(product_key='1_module', message=message)
        case '👨‍👩‍👧‍👦 Внутрисемейные отношения':
            await send_invoice(product_key='2_module', message=message)
        case '🍃 Пост супружеские отношения':
            await send_invoice(product_key='3_module', message=message)
        case '<':
            await msg_bss(message)
        case unknown_command:
            await message.answer('Воспользуйтесь клавиатурой!')


async def process_pre_checkout_query(pre_checkout_query: PreCheckoutQuery):
    print('want')
    await pre_checkout_query.bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True)


async def process_successful_payment(message: Message, state: FSMContext):
    # Отправляем картинку об успешной оплате
    await message.answer_photo(
        photo='https://downloader.disk.yandex.ru/preview/c412736322ba9a2e39a6c9d0fcdb224cab098accb2ec800e53778a9b73c3a57a/63154aef/Y5L9Od3ID0A48Ydi6g4hVBHCMnX9bL8U39x1IXZm6BmMuAibb69cjgE4QAl4SO0ewSSl_SapFBU6vX7Hrz8aFg%3D%3D?uid=0&filename=bhf2&disposition=inline&hash=&limit=0&content_type=image%2Fpng&owner_uid=0&tknv=v2&size=1024x1024',
        reply_markup=keyboards.get_start())

    # Получаем нужные данные
    bot = message.bot
    config = bot['config']
    chat_id = await db.get_bss_chat(bot=bot)
    user_id = message.from_user.id
    invoice_payload = message.successful_payment.invoice_payload

    # Разбираем купленный товар
    if invoice_payload.endswith('module') or invoice_payload == 'full_module_pack':
        # Уведомляем о том, что сообщение на почту будет отправлено
        text = f'Скоро на указанную вами почту придёт ссылка на чат!'
        await message.answer(text=text)

        # Попросим указать инвайтера
        await message.answer(text="Если вас пригласил друг, то отправьте ссылку на его telegram, "
                                  "иначе напишите `нет`", parse_mode='Markdown')

        # Запоминаем оплаченную сумму, чтобы уведомить админов и сделать кэшбек
        await state.update_data(payment_amount=message.successful_payment.total_amount)

        # Ждем указания друга
        await state.set_state('wait_for_inviter_friend')

        # Получаем ссылку на чат
        link = (await message.bot.create_chat_invite_link(
            chat_id=chat_id, creates_join_request=True, name=str(user_id)
        )).invite_link

        # Формируем сообщение
        sender = config.misc.sender_email
        pswrd = config.misc.smtp_password
        msg = EmailMessage()
        msg["From"] = sender
        msg["To"] = message.successful_payment.order_info.email
        msg["Subject"] = "Бюро счастливых семей"
        msg.set_content(
            f'Вы успешно оплатили курс "Бюро счастливых семей"! Ссылка на чат проведения мероприятия: {link}'
        )

        # Отправляем сообщение на указанную при оплате почту
        await aiosmtplib.send(msg, hostname="smtp.yandex.ru", port=465, username=sender, password=pswrd, use_tls=True)

    # Если человек купил полный курс, то он добавляется в особый список в бд
    # Людям из этого списка админ может рассылать доп. материалы
    if invoice_payload == 'full_module_pack':
        await db.add_full_pack_user(user_id=user_id, user_name=message.from_user.first_name, bot=message.bot)

    # Добавим платеж в бд
    await db.add_payment(user_id=user_id, product=invoice_payload, bot=message.bot)


async def receive_inviter_friend(message: Message, state: FSMContext):
    data = await state.get_data()
    amount = data['payment_amount'] / 100
    await state.finish()
    if message.text.lower() == 'нет':
        await message.answer(text='Хорошо!')
        return
    admins = message.bot['config'].tg_bot.admin_ids
    for admin_id in admins:
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


async def my_chat_member(update: ChatMemberUpdated):
    bot = update.bot
    chat_id = update.chat.id
    if not update.old_chat_member.is_chat_member():
        await db.set_bss_chat(chat_id=chat_id, bot=bot)
        await bot.send_message(chat_id=chat_id, text="Привет! Теперь данный чат будет использоваться как основной "
                                                     "для проведения Бюро счастливых семей! Если хотите изменить чат, "
                                                     "то напишите в нужной группе `/set_this_chat_as_main`. Также "
                                                     "не забудьте сделать меня админом, чтобы я мог добавлять новых "
                                                     "участников! :)",
                               parse_mode='Markdown')
    elif update.new_chat_member.is_chat_admin():
        await bot.send_message(chat_id=chat_id, text='Вау! Теперь я тоже админ 🦸')


def register_user(dp: Dispatcher):
    dp.register_message_handler(cmd_start, commands="start", state='*')
    dp.register_message_handler(msg_bss, Text(equals='❤️ Бюро счастливых семей'))
    dp.register_message_handler(send_pray_schedule, Text(equals='📿 Расписание молитв'))
    dp.register_message_handler(send_halal_map, Text(equals='🗺 Халяльная карта'))
    dp.register_message_handler(state_module_amount_selection, state=BSS.amount_selection)
    dp.register_message_handler(state_specific_module, state=BSS.specific_module_selection)
    dp.register_message_handler(process_successful_payment, content_types=ContentType.SUCCESSFUL_PAYMENT, state='*')
    dp.register_message_handler(receive_inviter_friend, state='wait_for_inviter_friend')
    dp.register_pre_checkout_query_handler(process_pre_checkout_query, state='*')
    dp.register_chat_join_request_handler(process_add_member_to_chat)
    dp.register_my_chat_member_handler(my_chat_member, chat_type=('group', 'supergroup'), state='*')

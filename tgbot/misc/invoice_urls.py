from aiogram import Bot
from aiogram.types import LabeledPrice
from tgbot.services import database as db


async def get_specific_module_invoice_url(user_id: int, module: int, bot: Bot):
    amount = await db.get_product_price(user_id=user_id, product=f'{module}_module', bot=bot)
    return await bot.create_invoice_link(
        title='Бюро счастливых семей',
        description=f'{module}-й модуль',
        payload=f'{module}_module',
        provider_token=bot['config'].misc.payment_token,
        currency='rub',
        prices=[LabeledPrice(label='Бюро счастливых семей', amount=amount)],
        need_email=True
    )


async def get_all_modules_invoice_url(user_id: int, bot: Bot):
    amount = await db.get_product_price(user_id=user_id, product=f'full_module_pack', bot=bot)
    return await bot.create_invoice_link(
        title='Бюро счастливых семей',
        description='все модули',
        payload=f'full_module_pack',
        provider_token=bot['config'].misc.payment_token,
        currency='rub',
        prices=[LabeledPrice(label='Бюро счастливых семей', amount=amount)],
        need_email=True
    )

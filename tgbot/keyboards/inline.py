from aiogram import Bot
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from tgbot.misc.invoice_urls import get_specific_module_invoice_url, get_all_modules_invoice_url


# Выбор количества модулей
async def get_amount_selection_keyboard(member_id: int, bot: Bot):
    url = await get_all_modules_invoice_url(user_id=member_id, bot=bot)
    buttons = [
        InlineKeyboardButton(text='1', callback_data='one_module'),
        InlineKeyboardButton(text='3', url=url)
    ]
    keyboard = InlineKeyboardMarkup()
    keyboard.add(*buttons)
    return keyboard


# Выбор конкретного модуля
async def get_specific_module_selection_keyboard(member_id: int, bot: Bot):
    urls = [
        await get_specific_module_invoice_url(user_id=member_id, module=num, bot=bot) for num in range(1, 4)
    ]
    buttons = [
        InlineKeyboardButton(text=f'{num}', url=urls[num - 1]) for num in range(1, 4)
    ]
    buttons.append(InlineKeyboardButton(text='<', callback_data='back_to_amount_selection'))
    keyboard = InlineKeyboardMarkup(row_width=3)
    keyboard.add(*buttons)
    return keyboard

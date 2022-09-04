from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


# Выбор первого действия
def get_start():
    buttons = [
        KeyboardButton(text='❤️ Бюро счастливых семей'),
        KeyboardButton(text='📿 Расписание молитв'),
        KeyboardButton(text='🗺 Халяльная карта')
    ]
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    keyboard.add(*buttons)
    return keyboard


# Выбор количества модулей
def get_amount_selection():
    buttons = [
        KeyboardButton(text='Один из модулей'),
        KeyboardButton(text='Полный цикл встреч'),
        KeyboardButton(text='<')
    ]
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    keyboard.add(*buttons)
    return keyboard


# Выбор конкретного модуля
def get_specific_module_selection():
    buttons = [
        KeyboardButton(text='👩‍❤️‍👨 До супружество'),
        KeyboardButton(text='👨‍👩‍👧‍👦 Внутрисемейные отношения'),
        KeyboardButton(text='🍃 Пост супружеские отношения'),
        KeyboardButton(text='<')
    ]
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    keyboard.add(*buttons)
    return keyboard

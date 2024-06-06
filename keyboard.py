from aiogram import Bot, Dispatcher, Router, types, F
from aiogram.types import BotCommand, BotCommandScopeDefault



kb = [
    [types.KeyboardButton(text='ДОХОД')],
    [types.KeyboardButton(text='РАСХОД')],
]
keyboard = types.ReplyKeyboardMarkup(keyboard=kb)

kb2 = [
    [types.KeyboardButton(text='RUB')],
    [types.KeyboardButton(text='EUR')],
    [types.KeyboardButton(text='USD')],
]
keyboard2 = types.ReplyKeyboardMarkup(keyboard=kb2)

comands = [
    BotCommand(command='/reg', description='Регистрация'),
    BotCommand(command='/add_operation', description='Добавление новой операции'),
    BotCommand(command='/operations', description='Просмотр операций'),
    BotCommand(command='/update_operation', description='Обновление суппы операции')
]
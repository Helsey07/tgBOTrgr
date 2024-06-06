
from aiogram import Bot, Dispatcher, Router, types, F
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command, StateFilter

from DB.connect_db import connect_to_db
from State.states import StatesBot
from KeyBoard.keyboard import keyboard

router = Router()
connection = connect_to_db()
#обработчик команды /start
@router.message(Command("start"))
async def start_command(message: types.Message):
        await message.answer("Привет, ГАНСТЕР! Выбери нужную тебе команду")

#обработчик команды /reg
@router.message(Command("reg"))
async def reg(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    print(user_id)

    connection = await connect_to_db()
    result = await connection.fetchval("SELECT * FROM users WHERE id = $1", user_id)

    if result:
        await message.answer("Ты уже зарегистрирован 🤬")
        await state.clear()
    else:
        await message.answer("Напиши свой логин  👀")
        await state.set_state(StatesBot.login_entry_for_reg)
    await connection.close()

@router.message(StateFilter(StatesBot.login_entry_for_reg))
async def set_currency_name(message: types.Message, state: FSMContext):
    name = message.text.strip()
    user_id = message.from_user.id

    connection = await connect_to_db()
    availabilityLogin = await connection.fetchrow("SELECT * FROM users WHERE name = $1", name)

    if availabilityLogin:
        await message.answer("Логин уже занят... Придумай уникальный 🤬")
    else:
        await connection.fetchrow("INSERT INTO users (id, name) VALUES ($1, $2)", user_id, name)
        await message.answer("Теперь ты с нами!!!!  🤪")
        await state.clear()
    await connection.close()
# ___________________________________________________________________________________________________________________
#обработчик команды /add_operation

@router.message(Command("add_operation"))
async def add_operation(message: types.Message):
    user_id = message.from_user.id

    connection = await connect_to_db()
    result = await connection.fetchval("SELECT * FROM users WHERE id = $1", user_id)

    if not result:
        await message.answer("Ты не зарегистрирован 🤬")
    else:
        await message.answer("Выбери нужную операцию", reply_markup=keyboard)

    await connection.close()

@router.message(Command("update_operation"))
async def update_operation(message: types.Message, state: FSMContext):
    user_id = message.from_user.id

    connection = await connect_to_db()
    result = await connection.fetchval("SELECT * FROM users WHERE id = $1", user_id)

    if not result:
        await message.answer("Тебе нужно зарегистрироваться!")
        await state.clear()
    else:
        await message.answer("Введи идентификатор операции")
        await state.set_state(StatesBot.operationIdentifier)
    await connection.close()

@router.message(StateFilter(StatesBot.operationIdentifier))
async def operationIdentifier(message: types.Message, state: FSMContext):
    user_id = message.from_user.id

    try:
        operationIdentifier = int(message.text.strip())
        connection = await connect_to_db()
        result = await connection.fetchval("SELECT * FROM operations WHERE id = $1 and chat_id=$2", operationIdentifier,
                                       user_id)
        await connection.close()

        if result:
            await message.answer('Введите сумму, на которую хотите заменить')
            await state.update_data(operationIdentifier=operationIdentifier)
            await state.set_state(StatesBot.replacementAmount)
        else:
            await message.answer('Что-то пошло не так. Проверьте ваш индификатор.')
    except:
        await message.answer('Введено не коректное число.')


@router.message(StateFilter(StatesBot.replacementAmount))
async def replacementAmount(message: types.Message, state: FSMContext):
    try:
        replacementAmount = float(message.text.strip())

        data = await state.get_data()
        operationIdentifier = data.get('operationIdentifier')
        try:
            connection = await connect_to_db()
            await connection.fetchval("UPDATE operations SET sum=$1 WHERE id=$2",
                                               replacementAmount,
                                               operationIdentifier)
            await message.answer('Изменения успешно сохранены')
            await connection.close()
            await state.clear()
        except:
            await message.answer('Что-то пошло не так...')
    except:
        await message.answer('Вы ввели не коректное число')
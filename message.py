import re
from aiogram import Bot, Dispatcher, Router, types, F
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command, StateFilter
import datetime

from DB.connect_db import connect_to_db
from State.states import StatesBot

router = Router()
connection = connect_to_db()

@router.message(F.text == 'РАСХОД')
async def add_operation(message: types.Message, state: FSMContext):
    operation_type = message.text.strip()
    if operation_type:
        await message.answer("Введи сумму операции в рублях")
        await state.update_data(operation_type=operation_type)
        await state.set_state(StatesBot.money)
    else:
        await message.answer("Выберите команду из предложенных")

@router.message(F.text == 'ДОХОД')
async def add_operation(message: types.Message, state: FSMContext):
    operation_type = message.text.strip()
    if operation_type:
        await message.answer("Введи сумму операции в рублях")
        await state.update_data(operation_type=operation_type)
        await state.set_state(StatesBot.money)
    else:
        await message.answer("Выберите команду из предложенных")

@router.message(StateFilter(StatesBot.money))
async def money(message: types.Message, state: FSMContext):
    try:
        print('Состояние money')
        money = float(message.text.strip())
        await message.answer("Введи дату")
        await state.update_data(amount=money)
        await state.set_state(StatesBot.date)
    except ValueError:
        await message.answer("Введите корректную сумму операции в рублях (число)")

@router.message(StateFilter(StatesBot.date))
async def date(message: types.Message, state: FSMContext):
    date_str = message.text.strip()
    # Проверяем формат даты (Регулярное выражение)
    if re.match(r'\d{2}\.\d{2}\.\d{4}', date_str):
        try:
            # Пробуем преобразовать строку в объект datetime
            date = datetime.datetime.strptime(date_str, '%d.%m.%Y')

            await state.update_data(date=date)
            data = await state.get_data()

            operation_type = data.get('operation_type')  # Получение типа операции
            amount = data.get('amount')
            date = data.get('date')
            user_id = message.from_user.id
            try:
                print('Попытка сохранения в базу данных')
                connection = await connect_to_db()
                await connection.fetchrow(
                    "INSERT INTO operations (date, sum, chat_id, type_operation) VALUES ($1, $2, $3, $4)",
                    date, amount, user_id, operation_type)
                await message.answer("Сохранение прошло успешно")
                await state.clear()
                await connection.close()
            except Exception:
                await message.answer("ЧО ТО ПОШЛО НЕ ТАК")
        except ValueError:
            await message.answer("Введите корректную дату в формате ДД.ММ.ГГГГ1")
    else:
        await message.answer("Введите дату в формате ДД.ММ.ГГГГ2")
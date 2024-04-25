import aiohttp

from aiogram.filters import Command, CommandObject
from aiogram.types import Message
from aiogram.utils.keyboard import ReplyKeyboardBuilder

from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram import Router, types
from util import category, name, recipe_by_category, id_reciep
router = Router()


@router.message(Command("name"))
async def search_by_name(message: Message, command: CommandObject):
    if command.args is None:
        await message.answer(
            "Ошибка! Не переданы аргументы!"
        )
        return
    async with aiohttp.ClientSession() as session:
        data = await name(session, command.args)

    await message.answer(data)


class OrderMeal(StatesGroup):
    category_waiting = State()
    id_waiting = State()


@router.message(Command('category_search_random'))
async def search_category(message: Message, command: CommandObject, state: FSMContext):
    if command.args is None:
       await message.answer(
          "Ошибка: не переданы аргументы"
       )
       return
    async with aiohttp.ClientSession() as session:
        data = await category(session)

    await state.set_data({'quantity': int(command.args)})

    builder = ReplyKeyboardBuilder()
    for meal in data:
        builder.add(types.KeyboardButton(text=meal))
    builder.adjust(4)

    await message.answer(
       f"Выберите категорию:",
       reply_markup=builder.as_markup(resize_keyboard=True),

    )
    await state.set_state(OrderMeal.category_waiting.state)


@router.message(OrderMeal.category_waiting)
async def meal_by_category(message: types.Message, state: FSMContext):
    async with aiohttp.ClientSession() as session:
        text, ids = await recipe_by_category(session, message.text, await state.get_data())

        await state.set_data({'ids': ids})

    builder = ReplyKeyboardBuilder()
    builder.add(types.KeyboardButton(text='Покажи рецеты'))
    await message.answer(
         f'Как вам такие варианты: {','.join(text)}',
        reply_markup=builder.as_markup(resize_keyboard=True)
     )

    await state.set_state(OrderMeal.id_waiting.state)


@router.message(OrderMeal.id_waiting)
async def meal_by_id(message: types.Message, state: FSMContext):
    async with aiohttp.ClientSession() as session:
        data = await state.get_data()
        meals = await id_reciep(session, data)
        print(meals)
        for meal in meals:
            await message.answer(
                meal
            )




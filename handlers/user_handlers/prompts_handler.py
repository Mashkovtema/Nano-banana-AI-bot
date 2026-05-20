from aiogram import Bot, types, Router, F
from aiogram.filters import Command, StateFilter, or_f
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup, default_state
import logging

from config_data.config_data import Config, load_config
from keyboard import admin_keyboard, user_keyboard
from database.requests import admin_requests, user_requests

config: Config = load_config()
router = Router()


@router.message(or_f(F.text == '💡 Идеи и промпты/Ideas and Prompts', Command('ideas')))
async def ideas(message: types.Message):
    """Идеи"""
    logging.info('ideas')
    ideas_data = await user_requests.get_ideas()
    if ideas_data:
        idea = ideas_data[0]
        idea = idea.__dict__
        text = (f'Идея/idea {idea["id"]}\n\n'
                f'💡 Описание/Description: {idea["description"]}\n\n'
                f'🎨 Промпт/Prompt: {idea["prompt"]}')

        markup = await user_keyboard.pagination_buttons(0, ideas_data)
        await message.answer(text=text, reply_markup=markup)

    else:
        await message.answer('Идей для генерации пока что нет ❌')


@router.callback_query(F.data.startswith('pagination-user-ideas_'))
async def pagination_user_ideas(callback: types.CallbackQuery):
    page = int(str(callback.data).split('_')[1])
    ideas_data = await user_requests.get_ideas()

    if 0 <= page < len(ideas_data):

        idea = ideas_data[page]
        idea = idea.__dict__
        text = (f'Идея/idea {idea["id"]}\n\n'
                f'💡 Описание/Description: {idea["description"]}\n\n'
                f'🎨 Промпт/Prompt: {idea["prompt"]}')

        markup = await user_keyboard.pagination_buttons(page, ideas_data)
        await callback.message.edit_text(text=text, reply_markup=markup)
    else:
        await callback.answer()












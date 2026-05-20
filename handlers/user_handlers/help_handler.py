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


@router.message(or_f(F.text == 'ℹ️ Помощь/help', Command('help')))
async def help_handler(message: types.Message):
    """Помощь"""
    logging.info('help_handler')
    text = ('📖 Справка по командам\n\n'
            'Основные команды:\n'
            '/start - Главное меню\n'
            '/help - Эта справка\n'
            '/balance - Проверить и пополнить баланс\n'
            '/referal - Реферальная система\n\n'
            '🎨 Генерация изображений:\n'
            'Используйте /generate для выбора типа генерации\n\n'
            '💡 Раздел Идеи и промпты:\n'
            '/ideas Открывает витрину готовых промптов и примеров\n\n'
            '❓ Вопросы?\n'
            'Напишите нам: @MarselleGaya\n\n\n'
            '📖 Command Reference\n\n'
            'Main Commands:\n'
            '/start - Main Menu\n'
            '/help - This Guide\n'
            '/balance - Check & Top Up Balance\n'
            '/referral - Referral System\n\n'
            '🎨 Image Generation:\n'
            'Use /generate to select a generation type\n\n'
            '💡 Ideas & Prompts Section:\n'
            '/ideas - Opens a showcase of ready-made prompts and examples\n\n'
            '❓ Questions?\n'
            'Message us: @MarselleGaya'
            )
    await message.answer(text)
from aiogram import Bot, types, Router, F
from aiogram.fsm.context import FSMContext
from aiogram.filters import or_f, Command
import logging

from config_data.config_data import Config, load_config
from keyboard import admin_keyboard, user_keyboard
from database.requests import admin_requests, user_requests

config: Config = load_config()
router = Router()


@router.message(or_f(F.text == '👤 Реферальная программа/referal', Command('referal')))
async def referal(message: types.Message, state: FSMContext):
    """Реферальная программа"""
    logging.info('referal')
    user_id = int(message.from_user.id)
    bot_username = config.tg_bot.bot_username
    referal_cnt = await user_requests.get_referal_cnt(user_id)

    text = (f'👤 Реферальная программа\n'
            f'👥 Вами было приглашено {referal_cnt} пользователей\n'
            f'Ваша реферальная ссылка: <code>https://t.me/{bot_username}?start=ref_{user_id}</code>\n'
            f'💰 Вы будете получать по 20% с каждого пополнения приглашенного пользователя\n\n'
            f'👤 Referral Program\n'
            f'👥 You have invited {referal_cnt} users\n'
            f'Your referral link: <code>https://t.me/{bot_username}?start=ref_{user_id}</code>\n'
            f'💰 You will receive 20% of every deposit made by an invited user'
            )

    await state.clear()
    await message.answer(text)
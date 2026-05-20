from aiogram import Bot, types, Router, F
from aiogram.filters import Command
    
import logging
from config_data.config_data import Config, load_config
from keyboard import admin_keyboard, user_keyboard
from database.requests import admin_requests, user_requests

config: Config = load_config()
router = Router()

admin_ids = str(config.tg_bot.admin_ids).split(',')

def extract_arg(arg):
    return arg.split()[1:]


@router.message(Command("start"))
async def start(message: types.Message, bot: Bot):
    """Старт"""
    logging.info('start')
    user_id = int(message.from_user.id)
    username = str(message.from_user.username)
    name = str(message.from_user.first_name)
    command = extract_arg(message.text)

    if command:
        command = command[0]
        invite_user_id = int(command.split('_')[1])

        if username:
            text = (f'👤 Реферальная программа\n'
                    f'✅Новый переход по вашей реферальной ссылке!\n'
                    f'Пользователь: @{username}\n\n'
                    f'👤 Referral Program\n'
                    f'✅ New visit via your referral link!\n'
                    f'User: @{username}')
        else:
            text = (f'👤 Реферальная программа\n'
                    f'✅Новый переход по вашей реферальной ссылке!\n\n'
                    f'👤 Referral Program\n'
                    f'✅ New visit via your referral link!\n')

        flag = await user_requests.add_new_referal(invite_user_id, user_id)
        if flag:
            await bot.send_message(chat_id=invite_user_id, text=text)

    if str(user_id) in admin_ids:
        markup = await admin_keyboard.main_admin_buttons()
        new_user = await user_requests.add_user(user_id, username)
        await message.answer('Вы админ, выберите действие:', reply_markup=markup)

    else:
        markup = await user_keyboard.main_buttons()
        new_user = await user_requests.add_user(user_id, username)

        if new_user:
            text = (f"👋 Добро пожаловать, {name}!\n\n"
                    f"Я бот Nano Banana - твой AI помощник для генерации изображений! 🎨\n"
                    f"✅ Регистрация прошла успешно!\n"
                    f"🎁 Вам начислено 100 бонусных рублей\n\n"
                    f"Что я умею:\n"
                    f"• 📝 Создавать изображения из текста\n"
                    f"• 📹 Создавать видео из текста\n"
                    f"• 🖼 Редактировать загруженные изображения\n\n\n"
                    f"👋 Welcome, {name}!\n\n"
                    f"I'm Nano Banana—your AI assistant for generating images! 🎨\n"
                    f"✅ Registration successful!\n"
                    f"🎁 You have received 100 bonus rubles.\n\n"
                    f"What I can do:\n"
                    f"• 📝 Create images from text\n"
                    f"• 📹 Create videos from text\n"
                    f"• 🖼 Edit uploaded images\n"
                    )
        else:
            text = (f"👋 Добро пожаловать, {name}!\n\n"
                    f"Я бот Nano Banana - твой AI помощник для генерации изображений! 🎨\n"
                    f"Что я умею:\n"
                    f"• 📝 Создавать изображения из текста\n"
                    f"• 📹 Создавать видео из текста\n"
                    f"• 🖼 Редактировать загруженные изображения\n\n\n"
                    f"👋 Welcome, {name}!\n\n"
                    f"I'm Nano Banana—your AI assistant for generating images! 🎨\n"
                    f"What I can do:\n"
                    f"• 📝 Create images from text\n"
                    f"• 📹 Create videos from text\n"
                    f"• 🖼 Edit uploaded images\n"
                    )

        await message.answer(text, reply_markup=markup)

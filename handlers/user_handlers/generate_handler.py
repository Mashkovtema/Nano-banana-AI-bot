from aiogram import Bot, types, Router, F
from aiogram.filters import Command, StateFilter, or_f
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup, default_state
from aiogram.types import FSInputFile
import logging
import os

from config_data.config_data import Config, load_config
from keyboard import admin_keyboard, user_keyboard
from database.requests import admin_requests, user_requests
from utils import utils

config: Config = load_config()
router = Router()


class FsmGenerate(StatesGroup):
    get_prompt = State()
    get_photo = State()


@router.message(or_f(F.text == '🎨 Генерация/Generation', Command('generate')))
async def start_generate(message: types.Message, state: FSMContext):
    """Начало генерации"""
    logging.info('start_generate')
    user_id = int(message.from_user.id)
    user_data = await user_requests.get_user_data(user_id)
    markup = await user_keyboard.select_type()

    await message.answer('Выберите режим работы 👇\n\n'
                         'Select an operating mode 👇', reply_markup=markup)
    await state.update_data(balance=user_data['balance'])


@router.callback_query(F.data.startswith('select-type_'))
async def select_type(callback: types.CallbackQuery, state: FSMContext):
    """Выбор типа генерации"""
    logging.info('select-type')
    type_ = str(callback.data).split('_')[1]
    if 'photo' in type_:
        markup = await user_keyboard.select_model_photo()
    else:
        markup = await user_keyboard.select_model_video()

    await state.update_data(type=type_)
    await callback.message.edit_text('Выберите нейросеть для генерации 👇\n\n'
                                     'Select a neural network for generation 👇', reply_markup=markup)


@router.callback_query(F.data.startswith('select-model_'))
async def select_model(callback: types.CallbackQuery, state: FSMContext):
    """Выбор модели"""
    logging.info('select_model')
    model = str(callback.data).split('_')[1]
    markup = await user_keyboard.back_button('back-generate_model')
    text = ('Отправьте текстовое описание того, что вы хотите создать 👇\n'
            'Пример: красивый закат над океаном, фотореализм\n\n'
            'Send a text description of what you want to create 👇\n'
            'Example: A beautiful sunset over the ocean, photorealistic'
            )

    await state.update_data(model=model)
    await state.set_state(FsmGenerate.get_prompt)
    await callback.message.edit_text(text=text, reply_markup=markup)


@router.message(StateFilter(FsmGenerate.get_prompt))
async def get_prompt(message: types.Message, state: FSMContext):
    """Получение промпта"""
    logging.info('get_prompt')
    prompt = str(message.text)
    state_data = await state.get_data()
    quality, format = await utils.check_data(prompt)
    cost = await utils.calculate_cost_main(state_data['type'], state_data['model'], quality, 5)

    if state_data['type'] == 'edit-photo':
        markup = await user_keyboard.back_button('back-generate_model')
        text = ('🖼 Отправьте фотографию которую хотите отредактировать\n\n'
                '🖼 Send the photo you would like to edit.')
        await state.set_state(FsmGenerate.get_photo)
        await message.answer(text=text, reply_markup=markup)

    else:
        if 'veo' in state_data['model']:
            markup = await user_keyboard.generate_settings_buttons(quality, format, state_data['type'], 4, state_data['model'])
        else:
            markup = await user_keyboard.generate_settings_buttons(quality, format, state_data['type'], 5, state_data['model'])

        text = (f'Подтвердите генерацию/Confirm generation\n\n'
                f'📝 Промпт/Prompt: {prompt}\n\n'
                f'🎨 Модель/Model: {state_data["model"]}\n'
                f'💵 Стоимость генерации/cost: {cost} руб.\n'
                f'💰 Баланс/balance: {state_data["balance"]}\n\n'
                f'⚙️ Настройте параметры и нажмите кнопку "Генерировать"\n'
                f'⚙️ Configure the settings and click the "Generate" button.')

        await message.answer(text=text, reply_markup=markup)

    await state.update_data(prompt=prompt)
    await state.update_data(quality=quality)
    await state.update_data(format=format)
    await state.update_data(cost=cost)
    await state.update_data(long=5)
    await state.update_data(file_path='')


@router.message(StateFilter(FsmGenerate.get_photo))
async def get_photo(message: types.Message, state: FSMContext, bot: Bot):
    """Получение фотографии для генерации"""
    logging.info('get_photo')
    user_id = int(message.from_user.id)
    try:
        photo_id = str(message.photo[-1].file_id)
        file_path = f'generations/{user_id}.jpg'
        file = await bot.get_file(file_id=photo_id)

        await bot.download_file(file.file_path, destination=file_path)
        await state.set_state(default_state)

        state_data = await state.get_data()
        cost = await utils.calculate_cost_main(state_data['type'], state_data['model'], state_data['quality'], state_data['long'])
        markup = await user_keyboard.generate_settings_buttons(state_data['quality'], state_data['format'], state_data['type'], state_data['long'], state_data['model'])

        text = (f'Подтвердите генерацию/Confirm generation\n\n'
                f'📝 Промпт/Prompt: {state_data["prompt"]}\n\n'
                f'🎨 Модель/Model: {state_data["model"]}\n'
                f'💵 Стоимость генерации/cost: {cost} руб.\n'
                f'💰 Баланс/balance: {state_data["balance"]}\n\n'
                f'⚙️ Настройте параметры и нажмите кнопку "Генерировать"\n'
                f'⚙️ Configure the settings and click the "Generate" button.')

        await state.update_data(cost=cost)
        await state.update_data(file_path=file_path)
        await state.update_data(file_id=photo_id)
        await message.answer_photo(photo=photo_id, caption=text, reply_markup=markup)

    except:
        await message.answer('Вы отправили не фото, попробуйте еще раз ❌')


@router.callback_query(F.data.startswith('select-settings_'))
async def select_settings_for_generate(callback: types.CallbackQuery, state: FSMContext):
    """Выбор настроек для генерации"""
    logging.info('select_settings_for_generate')
    flag = str(callback.data).split('_')[1]
    data = str(callback.data).split('_')[2]

    if flag == 'format':
        await state.update_data(format=data)
    if flag == 'quality':
        await state.update_data(quality=data)
    if flag == 'long':
        await state.update_data(long=int(data))

    state_data = await state.get_data()
    cost = await utils.calculate_cost_main(state_data['type'], state_data['model'], state_data['quality'], state_data['long'])
    markup = await user_keyboard.generate_settings_buttons(state_data['quality'], state_data['format'], state_data['type'], state_data['long'], state_data['model'])

    text = (f'Подтвердите генерацию/Confirm generation\n\n'
            f'📝 Промпт/Prompt: {state_data["prompt"]}\n\n'
            f'🎨 Модель/Model: {state_data["model"]}\n'
            f'💵 Стоимость генерации/cost: {cost} руб.\n'
            f'💰 Баланс/balance: {state_data["balance"]}\n\n'
            f'⚙️ Настройте параметры и нажмите кнопку "Генерировать"\n'
            f'⚙️ Configure the settings and click the "Generate" button.')

    await state.update_data(cost=cost)

    if state_data['type'] == 'edit-photo':
        await callback.message.edit_caption(caption=text, reply_markup=markup)
    else:
        await callback.message.edit_text(text=text, reply_markup=markup)


@router.callback_query(F.data.startswith('back-generate_'))
async def back_generate(callback: types.CallbackQuery, state: FSMContext):
    """Обработка кнопок назад"""
    logging.info('back_generate')
    flag = str(callback.data).split('_')[1]

    if flag == 'model':
        state_data = await state.get_data()
        if 'photo' in state_data['type']:
            markup = await user_keyboard.select_model_photo()
        else:
            markup = await user_keyboard.select_model_video()

        await state.set_state(default_state)
        await callback.message.edit_text('🎨 Выберите модель для генерации:\n\n'
                                         '🎨 Select a model for generation:', reply_markup=markup)

    if flag == 'prompt':
        state_data = await state.get_data()
        markup = await user_keyboard.back_button('back-generate_model')
        text = ('Отправьте текстовое описание того, что вы хотите создать 👇\n'
                'Пример: красивый закат над океаном, фотореализм\n\n'
                'Send a text description of what you want to create 👇\n'
                'Example: A beautiful sunset over the ocean, photorealistic'
                )
        await state.set_state(FsmGenerate.get_prompt)

        if state_data['type'] != 'edit-photo':
            await callback.message.edit_text(text=text, reply_markup=markup)
        else:
            await callback.message.delete()
            await callback.message.answer(text=text, reply_markup=markup)

    if flag == 'type':
        markup = await user_keyboard.select_type()
        await callback.message.edit_text('Выберите режим работы 👇\n\n'
                                         'Select an operating mode 👇', reply_markup=markup)
        await state.set_state(default_state)


@router.callback_query(F.data == 'start-generate')
async def start_generate(callback: types.CallbackQuery, state: FSMContext):
    """Начало генерации"""
    logging.info('start_generate')
    state_data = await state.get_data()

    if state_data['balance'] < state_data['cost']:
        await callback.answer('Недостаточно средств для генерации ❌\n\n'
                              'Insufficient funds for generation ❌')

    else:
        await callback.message.delete()
        await callback.message.answer('⏳ Генерация запущена/⏳ Generation started ...')
        user_id = int(callback.from_user.id)
        filename, message = await utils.start_generate(
            state_data['type'],
            state_data['model'],
            state_data['quality'],
            state_data['format'],
            state_data['prompt'],
            state_data['long'],
            user_id,
            state_data['file_path']
        )

        if filename:
            logging.info(f'Ответ ии: {message}')
            file = FSInputFile(path=filename)
            await user_requests.delete_money(user_id, state_data['cost'])

            if filename.startswith('generations/photo/'):
                await callback.message.answer_photo(photo=file, caption=message)

            if filename.startswith('generations/video/'):
                await callback.message.answer_video(video=file, caption=message)

            os.remove(filename)

        else:
            text = (f'❌ Не удалось сгенерировать изображение/error\n\n'
                    f'Для решения вопроса можете обратиться к администратору/admin link - @MarselleGaya')
            await callback.message.answer(text=text)
            await state.clear()






















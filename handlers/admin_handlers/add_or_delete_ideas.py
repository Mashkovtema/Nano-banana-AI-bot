from aiogram import Bot, types, Router, F
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup, default_state


import logging
from config_data.config_data import Config, load_config
from keyboard import admin_keyboard, user_keyboard
from database.requests import admin_requests, user_requests

config: Config = load_config()
router = Router()

admin_ids = str(config.tg_bot.admin_ids).split(',')


class FsmIdeas(StatesGroup):
    get_description = State()
    get_prompt = State()


@router.message(F.text == '📄 База идей и промптов')
async def ideas_base(message: types.Message):
    """Обновленрие идей для промптов"""
    logging.getLogger('ideas_base')
    markup = await admin_keyboard.add_or_delete()
    await message.answer('Выберите действие 👇', reply_markup=markup)

#######################################################################
########################## Добавление #################################
#######################################################################


@router.callback_query(F.data == 'add-idea')
async def add_new_idea(callback: types.CallbackQuery, state: FSMContext):
    """Добавление новой идеи для генерации"""
    logging.info('add_new_idea')
    text = ('💡 Введите промпт, например 👇\n\n'
            'Фотореалистичный романтический кадр пары на природе в золотой час. Мужчина держит девушку на руках, она обвивает его ногами за талию, они целуются. Девушка одной рукой касается его лица, создавая интимный момент.\n\n'
            'Локация: открытое поле с высокой травой, на фоне холмы и горы, мягко уходящие в перспективу. Солнце на горизонте \n\n'
            'Одежда: повседневный стиль — оверсайз джинсы, кроссовки белые массивные, футболка белая скини\n'
            'Мужчины в военной форме цвета мультикам, нашивка с флагом России на плече ')

    markup = await admin_keyboard.back_button('back-to-select-admin_select')
    await state.set_state(FsmIdeas.get_prompt)
    await callback.message.edit_text(text=text, reply_markup=markup)


@router.message(StateFilter(FsmIdeas.get_prompt))
async def get_prompt(message: types.Message, state: FSMContext):
    """Получение промпта"""
    logging.info('get_prompt')
    prompt = str(message.text)
    text = '⚡️ Введите описание промпта 👇'
    markup = await admin_keyboard.back_button('back-to-select-admin_prompt')

    await state.update_data(prompt=prompt)
    await state.set_state(FsmIdeas.get_description)
    await message.answer(text=text, reply_markup=markup)


@router.message(StateFilter(FsmIdeas.get_description))
async def get_description(message: types.Message, state: FSMContext):
    """Получение описания промпта"""
    logging.info('get_description')
    description = str(message.text)
    markup = await admin_keyboard.yes_or_no('confirm-idea')
    state_data = await state.get_data()

    text = (f'💡 Описание: {description}\n\n'
            f'🎨 Промпт: {state_data["prompt"]}\n\n'
            f'Вы уверены что хотите добавить этот промпт ?')

    await state.update_data(description=description)
    await state.set_state(default_state)
    await message.answer(text=text, reply_markup=markup)


@router.callback_query(F.data.startswith('confirm-idea_'))
async def add_or_no(callback: types.CallbackQuery, state: FSMContext):
    """Добавить идею или нет"""
    logging.info('add_or_no')
    flag = str(callback.data).split('_')[1]
    if flag == 'yes':
        state_data = await state.get_data()
        markup = await admin_keyboard.add_another()

        await admin_requests.add_new_idea(state_data['description'], state_data['prompt'])
        await callback.message.edit_text('Идея успешно добавлена ✅', reply_markup=markup)
        await state.clear()
    else:
        await state.clear()
        await callback.message.edit_text('Добавление идеи отменено ❌')


#######################################################################
########################## Удаление ###################################
#######################################################################

@router.callback_query(F.data == 'delete-idea')
async def delete_idea(callback: types.CallbackQuery, state: FSMContext):
    """Удаление идеи"""
    logging.info('delete_idea')
    ideas_data = await admin_requests.get_all_ideas()
    if ideas_data:
        markup = await admin_keyboard.ideas_pagination(ideas_data, 0)
        await callback.message.edit_text('Выберите идею для удаления 👇', reply_markup=markup)
        await state.update_data(page=0)
    else:
        await callback.answer('Идеи для удаления отсутствуют ❌')


@router.callback_query(F.data.startswith('pagination-ideas_'))
async def pagination_delete(callback: types.CallbackQuery, state: FSMContext):
    """пагинация"""
    logging.info('pagination')
    page = int(str(callback.data).split('_')[1])
    ideas_data = await admin_requests.get_all_ideas()
    markup = await admin_keyboard.ideas_pagination(ideas_data, page)

    if markup:
        await callback.message.edit_text('Выберите идею для удаления 👇', reply_markup=markup)
        await state.update_data(page=page)

    await callback.answer()


@router.callback_query(F.data.startswith('select-idea-delete_'))
async def select_idea(callback: types.CallbackQuery, state: FSMContext):
    """Выбор идеи"""
    logging.info('select_idea')
    index = int(str(callback.data).split('_')[1])
    idea_data = await admin_requests.get_idea_by_index(index)
    markup = await admin_keyboard.yes_or_no('delete-idea-or-no')

    text = (f'Идея номер {idea_data["id"]}\n\n'
            f'💡 Описание: {idea_data["description"]}\n\n'
            f'🎨 Промпт: {idea_data["prompt"]}\n\n'
             f'Вы уверены что хотите удалить эту идею?')

    await state.update_data(index=index)
    await callback.message.edit_text(text=text, reply_markup=markup)


@router.callback_query(F.data.startswith('delete-idea-or-no_'))
async def delete_idea_or_no(callback: types.CallbackQuery, state: FSMContext):
    """Удалить идею или нет"""
    logging.info('delete_idea_or_no')
    flag = str(callback.data).split('_')[1]
    state_data = await state.get_data()

    if flag == 'yes':
        index = state_data['index']
        markup = await admin_keyboard.next_button()

        await admin_requests.delete_idea(index)
        await state.clear()
        await callback.message.edit_text('Идея успешно удалена ✅', reply_markup=markup)

    else:
        page = state_data['page']
        ideas_data = await admin_requests.get_all_ideas()
        markup = await admin_keyboard.ideas_pagination(ideas_data, page)

        await callback.message.edit_text('Выберите идею для удаления 👇', reply_markup=markup)


@router.callback_query(F.data.startswith('back-to-select-admin_'))
async def back_buttons(callback: types.CallbackQuery, state: FSMContext):
    """Обработка кнопок назад"""
    logging.info('back_buttons')
    flag = str(callback.data).split('_')[1]

    if flag == 'select':
        markup = await admin_keyboard.add_or_delete()
        await callback.message.edit_text('Выберите действие 👇', reply_markup=markup)
        await state.set_state(default_state)

    if flag == 'prompt':
        text = ('💡 Введите промпт, например 👇\n\n'
                'Фотореалистичный романтический кадр пары на природе в золотой час. Мужчина держит девушку на руках, она обвивает его ногами за талию, они целуются. Девушка одной рукой касается его лица, создавая интимный момент.\n\n'
                'Локация: открытое поле с высокой травой, на фоне холмы и горы, мягко уходящие в перспективу. Солнце на горизонте \n\n'
                'Одежда: повседневный стиль — оверсайз джинсы, кроссовки белые массивные, футболка белая скини\n'
                'Мужчины в военной форме цвета мультикам, нашивка с флагом России на плече ')

        markup = await admin_keyboard.back_button('back-to-select-admin_select')
        await state.set_state(FsmIdeas.get_prompt)
        await callback.message.edit_text(text=text, reply_markup=markup)











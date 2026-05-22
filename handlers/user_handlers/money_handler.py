from aiogram import Bot, types, Router, F
from aiogram.filters import Command, StateFilter, or_f
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup, default_state

from aiohttp import web
import logging

from config_data.config_data import Config, load_config
from keyboard import admin_keyboard, user_keyboard
from database.requests import admin_requests, user_requests
from utils import utils

config: Config = load_config()
router = Router()

class MoneyFsm(StatesGroup):
    get_summ = State()


@router.message(or_f(F.text == '💳 Пополнить/Top up balance', Command('balance')))
async def money(message: types.Message, state: FSMContext):
    """Баланс"""
    logging.info('money')
    user_id = int(message.from_user.id)
    user_data = await user_requests.get_user_data(user_id)
    markup = await user_keyboard.money_buttons()

    text = (f'💰 Ваш баланс: {user_data["balance"]} 💎\n'
            f'Выберите сумму для пополнения 👇\n\n'
            f'💰 Your balance: {user_data["balance"]} 💎\n'
            f'Select an amount to top up 👇'
            )

    await state.clear()
    await message.answer(text=text, reply_markup=markup)


@router.callback_query(F.data == 'back-to-select-summ')
async def back_to_select_summ(callback: types.CallbackQuery, state: FSMContext):
    """Нзазад к выбору суммы"""
    logging.info('back_to_select_summ')
    user_id = int(callback.from_user.id)
    user_data = await user_requests.get_user_data(user_id)
    markup = await user_keyboard.money_buttons()

    text = (f'💰 Ваш баланс: {user_data["balance"]} 💎\n'
            f'Выберите сумму для пополнения 👇\n\n'
            f'💰 Your balance: {user_data["balance"]} 💎\n'
            f'Select an amount to top up 👇'
            )

    await state.clear()
    await callback.message.edit_text(text=text, reply_markup=markup)


@router.callback_query(F.data.startswith('select-money_'))
async def select_money(callback: types.CallbackQuery, state: FSMContext):
    """Получение суммы для пополнения"""
    logging.info('select_money')
    summ = str(callback.data).split('_')[1]

    if summ == 'another':
        text = (f'Введите сумму для пополнения 👇\n'
                f'(Не менее 100)\n\n'
                f'Enter the deposit amount 👇\n'
                f'(Minimum 100)'
                )

        markup = await user_keyboard.back_button('back-to-select-summ')
        await state.set_state(MoneyFsm.get_summ)
        await callback.message.edit_text(text=text, reply_markup=markup)

    else:
        text = 'Выберите валюту/select currency 👇'

        markup = await user_keyboard.select_currency(int(summ))
        await state.set_state(default_state)
        await state.update_data(summ=int(summ))
        await callback.message.edit_text(text=text, reply_markup=markup)


@router.callback_query(F.data.startswith('select-currency_'))
async def select_currency(callback: types.CallbackQuery, state: FSMContext):
    """Получение валюты"""
    logging.info('select_currency')
    currency = str(callback.data).split('_')[1]
    user_id = int(callback.from_user.id)
    state_data = await state.get_data()

    index = await user_requests.get_payment_index()
    cost_with_convertation = await utils.convert_function(state_data['summ'], currency)

    new_payment = {
        'user_id': user_id,
        'label': f'{user_id}-{index}',
        'summ': cost_with_convertation,
        'top_up_balance': state_data['summ'],
        'currency': currency
    }

    link, payment_id = await utils.create_invoice(cost_with_convertation, currency, index)

    markup = await user_keyboard.pay_button(link)
    text = (f'💵 Сумма к оплате: {cost_with_convertation} {currency}\n'
            f'Нажмите на кнопку для перехода к оплате 👇\n\n'
            f'💵 Amount due: {cost_with_convertation} {currency}\n'
            f'Click the button to proceed to payment 👇'
            )

    new_payment['label'] = payment_id

    await user_requests.add_new_payment(new_payment)
    await callback.message.edit_text(text=text, reply_markup=markup)
    await state.clear()


@router.message(StateFilter(MoneyFsm.get_summ))
async def get_summ(message: types.Message, state: FSMContext):
    """Получение суммы для пополнения"""
    logging.info('get_summ')
    try:
        summ = int(message.text)
        if summ >= 100:

            text = 'Выберите валюту/select currency 👇'

            markup = await user_keyboard.select_currency(summ)
            await state.set_state(default_state)
            await state.update_data(summ=int(summ))
            await message.answer(text=text, reply_markup=markup)

        else:
            markup = await user_keyboard.back_button('back-to-select-summ')
            await message.answer('Сумма должна быть больше 100 ❌\n\n'
                                 'The amount must be greater than 100  ❌', reply_markup=markup)
    except:
        markup = await user_keyboard.back_button('back-to-select-summ')
        await message.answer('Введена некорректная сумма для пополнения, попробуйте еще раз ❌\n\n'
                             'An invalid top-up amount was entered. Please try again. ❌', reply_markup=markup)


async def handle_webhook(request: web.Request):
    try:
        data = await request.json()
        logging.info(f"Получен вебхук: \n{data}")

        bot = request.app['bot']
        status = data['status']
        label = data['contractId']

        if status == 'completed' or status == 'success':
            summ, user_id = await user_requests.process_payment(label)
            check_invite = await user_requests.add_referal_money(user_id, summ)

            if summ != 0:
                text = (f'✅ Ваш баланс успешно пополнен на {summ} 💎\n\n'
                        f'✅ Your balance has been successfully topped up by {summ} 💎')
                await bot.send_message(chat_id=user_id, text=text)

            if check_invite != 0:
                text = (f'✅ Ваш баланс успешно пополнен на {int(summ * 0.2)} 💎 за приглашенного пользователя\n\n'
                        f'✅ Your balance has been successfully topped up by {int(summ * 0.2)} 💎 for an invited user.')
                await bot.send_message(chat_id=check_invite, text=text)

        return web.Response(status=200, text="OK")


    except Exception as e:
        logging.error(f"Ошибка при обработке вебхука: {e}")
        return web.Response(status=400, text="Invalid data format or processing error")  # Возвращаем код ошибки
















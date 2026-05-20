from aiogram import Bot, types, Router, F
from aiogram.filters import Command, StateFilter, or_f
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup, default_state

from yoomoney import Quickpay
from aiohttp import web
import logging

from config_data.config_data import Config, load_config
from keyboard import admin_keyboard, user_keyboard
from database.requests import admin_requests, user_requests

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

    text = (f'💰 Ваш баланс: {user_data["balance"]} Руб\n\n'
            f'Выберите сумму для пополнения 👇\n\n\n'
            f'💰 Your balance: {user_data["balance"]} RUB\n\n'
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

    text = (f'💰 Ваш баланс: {user_data["balance"]} Руб\n\n'
            f'Выберите сумму для пополнения 👇\n\n\n'
            f'💰 Your balance: {user_data["balance"]} RUB\n\n'
            f'Select an amount to top up 👇'
            )

    await state.clear()
    await callback.message.edit_text(text=text, reply_markup=markup)


@router.callback_query(F.data.startswith('select-money_'))
async def select_money(callback: types.CallbackQuery, state: FSMContext):
    """Выбор суммы для пополнения"""
    logging.info('select_money')
    summ = str(callback.data).split('_')[1]
    user_id = int(callback.from_user.id)
    if summ == 'another':
        text = (f'Введите сумму для пополнения 👇\n'
                f'(Не менее 100р)\n\n'
                f'Enter the deposit amount 👇\n'
                f'(Minimum 100 RUB)'
                )

        markup = await user_keyboard.back_button('back-to-select-summ')
        await state.set_state(MoneyFsm.get_summ)
        await callback.message.edit_text(text=text, reply_markup=markup)
    else:
        summ = int(summ)
        index = await user_requests.get_payment_index()
        new_payment = {
            'user_id': user_id,
            'label': f'{user_id}-{index}',
            'summ': summ,
        }

        link = Quickpay(
            receiver=config.tg_bot.yoomoney_receiver,
            quickpay_form='shop',
            targets=f'Оплата токенов в боте на сумму {summ}р',
            paymentType='SB',
            sum=new_payment['summ'],
            label=new_payment['label']
        ).base_url

        markup = await user_keyboard.pay_button(link)
        text = (f'💵 Сумма к оплате: {summ}р\n\n'
                f'Нажмите на кнопку для перехода к оплате 👇\n\n\n'
                f'💵 Amount due: {summ} RUB\n\n' 
                f'Click the button to proceed to payment 👇'
                )

        await user_requests.add_new_payment(new_payment)
        await callback.message.edit_text(text=text, reply_markup=markup)
        await state.clear()


@router.message(StateFilter(MoneyFsm.get_summ))
async def get_summ(message: types.Message, state: FSMContext):
    """Получение суммы для пополнения"""
    logging.info('get_summ')
    try:
        summ = int(message.text)
        user_id = int(message.from_user.id)
        if summ >= 100:

            index = await user_requests.get_payment_index()
            new_payment = {
                'user_id': user_id,
                'label': f'{user_id}-{index}',
                'summ': summ,
            }

            link = Quickpay(
                receiver=config.tg_bot.yoomoney_receiver,
                quickpay_form='shop',
                targets=f'Оплата токенов в боте на сумму {summ}р',
                paymentType='SB',
                sum=new_payment['summ'],
                label=new_payment['label']
            ).base_url

            markup = await user_keyboard.pay_button(link)
            text = (f'💵 Сумма к оплате: {summ}р\n\n'
                    f'Нажмите на кнопку для перехода к оплате 👇\n\n\n'
                    f'💵 Amount due: {summ} RUB\n\n' 
                    f'Click the button to proceed to payment 👇'
                    )

            await user_requests.add_new_payment(new_payment)
            await message.answer(text=text, reply_markup=markup)
            await state.clear()

        else:
            markup = await user_keyboard.back_button('back-to-select-summ')
            await message.answer('Сумма должна быть больше 100р ❌\n\n'
                                 'The amount must be greater than 100 RUB ❌', reply_markup=markup)
    except:
        markup = await user_keyboard.back_button('back-to-select-summ')
        await message.answer('Введена некорректная сумма для пополнения, попробуйте еще раз ❌\n\n'
                             'An invalid top-up amount was entered. Please try again. ❌', reply_markup=markup)


async def handle_webhook(request: web.Request):
    try:
        data = await request.post()
        logging.info(f"Получен вебхук: \n{data}")

        bot = request.app['bot']
        label = data.get('label')

        summ, user_id = await user_requests.process_payment(label)
        check_invite = await user_requests.add_referal_money(user_id, summ)

        if summ != 0:
            text = (f'✅ Ваш баланс успешно пополнен на {summ}р\n\n'
                    f'✅ Your balance has been successfully topped up by {summ} RUB.')
            await bot.send_message(chat_id=user_id, text=text)

        if check_invite != 0:
            text = (f'✅ Ваш баланс успешно пополнен на {int(summ * 0.2)}р за приглашенного пользователя\n\n'
                    f'✅ Your balance has been successfully topped up by {int(summ * 0.2)} RUB for an invited user.')
            await bot.send_message(chat_id=check_invite, text=text)

        return web.Response(status=200, text="OK")


    except Exception as e:
        logging.error(f"Ошибка при обработке вебхука: {e}")
        return web.Response(status=400, text="Invalid data format or processing error")  # Возвращаем код ошибки
















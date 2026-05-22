from database.models import async_session, Users, Ideas, Payments, Referal
from sqlalchemy import select, or_, and_, delete, func, case, cast, Integer, String
import logging


async def add_user(user_id: int, username: str) -> bool:
    """Проерка наличия пользователя в бд"""
    logging.info('add_user')
    async with async_session() as session:
        check = await session.scalar(select(Users).where(Users.user_id == user_id))
        if not check:
            new_user = Users(
                user_id=user_id,
                username=username
            )
            session.add(new_user)
            await session.commit()

            return True
        else:
            return False


async def get_user_data(user_id: int) -> dict:
    """Получение информации о пользователе"""
    logging.info('get_user_data')
    async with async_session() as session:
        user_data = await session.scalar(select(Users).where(Users.user_id == user_id))
        user_data = user_data.__dict__
        return user_data


async def get_ideas() -> list:
    """Получение списка идей для генераций"""
    logging.info('get_ideas')
    async with async_session() as session:
        ideas_data = await session.scalars(select(Ideas))
        if ideas_data:
            ideas_data = ideas_data.all()
            return ideas_data[::-1]
        else:
            return []


async def get_payment_index() -> int:
    """Получение индекса платежа"""
    logging.info('get_payment_index')
    async with async_session() as session:
        payments = await session.scalars(select(Payments.id))
        payments = payments.all()
        if payments:
            index = max(payments) + 1
        else:
            index = 1

        return index


async def add_new_payment(data: dict) -> None:
    """Добавление нового платежа"""
    logging.info('add_new_payment')
    async with async_session() as session:
        new_payment = Payments(**data)
        session.add(new_payment)
        await session.commit()


async def process_payment(label: str):
    """Проверка платежа"""
    logging.info('process_payment')
    async with async_session() as session:
        payment = await session.scalar(select(Payments).where(Payments.label == label))
        user_id = payment.user_id

        user_data = await session.scalar(select(Users).where(Users.user_id == user_id))

        if payment.status != 'Оплачено':
            payment_summ = payment.top_up_balance
            user_data.balance += payment_summ
            payment.status = 'Оплачено'

            await session.commit()
            return payment_summ, user_id

        else:
            return 0, user_id


async def add_referal_money(invited_user_id: int, summ: int) -> int:
    """Начисление вознаграждения за реферала"""
    logging.info('add_referal_money')
    async with async_session() as session:
        user_id = await session.scalar(select(Referal.user_id).where(Referal.invited_user_id == invited_user_id))
        if user_id:
            user_data = await session.scalar(select(Users).where(Users.user_id == user_id))
            user_data.balance += int(summ * 0.2)
            await session.commit()
            return user_id
        else:
            return 0


async def add_new_referal(user_id: int, invited_user_id: int) -> bool:
    """Запись новой рефералки"""
    logging.info('add_new_referal')
    async with async_session() as session:
        if user_id != invited_user_id:
            check = await session.scalar(select(Referal).where(Referal.user_id == user_id, Referal.invited_user_id == invited_user_id))

            if not check:
                new_referal = Referal(
                    user_id=user_id,
                    invited_user_id=invited_user_id
                )
                session.add(new_referal)
                await session.commit()

                return True
            else:
                return False
        else:
            return False


async def get_referal_cnt(user_id: int) -> int:
    """получение кол-ва приглашенных пользователей"""
    logging.info('get_referal_cnt')
    async with async_session() as session:
        user_invite_data = await session.scalars(select(Referal).where(Referal.user_id == user_id))
        user_invite_data = user_invite_data.all()
        return len(user_invite_data)


async def delete_money(user_id: int, cost: int) -> None:
    """Списание средств с баланса"""
    logging.info('delete_money')
    async with async_session() as session:
        user_data = await session.scalar(select(Users).where(Users.user_id == user_id))
        user_data.balance -= cost
        await session.commit()














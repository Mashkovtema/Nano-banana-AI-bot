from database.models import async_session, Users, Ideas
from sqlalchemy import select, or_, and_, delete, func, case, cast, Integer, String
import logging


async def add_new_idea(description: str, prompt: str) -> None:
    """Добавление новой идеи для генерации"""
    logging.getLogger('add_new_idea')
    async with async_session() as session:
        new_idea = Ideas(
            description=description,
            prompt=prompt
        )
        session.add(new_idea)
        await session.commit()


async def delete_idea(id: int) -> None:
    """Удаление идеи"""
    logging.info('delete_idea')
    async with async_session() as session:
        idea = await session.scalar(select(Ideas).where(Ideas.id == id))
        await session.delete(idea)
        await session.commit()


async def get_idea_by_index(index: str) -> dict:
    """Получение идеи по ее id"""
    logging.info('get_idea_by_index')
    async with async_session() as session:
        idea = await session.scalar(select(Ideas).where(Ideas.id == index))
        return idea.__dict__


async def get_all_ideas() -> list:
    """Получение списка всех идей"""
    logging.info('get_all_ideas')
    async with async_session() as session:
        data = await session.scalars(select(Ideas))
        if data:
            return data.all()
        else:
            return []
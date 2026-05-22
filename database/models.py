from sqlalchemy import String, Integer, Boolean, BigInteger, MetaData, Table, select
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, sessionmaker
from sqlalchemy.ext.asyncio import AsyncAttrs, async_sessionmaker, create_async_engine, AsyncSession


engine = create_async_engine("sqlite+aiosqlite:///database/database.sql")

async_session = async_sessionmaker(engine)


class Base(AsyncAttrs, DeclarativeBase):
    pass


class Users(Base):
    __tablename__ = 'Users'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(BigInteger, default=0)
    username: Mapped[str] = mapped_column(String, default='---')
    balance: Mapped[int] = mapped_column(Integer, default=100)


class Ideas(Base):
    __tablename__ = 'Ideas'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    description: Mapped[str] = mapped_column(String, default='---')
    prompt: Mapped[str] = mapped_column(String, default='---')


class Payments(Base):
    __tablename__ = 'Payments'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(BigInteger, default=0)
    label: Mapped[str] = mapped_column(String, default='---')
    summ: Mapped[int] = mapped_column(Integer, default=0)
    top_up_balance: Mapped[int] = mapped_column(Integer, default=0)
    currency: Mapped[str] = mapped_column(String, default='---')
    status: Mapped[str] = mapped_column(String, default='Не оплачено')


class Referal(Base):
    __tablename__ = 'Referal'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(BigInteger, default=0)
    invited_user_id: Mapped[int] = mapped_column(BigInteger, default=0)




async def async_main():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
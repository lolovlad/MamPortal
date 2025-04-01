from sqlalchemy import select, func
from asyncio import run
from server.database import async_session
from server.tables import (User,
                           TypeUser,
                           City,
                           StateEvent,
                           )
from uuid import uuid4


async def create_user_contest():
    async with async_session() as session:
        try:
            response = select(func.count(User.id))
            result = await session.execute(response)
            count = result.scalars().first()
            if count == 0:
                admin_type = TypeUser(
                    name="admin",
                    description=""
                )
                user_type = TypeUser(
                    name="user",
                    description=""
                )
                session.add(admin_type)
                session.add(user_type)
                await session.commit()
                admin_user = User(
                    email="lll-ooo-2003@mail.ru",
                    id_type=admin_type.id
                )
                admin_user.password = "admin"
                session.add(admin_user)
                await session.commit()
        finally:
            await session.close()


async def create_city_context():
    async with async_session() as session:
        try:
            response = select(func.count(City.id))
            result = await session.execute(response)
            count = result.scalars().first()
            if count == 0:
                city_1 = City(
                    name="Москва",
                    region="Московская область"
                )
                city_2 = City(
                    name="Астрахань",
                    region="Астраханска область"
                )

                session.add(city_1)
                session.add(city_2)
                await session.commit()
        finally:
            await session.close()


async def create_state_event_context():
    async with async_session() as session:
        try:
            response = select(func.count(StateEvent.id))
            result = await session.execute(response)
            count = result.scalars().first()
            if count == 0:
                state_1 = StateEvent(
                    name="opened",
                    description="Открыта регистрация"
                )
                state_2 = StateEvent(
                    name="closed",
                    description="Закрыта регистрация"
                )
                state_3 = StateEvent(
                    name="passed",
                    description="Прошел"
                )

                session.add(state_1)
                session.add(state_2)
                session.add(state_3)
                await session.commit()
        finally:
            await session.close()


async def main():
    await create_user_contest()
    await create_city_context()
    await create_state_event_context()

run(main())
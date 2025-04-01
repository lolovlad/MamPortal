from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from ..tables import PregnancyCalendar, User
from ..database import get_session
from sqlalchemy.orm.attributes import flag_modified

from fastapi import Depends


class CalendarRepository:
    def __init__(self, session: AsyncSession = Depends(get_session)):
        self.__session: AsyncSession = session

    async def get_calendary_by_uuid_user(self, uuid_user: str) -> PregnancyCalendar | None:
        response = select(PregnancyCalendar).join(User).where(User.uuid == uuid_user)
        result = await self.__session.execute(response)
        return result.scalars().first()

    async def get_calendary_by_uuid(self, uuid_calendar: str) -> PregnancyCalendar | None:
        response = select(PregnancyCalendar).where(PregnancyCalendar.uuid == uuid_calendar)
        result = await self.__session.execute(response)
        return result.scalars().first()

    async def add(self, target: PregnancyCalendar):
        try:
            self.__session.add(target)
            await self.__session.commit()
        except:
            await self.__session.rollback()
            raise Exception

    async def update(self, target: PregnancyCalendar):
        flag_modified(target, "calendar")
        try:
            self.__session.add(target)
            await self.__session.commit()
        except:
            await self.__session.rollback()
            raise Exception
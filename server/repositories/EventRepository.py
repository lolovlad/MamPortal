from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, desc
from ..tables import Event, Tag, UserToEvent, StateEvent, User, TagEvent
from ..database import get_session
from fastapi import Depends


class EventRepository:
    def __init__(self, session: AsyncSession = Depends(get_session)):
        self.__session: AsyncSession = session

    async def count_row(self, tags_list: list[int] | None, city: int | None) -> int:
        response = select(func.count(Event.id)).join(TagEvent)
        if tags_list is not None:
            response = response.where(TagEvent.id_tag.in_(tags_list))
        if city is not None:
            response = response.where(Event.id_city == city)
        result = await self.__session.execute(response)
        return result.scalars().first()

    async def get_all_state_event(self) -> list[StateEvent]:
        response = select(StateEvent)
        result = await self.__session.execute(response)
        return result.scalars().all()

    async def get_state_event_by_name(self, name: str) -> StateEvent:
        response = select(StateEvent).where(StateEvent.name == name)
        result = await self.__session.execute(response)
        return result.scalars().first()

    async def add(self, target: Event):
        try:
            self.__session.add(target)
            await self.__session.commit()
        except:
            await self.__session.rollback()
            raise Exception

    async def get_limit_event(self,
                              start: int,
                              end: int,
                              tags_list: list[int] | None,
                              city: int | None
                              ) -> list[Event]:
        response = select(Event).join(StateEvent).join(TagEvent, TagEvent.id_event == Event.id).order_by(desc(Event.date_conducting))
        if tags_list is not None:
            response = response.where(TagEvent.id_tag.in_(tags_list))
        if city is not None:
            response = response.where(Event.id_city == city)

        response = response.offset(start).limit(end)
        result = await self.__session.execute(response)
        return result.unique().scalars().all()

    async def get_event_by_uuid(self, uuid: str) -> Event:
        response = select(Event).where(Event.uuid == uuid)
        result = await self.__session.execute(response)
        return result.unique().scalars().one()

    async def get_event_by_search(self, name: str, count: int) -> list[Event]:
        response = select(Event).where(and_(
            Event.name.ilike(f'%{name}%'),
        )).order_by(desc(Event.date_conducting).limit(count))
        result = await self.__session.execute(response)
        return result.unique().scalars().all()

    async def delete(self, target: Event):
        try:
            await self.__session.delete(target)
            await self.__session.commit()
        except Exception:
            await self.__session.rollback()

    async def update(self, entity: Event):
        try:
            self.__session.add(entity)
            await self.__session.commit()
        except:
            await self.__session.rollback()
            raise Exception

    async def get_user_reg_by_user_and_event(self, uuid_event: str, uuid_user: str) -> UserToEvent | None:
        user_liked = select(UserToEvent).join(Event).join(User, User.id == UserToEvent.id_user).where(User.uuid == uuid_user).where(
            Event.uuid == uuid_event)
        result = await self.__session.execute(user_liked)
        return result.scalars().first()

    async def get_user_reg_info_by_uuid(self, uuid_event: str, uuid_user: str):
        t = await self.get_event_by_uuid(uuid_event)
        user_count = len(t.users)
        info = await self.get_user_reg_by_user_and_event(uuid_event, uuid_user) is not None

        return {"user_count": user_count, "is_user": info}

    async def add_user_reg(self, id_event: int, id_user: int):
        target = UserToEvent(
            id_event=id_event,
            id_user=id_user
        )
        try:
            self.__session.add(target)
            await self.__session.commit()
        except:
            await self.__session.rollback()
            raise Exception

    async def delete_user_reg(self, uuid_event: str, uuid_user: str):
        target = await self.get_user_reg_by_user_and_event(uuid_event, uuid_user)
        try:
            await self.__session.delete(target)
            await self.__session.commit()
        except Exception:
            await self.__session.rollback()

    async def count_row_by_user(self, uuid_user: str) -> int:
        response = select(func.count(Event.id)).join(UserToEvent).join(User, User.id == UserToEvent.id_user).where(uuid_user == User.uuid)
        result = await self.__session.execute(response)
        return result.scalars().first()

    async def get_limit_event_by_user(self, uuid_user: str, start: int, end: int) -> list[Event]:
        response = (select(Event)
                    .join(StateEvent)
                    .join(UserToEvent, Event.id == UserToEvent.id_event)
                    .join(User, User.id == UserToEvent.id_user)
                    .where(uuid_user == User.uuid)
                    .order_by(desc(Event.date_conducting)).offset(start).limit(end))
        result = await self.__session.execute(response)
        return result.unique().scalars().all()
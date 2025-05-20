from fastapi import Depends

from ..repositories import EventRepository, UserRepository, EnvRepository
from ..models.User import UserGet
from ..models.Event import *
from ..tables import Event
from datetime import datetime


class EventService:
    def __init__(self,
                 event_rep: EventRepository = Depends(),
                 user_rep: UserRepository = Depends(),
                 env_rep: EnvRepository = Depends()):
        self.__event_rep: EventRepository = event_rep
        self.__user_repo: UserRepository = user_rep
        self.__env_repo: EnvRepository = env_rep
        #self.__file_repo: FileBucketRepository = FileBucketRepository("user")
        self.__count_item: int = 20

    @property
    def count_item(self) -> int:
        return self.__count_item

    @count_item.setter
    def count_item(self, item):
        self.__count_item = item

    async def get_count_page(self, tags: str | None, city: int | None) -> int:
        tags_list = tags
        if tags is not None:
            tags_list = list(map(int, tags.split(",")))

        count_row = await self.__event_rep.count_row(tags_list, city)
        sub_page = 0
        if count_row % self.__count_item > 0:
            sub_page += 1
        return count_row // self.__count_item + sub_page

    async def create_event(self, target: PostEvent):
        state = await self.__event_rep.get_state_event_by_name("opened")
        tags = await self.__env_repo.get_tags_by_id_set(target.tags)

        entity = Event(
            date_conducting=target.date_conducting,
            date_stop=target.date_stop,
            id_city=target.id_city,
            address=target.address,
            description_lite=target.description_lite,
            name=target.name,
            description=target.description.encode("utf-8"),
            id_state=state.id

        )
        entity.tags.extend(tags)
        await self.__event_rep.add(entity)
        return entity

    async def get_state_event(self) -> list[GetState]:
        target = await self.__event_rep.get_all_state_event()
        return [GetState.model_validate(i, from_attributes=True) for i in target]

    async def get_page_event(self,
                             num_page: int,
                             tags: str | None,
                             city: int | None) -> list[GetLiteEvent]:
        tags_list = tags
        if tags is not None:
            tags_list = list(map(int, tags.split(",")))

        start = (num_page - 1) * self.__count_item
        events_entity = await self.__event_rep.get_limit_event(start, self.__count_item, tags_list, city)
        events = [GetLiteEvent.model_validate(entity, from_attributes=True) for entity in events_entity]
        return events

    async def get_event(self, uuid: str) -> GetEvent | None:
        target = await self.__event_rep.get_event_by_uuid(uuid)
        if target is None:
            return None
        return GetEvent.model_validate(target, from_attributes=True)

    async def get_event_by_search(self, search_field: str, count: int) -> list[GetLiteEvent]:
        events_entity = await self.__event_rep.get_event_by_search(search_field, count)
        events = [GetLiteEvent.model_validate(entity, from_attributes=True) for entity in events_entity]
        return events

    async def delete_event(self, uuid_event: str):
        target = await self.__event_rep.get_event_by_uuid(uuid_event)
        target.tags = []
        target.users = []
        await self.__event_rep.update(target)
        await self.__event_rep.delete(target)

    async def update_event(self, uuid_event: str, target: UpdateEvent):
        entity = await self.__event_rep.get_event_by_uuid(uuid_event)
        entity.tags = []
        await self.__event_rep.update(entity)

        tags = await self.__env_repo.get_tags_by_id_set(target.tags)

        event_dict = target.model_dump()

        for key in event_dict:
            if key == "description":
                setattr(entity, key, event_dict[key].encode())
            elif key == "tags":
                entity.tags = tags
            else:
                setattr(entity, key, event_dict[key])

        try:
            await self.__event_rep.update(entity)
        except Exception:
            raise Exception

    async def get_user_registration_info(self, uuid_event: str, uuid_user: str) -> UserRegInfo | None:
        if uuid_user == "no":
            t = await self.__event_rep.get_event_by_uuid(uuid_event)
            target = len(t.users)
            t = UserRegInfo(
                count=target,
                youLike=False
            )
            return t
        else:
            target = await self.__event_rep.get_user_reg_info_by_uuid(uuid_event, uuid_user)
            if target is None:
                return None
            t = UserRegInfo(
                count=target["user_count"],
                youReg=target["is_user"]
            )
            return t

    async def add_user_reg(self, uuid_event: str, uuid_user: str):
        event = await self.__event_rep.get_event_by_uuid(uuid_event)
        user = await self.__user_repo.get_user_by_uuid(uuid_user)
        await self.__event_rep.add_user_reg(event.id, user.id)

    async def delete_user_reg(self, uuid_event: str, uuid_user: str) -> list[UserGet]:
        await self.__event_rep.delete_user_reg(uuid_event, uuid_user)
        event = await self.__event_rep.get_event_by_uuid(uuid_event)
        return [UserGet.model_validate(i, from_attributes=True) for i in event.users]

    async def get_count_page_by_user(self, uuid_user: str) -> int:
        count_row = await self.__event_rep.count_row_by_user(uuid_user)
        sub_page = 0
        if count_row % self.__count_item > 0:
            sub_page += 1
        return count_row // self.__count_item + sub_page

    async def get_page_event_by_user(self, uuid_user: str, num_page: int) -> list[GetLiteEvent]:
        start = (num_page - 1) * self.__count_item
        events_entity = await self.__event_rep.get_limit_event_by_user(uuid_user, start, self.__count_item)
        events = [GetLiteEvent.model_validate(entity, from_attributes=True) for entity in events_entity]
        return events

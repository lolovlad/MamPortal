from fastapi import Depends, UploadFile

from ..repositories import FileBucketRepository, CalendarRepository, UserRepository
from ..models.Calendar import *
from ..tables import PregnancyCalendar
from uuid import uuid4

from datetime import timedelta


class CalendarService:
    def __init__(self,
                 calendar_rep: CalendarRepository = Depends(),
                 user_rep: UserRepository = Depends()):
        self.__calendar_repo: CalendarRepository = calendar_rep
        self.__user_rep: UserRepository = user_rep
        self.__file_repo: FileBucketRepository = FileBucketRepository("calendar")
        self.__count_item: int = 20

    async def get_calendar_by_uuid_user(self, uuid_user: str) -> GetPregnancyCalendar | None:
        target = await self.__calendar_repo.get_calendary_by_uuid_user(uuid_user)
        if target is None:
            return None

        return GetPregnancyCalendar.model_validate(target, from_attributes=True)

    async def create_calendar(self, uuid_user: str, target: PostPregnancyCalendar):
        user = await self.__user_rep.get_user_by_uuid(uuid_user)

        date_end = target.date_start + timedelta(days=280)

        entity = PregnancyCalendar(
            id_user=user.id,
            name=target.name,
            date_start=target.date_start - timedelta(days=60),
            date_end=date_end + timedelta(days=30),
            calendar={}
        )

        await self.__calendar_repo.add(entity)

    async def add_calendar_item(self, uuid_calendar: str, img: UploadFile, target: PostCalendarItem):
        calendar = await self.__calendar_repo.get_calendary_by_uuid(uuid_calendar)
        cl = calendar.calendar

        ext = img.filename.split(".")[1]
        dir_name = f"{calendar.uuid}/{str(uuid4())}"
        file_key = f"{dir_name}.{ext}"
        content = await img.read()
        await self.__file_repo.upload_file(file_key,
                                           content,
                                           img.content_type)

        cl[target.date.strftime("%Y-%m-%d")] = {
            "date": target.date.strftime("%Y-%m-%d"),
            "name": target.name,
            "description": target.description,
            "img": f"http://localhost:9000/calendar/{file_key}"
        }

        calendar.calendar = cl

        await self.__calendar_repo.update(calendar)

    async def update_calendar_item(self, uuid_calendar: str, img: UploadFile | None, target: UpdateCalendarItem):
        calendar = await self.__calendar_repo.get_calendary_by_uuid(uuid_calendar)
        cl = calendar.calendar

        item = cl[target.date.strftime("%Y-%m-%d")]
        if img is not None:
            name_img = '/'.join(item["img"].split("/")[-2:])
            await self.__file_repo.delete_file(name_img)
            ext = img.filename.split(".")[1]
            dir_name = f"{calendar.uuid}/{str(uuid4())}"
            file_key = f"{dir_name}.{ext}"
            content = await img.read()
            await self.__file_repo.upload_file(file_key,
                                               content,
                                               img.content_type)

            item["img"] = f"http://localhost:9000/calendar/{file_key}"

        item["name"] = target.name
        item["description"] = target.description
        calendar.calendar = cl

        await self.__calendar_repo.update(calendar)

    async def delete_calendar_item(self, uuid_calendar: str, date: str):
        calendar = await self.__calendar_repo.get_calendary_by_uuid(uuid_calendar)
        cl = calendar.calendar
        name_img = '/'.join(cl[date]["img"].split("/")[-2:])
        await self.__file_repo.delete_file(name_img)
        del cl[date]

        calendar.calendar = cl

        await self.__calendar_repo.update(calendar)



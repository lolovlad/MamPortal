from pydantic import BaseModel, UUID4, field_serializer
from datetime import datetime


class BasePregnancyCalendar(BaseModel):
    name: str
    date_start: datetime | None = None


class GetPregnancyCalendar(BasePregnancyCalendar):
    uuid: UUID4
    date_end: datetime
    calendar: dict

    @field_serializer('uuid')
    def serialize_uuid(self, uuid: UUID4, _info):
        return str(uuid)


class PostPregnancyCalendar(BasePregnancyCalendar):
    pass


class PostCalendarItem(BaseModel):
    name: str | None
    date: datetime | None
    description: str | None


class UpdateCalendarItem(PostCalendarItem):
    pass

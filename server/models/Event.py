from pydantic import BaseModel, UUID4, field_serializer
from .Env import GetTag, GetCity
from .User import UserGet
from datetime import datetime


class GetState(BaseModel):
    id: int
    name: str
    description: str


class BaseEvent(BaseModel):
    name: str
    date_conducting: datetime
    date_stop: datetime
    id_city: int
    address: str
    name: str
    description_lite: str


class PostEvent(BaseEvent):
    tags: list[int]
    description: str
    id_state: int


class GetLiteEvent(BaseEvent):
    uuid: UUID4
    city: GetCity
    tags: list[GetTag]
    state: GetState

    @field_serializer('uuid')
    def serialize_uuid(self, uuid: UUID4, _info):
        return str(uuid)


class GetEvent(GetLiteEvent):
    description: str
    users: list[UserGet]


class UpdateEvent(BaseEvent):
    tags: list[int]
    description: str
    id_state: int


class UserRegInfo(BaseModel):
    count: int
    youReg: bool




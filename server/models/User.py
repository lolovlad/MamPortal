from pydantic import BaseModel, UUID4, field_serializer
from datetime import datetime, date


class TypeUser(BaseModel):
    name: str
    description: str | None = ""


class GetTypeUser(TypeUser):
    id: int


class UserBase(BaseModel):
    email: str | None
    id_type: int
    name: str | None
    surname: str | None
    patronymic: str | None
    phone: str | None
    mood_emoji: str | None
    city: str | None
    birth_date: date | None

    @field_serializer("birth_date")
    def serialize_birth_date(self, birth_date: date | None, _info):
        return birth_date.isoformat() if birth_date else None


class UserGet(UserBase):
    uuid: UUID4
    type: GetTypeUser
    icon: str | None

    @field_serializer('uuid')
    def serialize_uuid(self, uuid: UUID4, _info):
        return str(uuid)

    @field_serializer('icon')
    def serialize_icon(self, icon: str, _info):
        return f"http://localhost:9000/icon/{icon}"


class UserPost(UserBase):
    password: str


class UserUpdate(UserBase):
    password: str | None = None


class PasswordUpdate(BaseModel):
    old: str
    new: str
    confirm: str

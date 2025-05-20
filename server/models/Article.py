from pydantic import BaseModel, UUID4, field_serializer
from .Env import GetTag, GetTypeArticle
from .User import UserGet
from datetime import datetime


class BaseArticle(BaseModel):
    name: str
    description_lite: str
    id_type: int


class PostArticle(BaseArticle):
    tags: list[int]
    description: str


class GetArticle(BaseArticle):
    uuid: UUID4
    autor: UserGet
    date_publications: datetime
    type: GetTypeArticle
    description: str
    tags: list[GetTag]

    @field_serializer('uuid')
    def serialize_uuid(self, uuid: UUID4, _info):
        return str(uuid)


class GetLiteArticle(BaseArticle):
    uuid: UUID4
    autor: UserGet
    date_publications: datetime
    type: GetTypeArticle
    tags: list[GetTag]

    @field_serializer('uuid')
    def serialize_uuid(self, uuid: UUID4, _info):
        return str(uuid)


class UpdateArticle(BaseArticle):
    tags: list[int]
    description: str


class GetCommentary(BaseModel):
    uuid: UUID4
    user: UserGet
    content: str
    date_publications: datetime

    @field_serializer('uuid')
    def serialize_uuid(self, uuid: UUID4, _info):
        return str(uuid)


class LikeInfo(BaseModel):
    count: int
    youLike: bool


class PostComment(BaseModel):
    content: str

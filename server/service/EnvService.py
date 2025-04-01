from fastapi import Depends, UploadFile

from ..repositories import EnvRepository
from ..models.Env import *
from ..tables import City, Tag, TypeArticle


class EnvService:
    def __init__(self, env_rep: EnvRepository = Depends()):
        self.__env_repo: EnvRepository = env_rep
        #self.__file_repo: FileBucketRepository = FileBucketRepository("user")

    async def get_all_city(self) -> list[GetCity]:
        target = await self.__env_repo.get_all_city()
        return [GetCity.model_validate(i, from_attributes=True) for i in target]

    async def create_city(self, target: PostCity):
        entity = City(
            name=target.name,
            region=target.region,
        )
        try:
            await self.__env_repo.add(entity)
        except Exception:
            raise Exception

    async def get_one_city(self, id_city: int) -> GetCity:
        target = await self.__env_repo.get_city_by_id(id_city)
        return GetCity.model_validate(target, from_attributes=True)

    async def update_city(self, id_city: int, target: PutCity):
        entity = await self.__env_repo.get_city_by_id(id_city)
        entity.name = target.name
        entity.region = target.region

        await self.__env_repo.update(entity)

    async def get_all_type_article(self) -> list[GetTypeArticle]:
        target = await self.__env_repo.get_all_type_article()
        return [GetTypeArticle.model_validate(i, from_attributes=True) for i in target]

    async def create_type_article(self, target: PostTypeArticle):
        entity = TypeArticle(
            name=target.name,
            description=target.description,
        )
        try:
            await self.__env_repo.add(entity)
        except Exception:
            raise Exception

    async def get_one_type_article(self, id_type_article: int) -> GetTypeArticle:
        target = await self.__env_repo.get_type_article_by_id(id_type_article)
        return GetTypeArticle.model_validate(target, from_attributes=True)

    async def update_type_article(self, id_type_article: int, target: PutTypeArticle):
        entity = await self.__env_repo.get_type_article_by_id(id_type_article)
        entity.name = target.name
        entity.description = target.description

        await self.__env_repo.update(entity)

    async def get_all_tag(self) -> list[GetTag]:
        target = await self.__env_repo.get_all_tag()
        return [GetTag.model_validate(i, from_attributes=True) for i in target]

    async def create_tag(self, target: PostTag):
        entity = Tag(
            name=target.name,
            description=target.description,
        )
        try:
            await self.__env_repo.add(entity)
        except Exception:
            raise Exception

    async def get_one_tag(self, id_tag: int) -> GetTag:
        target = await self.__env_repo.get_tag_by_id(id_tag)
        return GetTag.model_validate(target, from_attributes=True)

    async def update_tag(self, id_tag: int, target: PutTag):
        entity = await self.__env_repo.get_tag_by_id(id_tag)
        entity.name = target.name
        entity.description = target.description

        await self.__env_repo.update(entity)

    async def get_tags_by_search(self, search_field: str, count: int) -> list[GetTag]:
        tags = await self.__env_repo.get_tags_by_search_field(
            search_field,
            count
        )
        tags = [GetTag.model_validate(entity, from_attributes=True) for entity in tags]
        return tags
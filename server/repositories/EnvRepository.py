from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from ..tables import City, TypeArticle, Tag
from ..database import get_session

from ..models.Env import PostCity

from fastapi import Depends


class EnvRepository:
    def __init__(self, session: AsyncSession = Depends(get_session)):
        self.__session: AsyncSession = session

    async def get_all_city(self) -> list[City]:
        response = select(City)
        result = await self.__session.execute(response)
        return result.scalars().all()

    async def get_all_type_article(self) -> list[TypeArticle]:
        response = select(TypeArticle)
        result = await self.__session.execute(response)
        return result.scalars().all()

    async def get_all_tag(self) -> list[Tag]:
        response = select(Tag)
        result = await self.__session.execute(response)
        return result.scalars().all()

    async def add(self, target: City | Tag | TypeArticle):
        try:
            self.__session.add(target)
            await self.__session.commit()
        except:
            await self.__session.rollback()
            raise Exception

    async def get_city_by_id(self, id_city: int) -> City | None:
        target = await self.__session.get(City, id_city)
        return target

    async def get_type_article_by_id(self, id_type_article: int) -> TypeArticle | None:
        target = await self.__session.get(TypeArticle, id_type_article)
        return target

    async def get_tag_by_id(self, id_tag: int) -> Tag | None:
        target = await self.__session.get(Tag, id_tag)
        return target

    async def update(self, target: City | Tag | TypeArticle):
        try:
            self.__session.add(target)
            await self.__session.commit()
        except:
            await self.__session.rollback()
            raise Exception

    async def get_tags_by_search_field(self,
                                        name: str,
                                        count: int) -> list[Tag]:
        response = select(Tag).where(and_(
            Tag.name.ilike(f'%{name}%'),
        )).limit(count).order_by(Tag.id)
        result = await self.__session.execute(response)
        return result.scalars().all()

    async def get_tags_by_id_set(self, id_list: list[int]) -> list[Tag]:
        response = select(Tag).where(Tag.id.in_(id_list))
        result = await self.__session.execute(response)
        return result.scalars().all()
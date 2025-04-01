from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, desc
from ..tables import Article, TagArticle, Comment, Like, User
from ..database import get_session
from fastapi import Depends


class ArticleRepository:
    def __init__(self, session: AsyncSession = Depends(get_session)):
        self.__session: AsyncSession = session

    async def count_row(self, tags_list: list[int] | None, type_article: int | None) -> int:
        response = select(func.count(Article.id)).join(TagArticle)
        if tags_list is not None:
            response = response.where(TagArticle.id_tag.in_(tags_list))
        if type_article is not None:
            response = response.where(Article.id_type == type_article)
        result = await self.__session.execute(response)
        return result.scalars().first()

    async def get_limit_article(self,
                                start: int,
                                end: int,
                                tags_list: list[int] | None,
                                type_article: int | None) -> list[Article]:
        response = select(Article).join(TagArticle).order_by(desc(Article.date_publications))
        if tags_list is not None:
            response = response.where(TagArticle.id_tag.in_(tags_list))
        if type_article is not None:
            response = response.where(Article.id_type == type_article)

        response = response.offset(start).limit(end)
        result = await self.__session.execute(response)
        return result.unique().scalars().all()

    async def get_article_by_uuid(self, uuid: str) -> Article:
        response = select(Article).where(Article.uuid == uuid)
        result = await self.__session.execute(response)
        return result.unique().scalars().one()

    async def get_article_by_search(self, name: str, count: int) -> list[Article]:
        response = select(Article).where(and_(
            Article.name.ilike(f'%{name}%'),
        )).order_by(desc(Article.date_publications)).limit(count)
        result = await self.__session.execute(response)
        return result.unique().scalars().all()

    async def add(self, entity: Article):
        try:
            self.__session.add(entity)
            await self.__session.commit()
        except:
            await self.__session.rollback()
            raise Exception

    async def get_all_like_by_article(self, uuid_article: str) -> list[Like]:
        response = select(Like).join(Article).where(Article.uuid == uuid_article)
        result = await self.__session.execute(response)
        return result.scalars().all()

    async def get_all_comment_by_article(self, uuid_article: str) -> list[Comment]:
        response = select(Comment).join(Article).where(Article.uuid == uuid_article).order_by(desc(Comment.date_publications))
        result = await self.__session.execute(response)
        return result.unique().scalars().all()

    async def delete(self, target: Article):
        try:
            likes = await self.get_all_like_by_article(target.uuid)
            comments = await self.get_all_comment_by_article(target.uuid)
            for i in likes:
                await self.__session.delete(i)

            for i in comments:
                await self.__session.delete(i)

            await self.__session.delete(target)
            await self.__session.commit()
        except Exception:
            await self.__session.rollback()

    async def update(self, entity: Article):
        try:
            self.__session.add(entity)
            await self.__session.commit()
        except:
            await self.__session.rollback()
            raise Exception

    async def get_like_by_user_and_article(self, uuid_article: str, uuid_user: str) -> Like | None:
        user_liked = select(Like).join(Article).join(User, User.id == Like.id_user).where(User.uuid == uuid_user).where(
            Article.uuid == uuid_article)
        result = await self.__session.execute(user_liked)
        return result.scalars().first()

    async def get_like_info_by_uuid(self, uuid_article: str, uuid_user: str):
        likes_count = len(await self.get_all_like_by_article(uuid_article))
        info = await self.get_like_by_user_and_article(uuid_article, uuid_user) is not None

        return {"likes_count": likes_count, "user_liked": info}

    async def add_like(self, id_article: int, id_user: int):
        target = Like(
            id_article=id_article,
            id_user=id_user
        )
        try:
            self.__session.add(target)
            await self.__session.commit()
        except:
            await self.__session.rollback()
            raise Exception

    async def delete_like(self,  uuid_article: str, uuid_user: str):
        target = await self.get_like_by_user_and_article(uuid_article, uuid_user)
        try:
            await self.__session.delete(target)
            await self.__session.commit()
        except Exception:
            await self.__session.rollback()

    async def add_comment(self, entity: Comment):
        try:
            self.__session.add(entity)
            await self.__session.commit()
        except:
            await self.__session.rollback()
            raise Exception

    async def get_comment_by_uuid(self, uuid_comment: str) -> Comment:
        response = select(Comment).where(Comment.uuid == uuid_comment)
        result = await self.__session.execute(response)
        return result.unique().scalars().one()

    async def delete_comment(self, uuid_comment: str):
        try:
            target = await self.get_comment_by_uuid(uuid_comment)

            await self.__session.delete(target)
            await self.__session.commit()
        except Exception:
            await self.__session.rollback()

    async def count_row_by_user(self, uuid_user: str) -> int:
        response = select(func.count(Article.id)).join(Like).join(User, Like.id_user == User.id).where(User.uuid == uuid_user)
        result = await self.__session.execute(response)
        return result.scalars().first()

    async def get_limit_article_by_user(self, uuid_user: str, start: int, end: int) -> list[Article]:
        response = select(Article).join(Like).join(User, Like.id_user == User.id).where(User.uuid == uuid_user).order_by(desc(Article.date_publications)).offset(start).limit(end)
        result = await self.__session.execute(response)
        return result.unique().scalars().all()
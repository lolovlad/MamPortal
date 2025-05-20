from fastapi import Depends, UploadFile

from ..repositories import ArticleRepository, UserRepository, EnvRepository
from ..models.User import UserGet
from ..models.Article import *
from ..tables import Article, Comment
from datetime import datetime


class ArticleService:
    def __init__(self,
                 article_rep: ArticleRepository = Depends(),
                 user_rep: UserRepository = Depends(),
                 env_rep: EnvRepository = Depends()):
        self.__article_rep: ArticleRepository = article_rep
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

    async def get_count_page(self, tags: str | None, type_article: int | None) -> int:
        tags_list = tags
        if tags is not None:
            tags_list = list(map(int, tags.split(",")))

        count_row = await self.__article_rep.count_row(tags_list, type_article)
        sub_page = 0
        if count_row % self.__count_item > 0:
            sub_page += 1
        return count_row // self.__count_item + sub_page

    async def create_article(self, user: UserGet, target: PostArticle):
        user = await self.__user_repo.get_user_by_uuid(user.uuid)

        tags = await self.__env_repo.get_tags_by_id_set(target.tags)

        entity = Article(
            id_autor=user.id,
            date_publications=datetime.now(),
            id_type=target.id_type,
            description_lite=target.description_lite,
            name=target.name,
            description=target.description.encode("utf-8"),
        )
        entity.tags.extend(tags)
        await self.__article_rep.add(entity)
        return entity

    async def get_page_article(self,
                               num_page: int,
                               tags: str | None,
                               type_article: int | None) -> list[GetLiteArticle]:
        tags_list = tags
        if tags is not None:
            tags_list = list(map(int, tags.split(",")))

        start = (num_page - 1) * self.__count_item
        articles_entity = await self.__article_rep.get_limit_article(start, self.__count_item, tags_list, type_article)
        articles = [GetLiteArticle.model_validate(entity, from_attributes=True) for entity in articles_entity]
        return articles

    async def get_article(self, uuid: str) -> GetArticle | None:
        target = await self.__article_rep.get_article_by_uuid(uuid)
        if target is None:
            return None
        return GetArticle.model_validate(target, from_attributes=True)

    async def get_article_by_search(self, search_field: str, count: int) -> list[GetLiteArticle]:
        article_entity = await self.__article_rep.get_article_by_search(search_field, count)
        articles = [GetLiteArticle.model_validate(entity, from_attributes=True) for entity in article_entity]
        return articles

    async def delete_article(self, uuid_article: str):
        target = await self.__article_rep.get_article_by_uuid(uuid_article)
        await self.__article_rep.delete(target)

    async def update_article(self, uuid_article: str, target: UpdateArticle):
        entity = await self.__article_rep.get_article_by_uuid(uuid_article)
        entity.tags = []
        await self.__article_rep.update(entity)

        tags = await self.__env_repo.get_tags_by_id_set(target.tags)

        article_dict = target.model_dump()

        for key in article_dict:
            if key == "description":
                setattr(entity, key, article_dict[key].encode())
            elif key == "tags":
                entity.tags = tags
            else:
                setattr(entity, key, article_dict[key])

        try:
            await self.__article_rep.update(entity)
        except Exception:
            raise Exception

    async def get_commentary(self, uuid: str) -> list[GetCommentary] | None:
        target = await self.__article_rep.get_all_comment_by_article(uuid)
        if target is None:
            return None
        return [GetCommentary.model_validate(i, from_attributes=True) for i in target]

    async def get_like_info(self, uuid_article: str, uuid_user: str) -> LikeInfo | None:
        if uuid_user == "no":
            target = len(await self.__article_rep.get_all_like_by_article(uuid_article))
            t = LikeInfo(
                count=target,
                youLike=False
            )
            return t
        else:
            target = await self.__article_rep.get_like_info_by_uuid(uuid_article, uuid_user)
            if target is None:
                return None
            t = LikeInfo(
                count=target["likes_count"],
                youLike=target["user_liked"]
            )
            return t

    async def add_like(self, uuid_article: str, uuid_user: str):
        article = await self.__article_rep.get_article_by_uuid(uuid_article)
        user = await self.__user_repo.get_user_by_uuid(uuid_user)
        await self.__article_rep.add_like(article.id, user.id)

    async def delete_like(self, uuid_article: str, uuid_user: str):
        await self.__article_rep.delete_like(uuid_article, uuid_user)

    async def add_comment(self, uuid_article: str, uuid_user: str, target: PostComment):
        article = await self.__article_rep.get_article_by_uuid(uuid_article)
        user = await self.__user_repo.get_user_by_uuid(uuid_user)
        comment = Comment(
            id_user=user.id,
            id_article=article.id,
            content=target.content
        )
        await self.__article_rep.add_comment(comment)

    async def delete_comment(self, uuid_comment: str):
        await self.__article_rep.delete_comment(uuid_comment)

    async def get_count_page_by_user(self, uuid_user: str) -> int:
        count_row = await self.__article_rep.count_row_by_user(uuid_user)
        sub_page = 0
        if count_row % self.__count_item > 0:
            sub_page += 1
        return count_row // self.__count_item + sub_page

    async def get_page_event_by_user(self, uuid_user: str, num_page: int) -> list[GetLiteArticle]:
        start = (num_page - 1) * self.__count_item
        articles_entity = await self.__article_rep.get_limit_article_by_user(uuid_user, start, self.__count_item)
        articles = [GetLiteArticle.model_validate(entity, from_attributes=True) for entity in articles_entity]
        return articles
from fastapi import APIRouter, Depends, status, Response
from fastapi.responses import JSONResponse

from ..service import get_current_user, ArticleService
from ..models.Message import Message
from ..models.User import UserGet
from ..models.Article import *


router = APIRouter(prefix="/article", tags=["article"])

message_error = {
    status.HTTP_406_NOT_ACCEPTABLE: JSONResponse(content={"message": "отказ в доступе"},
                                                 status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
}


@router.post("", responses={
    status.HTTP_406_NOT_ACCEPTABLE: {"model": Message},
    status.HTTP_201_CREATED: {"model": Message},
    status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": Message}
})
async def create_article(target: PostArticle,
                         service: ArticleService = Depends(),
                         current_user: UserGet = Depends(get_current_user)):
    if current_user.type.name == "admin":
        try:
            await service.create_article(current_user, target)
            return JSONResponse(content={"message": "опубликовано"},
                                status_code=status.HTTP_201_CREATED)
        except Exception:
            return JSONResponse(content={"message": "ошибка добавления"},
                                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
    else:
        return message_error[status.HTTP_406_NOT_ACCEPTABLE]


@router.get("/get_one/{uuid}", responses={
    status.HTTP_406_NOT_ACCEPTABLE: {"model": Message},
    status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": Message}
}, response_model=GetArticle)
async def get_one_article(uuid: str,
                          service: ArticleService = Depends(),
                          ):
    article = await service.get_article(uuid)
    if article is not None:
        return article
    else:
        return JSONResponse(content={"message": "статьи не существует"},
                            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


@router.get("/page", response_model=list[GetLiteArticle],
            responses={
                status.HTTP_406_NOT_ACCEPTABLE: {"model": Message},
                status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": Message},
                status.HTTP_200_OK: {"model": Message}
            })
async def get_page_article(response: Response,
                           page: int = 1,
                           tags: str | None = None,
                           type_article: int | None = None,
                           service: ArticleService = Depends()):
    count_page = await service.get_count_page(tags, type_article)
    response.headers["X-Count-Page"] = str(count_page)
    response.headers["X-Count-Item"] = str(service.count_item)
    articles = await service.get_page_article(page, tags, type_article)
    return articles


@router.get("/search", response_model=list[GetLiteArticle],
            responses={
                status.HTTP_406_NOT_ACCEPTABLE: {"model": Message},
                status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": Message},
                status.HTTP_200_OK: {"model": Message}
            })
async def get_article_by_search(search_field: str,
                                count: int = 5,
                                service: ArticleService = Depends(),
                                ):
    articles = await service.get_article_by_search(search_field, count)
    return articles


@router.delete("/{uuid}", responses={
            status.HTTP_406_NOT_ACCEPTABLE: {"model": Message},
            status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": Message},
            status.HTTP_200_OK: {"model": Message}
})
async def delete_article(uuid: str,
                         service: ArticleService = Depends(),
                         current_user: UserGet = Depends(get_current_user)):
    if current_user.type.name == "admin":
        try:
            await service.delete_article(uuid)
            return JSONResponse(status_code=status.HTTP_200_OK,
                                content={"message": "Удалено"})
        except Exception:
            return JSONResponse(content={"message": "ошибка обновления"},
                                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
    else:
        return message_error[status.HTTP_406_NOT_ACCEPTABLE]


@router.put("/{uuid}", responses={
            status.HTTP_406_NOT_ACCEPTABLE: {"model": Message},
            status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": Message},
            status.HTTP_205_RESET_CONTENT: {}
})
async def update_article(uuid: str,
                         article_update: UpdateArticle,
                         service: ArticleService = Depends(),
                         current_user: UserGet = Depends(get_current_user)):
    if current_user.type.name == "admin":
        try:
            await service.update_article(uuid, article_update)
            return JSONResponse(status_code=status.HTTP_205_RESET_CONTENT, content=None)
        except Exception:
            return JSONResponse(content={"message": "ошибка обновления"},
                                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
    else:
        return message_error[status.HTTP_406_NOT_ACCEPTABLE]


@router.get("/commentary/{uuid}", responses={
    status.HTTP_406_NOT_ACCEPTABLE: {"model": Message},
    status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": Message}
}, response_model=list[GetCommentary])
async def get_commentary(uuid: str,
                         service: ArticleService = Depends(),
                         ):
    comment = await service.get_commentary(uuid)
    if comment is not None:
        return comment
    else:
        return JSONResponse(content={"message": "комментариев не существует"},
                            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


@router.get("/like/{uuid_article}", responses={
    status.HTTP_406_NOT_ACCEPTABLE: {"model": Message},
    status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": Message}
}, response_model=LikeInfo)
async def get_like_info(uuid_article: str,
                        uuid_user: str | None = None,
                        service: ArticleService = Depends(),
                        ):
    like = await service.get_like_info(uuid_article, uuid_user)
    if like is not None:
        return like
    else:
        return JSONResponse(content={"message": "статьи не существует"},
                            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


@router.post("/like/{uuid_article}", responses={
    status.HTTP_406_NOT_ACCEPTABLE: {"model": Message},
    status.HTTP_201_CREATED: {"model": Message},
    status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": Message}
})
async def add_like(uuid_article: str,
                   service: ArticleService = Depends(),
                   current_user: UserGet = Depends(get_current_user)
                   ):
    try:
        await service.add_like(uuid_article, current_user.uuid)
        return JSONResponse(content={"message": "добавлено"},
                            status_code=status.HTTP_201_CREATED)
    except Exception:
        return JSONResponse(content={"message": "ошибка добавления"},
                            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


@router.delete("/like/{uuid_article}", responses={
            status.HTTP_406_NOT_ACCEPTABLE: {"model": Message},
            status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": Message},
            status.HTTP_200_OK: {"model": Message}
})
async def delete_like(uuid_article: str,
                      service: ArticleService = Depends(),
                      current_user: UserGet = Depends(get_current_user)):

    try:
        await service.delete_like(uuid_article, current_user.uuid)
        return JSONResponse(status_code=status.HTTP_200_OK,
                            content={"message": "Удалено"})
    except Exception:
        return JSONResponse(content={"message": "ошибка обновления"},
                            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


@router.post("/commentary/{uuid_article}", responses={
    status.HTTP_406_NOT_ACCEPTABLE: {"model": Message},
    status.HTTP_201_CREATED: {"model": Message},
    status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": Message}
})
async def add_comment(uuid_article: str,
                      target: PostComment,
                      service: ArticleService = Depends(),
                      current_user: UserGet = Depends(get_current_user)
                      ):
    try:
        await service.add_comment(uuid_article, current_user.uuid, target)
        return JSONResponse(content={"message": "добавлено"},
                            status_code=status.HTTP_201_CREATED)
    except Exception:
        return JSONResponse(content={"message": "ошибка добавления"},
                            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


@router.delete("/commentary/{uuid_comment}", responses={
            status.HTTP_406_NOT_ACCEPTABLE: {"model": Message},
            status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": Message},
            status.HTTP_200_OK: {"model": Message}
})
async def delete_comment(uuid_comment: str,
                         service: ArticleService = Depends(),
                         current_user: UserGet = Depends(get_current_user)):
    if current_user.type.name == "admin":
        try:
            await service.delete_comment(uuid_comment)
            return JSONResponse(status_code=status.HTTP_200_OK,
                                content={"message": "Удалено"})
        except Exception:
            return JSONResponse(content={"message": "ошибка обновления"},
                                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
    else:
        return message_error[status.HTTP_406_NOT_ACCEPTABLE]


@router.get("/page/by_user", response_model=list[GetLiteArticle],
            responses={
                status.HTTP_406_NOT_ACCEPTABLE: {"model": Message},
                status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": Message},
                status.HTTP_200_OK: {"model": Message}
            })
async def get_page_article_by_user(response: Response,
                                   page: int = 1,
                                   service: ArticleService = Depends(),
                                   current_user: UserGet = Depends(get_current_user)):
    count_page = await service.get_count_page_by_user(current_user.uuid)
    response.headers["X-Count-Page"] = str(count_page)
    response.headers["X-Count-Item"] = str(service.count_item)
    articles = await service.get_page_event_by_user(current_user.uuid, page)
    return articles
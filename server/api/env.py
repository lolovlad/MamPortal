from fastapi import APIRouter, Depends, status, Request, Response
from fastapi.responses import JSONResponse, RedirectResponse

from starlette.templating import Jinja2Templates

from ..service import EnvService, get_current_user
from ..models.Message import Message
from ..models.User import UserGet
from ..models.Env import *


router = APIRouter(prefix="/env", tags=["env"])

message_error = {
    status.HTTP_406_NOT_ACCEPTABLE: JSONResponse(content={"message": "отказ в доступе"},
                                                 status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
}


@router.get("/city", responses={
    status.HTTP_406_NOT_ACCEPTABLE: {"model": Message},
    status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": Message}
}, response_model=list[GetCity])
async def get_city(service: EnvService = Depends()):
    city = await service.get_all_city()
    return city


@router.post("/city", responses={
    status.HTTP_406_NOT_ACCEPTABLE: {"model": Message},
    status.HTTP_201_CREATED: {"model": Message},
    status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": Message}
})
async def add_city(target: PostCity,
                   service: EnvService = Depends(),
                   current_user: UserGet = Depends(get_current_user)):
    if current_user.type.name == "admin":
        try:
            await service.create_city(target)
            return JSONResponse(content={"message": "добавлено"},
                                status_code=status.HTTP_201_CREATED)
        except Exception:
            return JSONResponse(content={"message": "ошибка добавления"},
                                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
    else:
        return message_error[status.HTTP_406_NOT_ACCEPTABLE]


@router.put("/city/{id_city}", responses={
    status.HTTP_406_NOT_ACCEPTABLE: {"model": Message},
    status.HTTP_200_OK: {"model": Message},
    status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": Message}
})
async def update_city(id_city: int,
                      target: PutCity,
                      service: EnvService = Depends(),
                      current_user: UserGet = Depends(get_current_user)):
    if current_user.type.name == "admin":
        try:
            await service.update_city(id_city, target)
            return JSONResponse(content={"message": "Обновленно"},
                                status_code=status.HTTP_200_OK)
        except Exception:
            return JSONResponse(content={"message": "ошибка добавления"},
                                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
    else:
        return message_error[status.HTTP_406_NOT_ACCEPTABLE]


@router.get("/city/one/{id_city}", responses={
    status.HTTP_406_NOT_ACCEPTABLE: {"model": Message},
    status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": Message}
}, response_model=GetCity)
async def get_one_city(id_city: int,
                       service: EnvService = Depends(),
                       current_user: UserGet = Depends(get_current_user)
                       ):
    city = await service.get_one_city(id_city)
    if city is not None:
        return city
    else:
        return JSONResponse(content={"message": "Пользователя не существует"},
                            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


@router.get("/type_article", responses={
    status.HTTP_406_NOT_ACCEPTABLE: {"model": Message},
    status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": Message}
}, response_model=list[GetTypeArticle])
async def get_type_article(service: EnvService = Depends()):
    city = await service.get_all_type_article()
    return city


@router.post("/type_article", responses={
    status.HTTP_406_NOT_ACCEPTABLE: {"model": Message},
    status.HTTP_201_CREATED: {"model": Message},
    status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": Message}
})
async def add_type_article(target: PostTypeArticle,
                           service: EnvService = Depends(),
                           current_user: UserGet = Depends(get_current_user)):
    if current_user.type.name == "admin":
        try:
            await service.create_type_article(target)
            return JSONResponse(content={"message": "добавлено"},
                                status_code=status.HTTP_201_CREATED)
        except Exception:
            return JSONResponse(content={"message": "ошибка добавления"},
                                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
    else:
        return message_error[status.HTTP_406_NOT_ACCEPTABLE]


@router.put("/type_article/{id_type_article}", responses={
    status.HTTP_406_NOT_ACCEPTABLE: {"model": Message},
    status.HTTP_200_OK: {"model": Message},
    status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": Message}
})
async def update_type_article(id_type_article: int,
                              target: PutTypeArticle,
                              service: EnvService = Depends(),
                              current_user: UserGet = Depends(get_current_user)):
    if current_user.type.name == "admin":
        try:
            await service.update_type_article(id_type_article, target)
            return JSONResponse(content={"message": "Обновленно"},
                                status_code=status.HTTP_200_OK)
        except Exception:
            return JSONResponse(content={"message": "ошибка добавления"},
                                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
    else:
        return message_error[status.HTTP_406_NOT_ACCEPTABLE]


@router.get("/type_article/one/{id_type_article}", responses={
    status.HTTP_406_NOT_ACCEPTABLE: {"model": Message},
    status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": Message}
}, response_model=GetTypeArticle)
async def get_one_type_article(id_type_article: int,
                               service: EnvService = Depends(),
                               current_user: UserGet = Depends(get_current_user)
                            ):
    type_article = await service.get_one_type_article(id_type_article)
    if type_article is not None:
        return type_article
    else:
        return JSONResponse(content={"message": "Пользователя не существует"},
                            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


@router.get("/tag", responses={
    status.HTTP_406_NOT_ACCEPTABLE: {"model": Message},
    status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": Message}
}, response_model=list[GetTag])
async def get_tag(service: EnvService = Depends()):
    tag = await service.get_all_tag()
    return tag


@router.post("/tag", responses={
    status.HTTP_406_NOT_ACCEPTABLE: {"model": Message},
    status.HTTP_201_CREATED: {"model": Message},
    status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": Message}
})
async def add_tag(target: PostTag,
                  service: EnvService = Depends(),
                  current_user: UserGet = Depends(get_current_user)):
    if current_user.type.name == "admin":
        try:
            await service.create_tag(target)
            return JSONResponse(content={"message": "добавлено"},
                                status_code=status.HTTP_201_CREATED)
        except Exception:
            return JSONResponse(content={"message": "ошибка добавления"},
                                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
    else:
        return message_error[status.HTTP_406_NOT_ACCEPTABLE]


@router.put("/tag/{id_tag}", responses={
    status.HTTP_406_NOT_ACCEPTABLE: {"model": Message},
    status.HTTP_200_OK: {"model": Message},
    status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": Message}
})
async def update_tag(id_tag: int,
                     target: PutTag,
                     service: EnvService = Depends(),
                     current_user: UserGet = Depends(get_current_user)):
    if current_user.type.name == "admin":
        try:
            await service.update_tag(id_tag, target)
            return JSONResponse(content={"message": "Обновленно"},
                                status_code=status.HTTP_200_OK)
        except Exception:
            return JSONResponse(content={"message": "ошибка добавления"},
                                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
    else:
        return message_error[status.HTTP_406_NOT_ACCEPTABLE]


@router.get("/tag/one/{id_tag}", responses={
    status.HTTP_406_NOT_ACCEPTABLE: {"model": Message},
    status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": Message}
}, response_model=GetTag)
async def get_one_city(id_tag: int,
                       service: EnvService = Depends(),
                       ):
    tag = await service.get_one_tag(id_tag)
    if tag is not None:
        return tag
    else:
        return JSONResponse(content={"message": "Пользователя не существует"},
                            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


@router.get("/tag/search", response_model=list[GetTag],
            responses={
                status.HTTP_406_NOT_ACCEPTABLE: {"model": Message},
                status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": Message},
                status.HTTP_200_OK: {"model": Message}
            })
async def get_tags_by_search(search_field: str,
                             count: int = 5,
                             service: EnvService = Depends()):

    tags = await service.get_tags_by_search(search_field, count)
    return tags
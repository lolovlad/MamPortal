from fastapi import APIRouter, Depends, status, Response
from fastapi.responses import JSONResponse

from ..service import get_current_user, EventService
from ..models.Message import Message
from ..models.User import UserGet
from ..models.Event import *


router = APIRouter(prefix="/event", tags=["event"])

message_error = {
    status.HTTP_406_NOT_ACCEPTABLE: JSONResponse(content={"message": "отказ в доступе"},
                                                 status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
}


@router.get("/state_event", responses={
    status.HTTP_406_NOT_ACCEPTABLE: {"model": Message},
    status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": Message}
}, response_model=list[GetState])
async def get_state_event(service: EventService = Depends(),
                          current_user: UserGet = Depends(get_current_user)):
    state_event = await service.get_state_event()
    return state_event


@router.post("", responses={
    status.HTTP_406_NOT_ACCEPTABLE: {"model": Message},
    status.HTTP_201_CREATED: {"model": Message},
    status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": Message}
})
async def create_event(target: PostEvent,
                       service: EventService = Depends(),
                       current_user: UserGet = Depends(get_current_user)):
    if current_user.type.name == "admin":
        try:
            await service.create_event(target)
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
}, response_model=GetEvent)
async def get_one_event(uuid: str,
                        service: EventService = Depends(),
                        ):
    event = await service.get_event(uuid)
    if event is not None:
        return event
    else:
        return JSONResponse(content={"message": "статьи не существует"},
                            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


@router.get("/page", response_model=list[GetLiteEvent],
            responses={
                status.HTTP_406_NOT_ACCEPTABLE: {"model": Message},
                status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": Message},
                status.HTTP_200_OK: {"model": Message}
            })
async def get_page_event(response: Response,
                         page: int = 1,
                         tags: str | None = None,
                         city: int | None = None,
                         service: EventService = Depends()):
    count_page = await service.get_count_page(tags, city)
    response.headers["X-Count-Page"] = str(count_page)
    response.headers["X-Count-Item"] = str(service.count_item)
    events = await service.get_page_event(page, tags, city)
    return events


@router.get("/search", response_model=list[GetLiteEvent],
            responses={
                status.HTTP_406_NOT_ACCEPTABLE: {"model": Message},
                status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": Message},
                status.HTTP_200_OK: {"model": Message}
            })
async def get_event_by_search(search_field: str,
                              count: int = 5,
                              service: EventService = Depends(),
                              ):
    events = await service.get_event_by_search(search_field, count)
    return events


@router.delete("/{uuid}", responses={
            status.HTTP_406_NOT_ACCEPTABLE: {"model": Message},
            status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": Message},
            status.HTTP_200_OK: {"model": Message}
})
async def delete_event(uuid: str,
                       service: EventService = Depends(),
                       current_user: UserGet = Depends(get_current_user)):
    if current_user.type.name == "admin":
        try:
            await service.delete_event(uuid)
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
async def update_event(uuid: str,
                       event_update: UpdateEvent,
                       service: EventService = Depends(),
                       current_user: UserGet = Depends(get_current_user)):
    if current_user.type.name == "admin":
        try:
            await service.update_event(uuid, event_update)
            return JSONResponse(status_code=status.HTTP_205_RESET_CONTENT, content=None)
        except Exception:
            return JSONResponse(content={"message": "ошибка обновления"},
                                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
    else:
        return message_error[status.HTTP_406_NOT_ACCEPTABLE]


@router.get("/user_registration/{uuid_event}", responses={
    status.HTTP_406_NOT_ACCEPTABLE: {"model": Message},
    status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": Message}
}, response_model=UserRegInfo)
async def get_user_registration_info(uuid_event: str,
                                     uuid_user: str | None = None,
                                     service: EventService = Depends(),
                                     ):
    reg_info = await service.get_user_registration_info(uuid_event, uuid_user)
    if reg_info is not None:
        return reg_info
    else:
        return JSONResponse(content={"message": "События не существует"},
                            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


@router.post("/user_registration/{uuid_event}", responses={
    status.HTTP_406_NOT_ACCEPTABLE: {"model": Message},
    status.HTTP_201_CREATED: {"model": Message},
    status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": Message}
})
async def add_user_reg(uuid_event: str,
                       service: EventService = Depends(),
                       current_user: UserGet = Depends(get_current_user)
                       ):
    try:
        await service.add_user_reg(uuid_event, current_user.uuid)
        return JSONResponse(content={"message": "добавлено"},
                            status_code=status.HTTP_201_CREATED)
    except Exception:
        return JSONResponse(content={"message": "ошибка добавления"},
                            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


@router.delete("/user_registration/{uuid_event}", responses={
            status.HTTP_406_NOT_ACCEPTABLE: {"model": Message},
            status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": Message},
            status.HTTP_200_OK: {"model": Message}
})
async def delete_user_reg(uuid_event: str,
                          service: EventService = Depends(),
                          current_user: UserGet = Depends(get_current_user)):

    try:
        await service.delete_user_reg(uuid_event, current_user.uuid)
        return JSONResponse(status_code=status.HTTP_200_OK,
                            content={"message": "Удалено"})
    except Exception:
        return JSONResponse(content={"message": "ошибка обновления"},
                            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


@router.delete("/user_registration/bny_user/{uuid_event}/{uuid_user}", responses={
            status.HTTP_406_NOT_ACCEPTABLE: {"model": Message},
            status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": Message},
}, response_model=list[UserGet])
async def delete_user_reg(uuid_event: str,
                          uuid_user: str,
                          service: EventService = Depends(),
                          current_user: UserGet = Depends(get_current_user)):
    if current_user.type.name == "admin":
        try:
            t = await service.delete_user_reg(uuid_event, uuid_user)
            return t
        except Exception:
            return JSONResponse(content={"message": "ошибка обновления"},
                                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
    else:
        return message_error[status.HTTP_406_NOT_ACCEPTABLE]


@router.get("/page/by_user", response_model=list[GetLiteEvent],
            responses={
                status.HTTP_406_NOT_ACCEPTABLE: {"model": Message},
                status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": Message},
                status.HTTP_200_OK: {"model": Message}
            })
async def get_page_event_by_user(response: Response,
                                 page: int = 1,
                                 service: EventService = Depends(),
                                 current_user: UserGet = Depends(get_current_user)):
    count_page = await service.get_count_page_by_user(current_user.uuid)
    response.headers["X-Count-Page"] = str(count_page)
    response.headers["X-Count-Item"] = str(service.count_item)
    events = await service.get_page_event_by_user(current_user.uuid, page)
    return events

from fastapi import APIRouter, Depends, status, Request, Response, UploadFile, File
from fastapi.responses import JSONResponse, RedirectResponse

from starlette.templating import Jinja2Templates

from ..service import UserService, get_current_user
from ..models.Message import Message
from ..models.User import UserGet, UserPost, GetTypeUser, UserUpdate, PasswordUpdate


router = APIRouter(prefix="/user", tags=["user"])

message_error = {
    status.HTTP_406_NOT_ACCEPTABLE: JSONResponse(content={"message": "отказ в доступе"},
                                                 status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
}


@router.get("/type_user", responses={
    status.HTTP_406_NOT_ACCEPTABLE: {"model": Message},
    status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": Message}
}, response_model=list[GetTypeUser])
async def get_type_user(user_service: UserService = Depends(),
                        current_user: UserGet = Depends(get_current_user)):
    type_users = await user_service.get_type_users()
    return type_users


@router.get("/get_one/{uuid}", responses={
    status.HTTP_406_NOT_ACCEPTABLE: {"model": Message},
    status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": Message}
}, response_model=UserGet)
async def get_one_user(uuid: str,
                       user_service: UserService = Depends(),
                       current_user: UserGet = Depends(get_current_user)
                       ):
    user = await user_service.get_user(uuid)
    if user is not None:
        return user
    else:
        return JSONResponse(content={"message": "Пользователя не существует"},
                            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


@router.post("", responses={
    status.HTTP_406_NOT_ACCEPTABLE: {"model": Message},
    status.HTTP_201_CREATED: {"model": Message},
    status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": Message}
})
async def create_user(user_target: UserPost,
                      user_service: UserService = Depends(),
                      current_user: UserGet = Depends(get_current_user)):
    if current_user.type.name == "admin":
        try:
            await user_service.create_user(user_target)
            return JSONResponse(content={"message": "добавлено"},
                                status_code=status.HTTP_201_CREATED)
        except Exception:
            return JSONResponse(content={"message": "ошибка добавления"},
                                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
    else:
        return message_error[status.HTTP_406_NOT_ACCEPTABLE]


@router.get("/page_user", response_model=list[UserGet],
            responses={
                status.HTTP_406_NOT_ACCEPTABLE: {"model": Message},
                status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": Message},
                status.HTTP_200_OK: {"model": Message}
            })
async def get_page_user(response: Response,
                        page: int = 1,
                        type_user: str | None = None,
                        current_user: UserGet = Depends(get_current_user),
                        user_service: UserService = Depends()):
    if current_user.type.name == "admin":
        count_page = await user_service.get_count_page()
        response.headers["X-Count-Page"] = str(count_page)
        response.headers["X-Count-Item"] = str(user_service.count_item)
        users = await user_service.get_page_user(page)
        return users
    else:
        return message_error[status.HTTP_406_NOT_ACCEPTABLE]


@router.get("/search", response_model=list[UserGet],
            responses={
                status.HTTP_406_NOT_ACCEPTABLE: {"model": Message},
                status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": Message},
                status.HTTP_200_OK: {"model": Message}
            })
async def get_users_by_search(search_field: str,
                              count: int = 5,
                              user_service: UserService = Depends(),
                              current_user: UserGet = Depends(get_current_user)
                              ):
    users = await user_service.get_users_by_search_field(search_field, count)
    return users


@router.put("/{uuid}", responses={
            status.HTTP_406_NOT_ACCEPTABLE: {"model": Message},
            status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": Message},
            status.HTTP_205_RESET_CONTENT: {}
})
async def update_user(uuid: str,
                      user_update: UserUpdate,
                      service: UserService = Depends(),
                      current_user: UserGet = Depends(get_current_user)):
    try:
        await service.update_user(uuid, user_update)
        return JSONResponse(status_code=status.HTTP_205_RESET_CONTENT, content=None)
    except Exception:
        return JSONResponse(content={"message": "ошибка обновления"},
                            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)



@router.delete("/{uuid}", responses={
            status.HTTP_406_NOT_ACCEPTABLE: {"model": Message},
            status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": Message},
            status.HTTP_200_OK: {"model": Message}
})
async def delete_user(uuid: str,
                      service: UserService = Depends(),
                      current_user: UserGet = Depends(get_current_user)):
    if current_user.type.name == "admin":
        try:
            await service.delete_user(uuid)
            return JSONResponse(status_code=status.HTTP_200_OK,
                                content={"message": "Удалено"})
        except Exception:
            return JSONResponse(content={"message": "ошибка обновления"},
                                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
    else:
        return message_error[status.HTTP_406_NOT_ACCEPTABLE]


@router.put("/password/update", responses={
            status.HTTP_406_NOT_ACCEPTABLE: {"model": Message},
            status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": Message},
            status.HTTP_205_RESET_CONTENT: {}
})
async def update_password_user(target: PasswordUpdate,
                               service: UserService = Depends(),
                               current_user: UserGet = Depends(get_current_user)):
    try:
        await service.update_password(current_user.uuid, target)
        return JSONResponse(status_code=status.HTTP_205_RESET_CONTENT, content=None)
    except Exception:
        return JSONResponse(content={"message": "ошибка обновления неправильный старый пароль"},
                            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


@router.post("/avatar/update")
async def update_avatar_user(file: UploadFile,
                             service: UserService = Depends(),
                             current_user: UserGet = Depends(get_current_user)):
    try:
        await service.upload_avatar(current_user.uuid, file)
        return JSONResponse(status_code=status.HTTP_205_RESET_CONTENT, content=None)
    except Exception:
        return JSONResponse(content={"message": "ошибка обновления неправильный старый пароль"},
                            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


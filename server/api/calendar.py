from fastapi import APIRouter, Depends, status, Response, UploadFile, Form, File
from fastapi.responses import JSONResponse

from typing import Annotated, Optional

from ..service import get_current_user, CalendarService
from ..models.Message import Message
from ..models.Calendar import *
from ..models.User import UserGet

from datetime import datetime


router = APIRouter(prefix="/calendar", tags=["calendar"])

message_error = {
    status.HTTP_406_NOT_ACCEPTABLE: JSONResponse(content={"message": "отказ в доступе"},
                                                 status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
}


@router.get("/calendar/user", responses={
    status.HTTP_406_NOT_ACCEPTABLE: {"model": Message},
    status.HTTP_404_NOT_FOUND: {"model": Message}
}, response_model=GetPregnancyCalendar)
async def get_one_calendar(service: CalendarService = Depends(),
                           current_user: UserGet = Depends(get_current_user)):
    calendar = await service.get_calendar_by_uuid_user(current_user.uuid)
    if calendar is not None:
        return calendar
    else:
        return JSONResponse(content={"message": "Календаря нет"},
                            status_code=status.HTTP_404_NOT_FOUND)


@router.post("", responses={
    status.HTTP_406_NOT_ACCEPTABLE: {"model": Message},
    status.HTTP_201_CREATED: {"model": Message},
    status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": Message}
})
async def create_calendar(target: PostPregnancyCalendar,
                          service: CalendarService = Depends(),
                          current_user: UserGet = Depends(get_current_user)):
    try:
        await service.create_calendar(current_user.uuid, target)
        return JSONResponse(content={"message": "опубликовано"},
                            status_code=status.HTTP_201_CREATED)
    except Exception:
        return JSONResponse(content={"message": "ошибка добавления"},
                            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


@router.post("/{uuid_calendar}", responses={
    status.HTTP_406_NOT_ACCEPTABLE: {"model": Message},
    status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": Message}
})
async def save_item_calendar(
        uuid_calendar: str,
        date: Annotated[str, Form()],
        description: Annotated[str, Form()],
        name: Annotated[str, Form()],
        img: Optional[UploadFile] = File(None),
        current_user: UserGet = Depends(get_current_user),
        service: CalendarService = Depends()):
    target = PostCalendarItem(
        name=name,
        description=description,
        date=datetime.fromisoformat(date)
    )
    await service.add_calendar_item(uuid_calendar, img, target)


@router.put("/{uuid_calendar}/{date}", responses={
    status.HTTP_406_NOT_ACCEPTABLE: {"model": Message},
    status.HTTP_200_OK: {"model": Message},
    status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": Message}
})
async def update_item_calendar(uuid_calendar: str,
                               date: str,
                               description: Annotated[str, Form(), None],
                               name: Annotated[str, Form(), None],
                               img: Optional[UploadFile] = File(None),
                               current_user: UserGet = Depends(get_current_user),
                               service: CalendarService = Depends()):
    try:
        target = UpdateCalendarItem(
            name=name,
            description=description,
            date=datetime.fromisoformat(date)
        )
        await service.update_calendar_item(uuid_calendar, img, target)
        return JSONResponse(content={"message": "Обновлен"},
                                     status_code=status.HTTP_200_OK)
    except Exception:
        return JSONResponse(content={"message": "Ошибка удаления"},
                            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


@router.delete("/{uuid_calendar}/{date}", responses={
    status.HTTP_406_NOT_ACCEPTABLE: {"model": Message},
    status.HTTP_200_OK: {"model": Message},
    status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": Message}
})
async def delete_item_calendar(uuid_calendar: str,
                               date: str,
                               current_user: UserGet = Depends(get_current_user),
                               service: CalendarService = Depends()):
    try:
        await service.delete_calendar_item(uuid_calendar, date)
        return JSONResponse(content={"message": "Обновлен"},
                                     status_code=status.HTTP_200_OK)
    except Exception:
        return JSONResponse(content={"message": "Ошибка удаления"},
                            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
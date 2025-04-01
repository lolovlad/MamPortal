from fastapi import Depends, UploadFile

from ..repositories import UserRepository, FileBucketRepository
from ..models.User import *
from ..tables import User



class UserService:
    def __init__(self, user_rep: UserRepository = Depends()):
        self.__user_repo: UserRepository = user_rep
        self.__file_repo: FileBucketRepository = FileBucketRepository("icon")
        self.__count_item: int = 20

    @property
    def count_item(self) -> int:
        return self.__count_item

    @count_item.setter
    def count_item(self, item):
        self.__count_item = item

    async def get_count_page(self) -> int:
        count_row = await self.__user_repo.count_row()
        sub_page = 0
        if count_row % self.__count_item > 0:
            sub_page += 1
        return count_row // self.__count_item + sub_page

    async def get_page_user(self, num_page: int) -> list[UserGet]:
        start = (num_page - 1) * self.__count_item
        users_entity = await self.__user_repo.get_limit_user(start, self.__count_item)
        users = [UserGet.model_validate(entity, from_attributes=True) for entity in users_entity]
        return users

    async def create_user(self, user: UserPost):
        entity = User(
            name=user.name,
            surname=user.surname,
            patronymic=user.patronymic,
            email=user.email,
            id_type=user.id_type,
            phone=user.phone
        )
        entity.password = user.password
        try:
            await self.__user_repo.add(entity)
        except Exception:
            raise Exception

    async def get_type_users(self) -> list[GetTypeUser]:
        type_users = await self.__user_repo.get_all_type_user()
        return [GetTypeUser.model_validate(obj, from_attributes=True) for obj in type_users]

    async def get_user(self, uuid: str) -> UserGet | None:
        user = await self.__user_repo.get_user_by_uuid(uuid)
        if user is None:
            return None
        return UserGet.model_validate(user, from_attributes=True)

    async def get_users_by_search_field(self, search_field: str, count: int):
        data_field = search_field.split(" ")
        surname, name, patronymic = "", "", ""
        if len(data_field) > 0:
            surname = data_field[0]
        if len(data_field) > 1:
            name = data_field[1]
        if len(data_field) > 2:
            patronymic = data_field[2]
        users_entity = await self.__user_repo.get_users_by_search_field(
            surname,
            name,
            patronymic,
            count
        )
        users = [UserGet.model_validate(entity, from_attributes=True) for entity in users_entity]
        return users

    async def update_user(self, uuid: str, user: UserUpdate):
        entity = await self.__user_repo.get_user_by_uuid(uuid)

        user_dict = user.model_dump()

        for key in user_dict:
            if key != "password":
                setattr(entity, key, user_dict[key])

        if user.password is not None:
            entity.password = user.password

        try:
            await self.__user_repo.update(entity)
        except Exception:
            raise Exception

    async def delete_user(self, uuid: str):
        await self.__user_repo.delete(uuid)

    async def update_password(self, uuid_user: str, target: PasswordUpdate):
        user = await self.__user_repo.get_user_by_uuid(uuid_user)
        if user.check_password(target.old):
            if target.new == target.confirm:
                user.password = target.new
                await self.__user_repo.update(user)
                return
        raise Exception

    async def upload_avatar(self, uuid_user: str, file: UploadFile):
        user = await self.__user_repo.get_user_by_uuid(uuid_user)

        ext = file.filename.split(".")[1]
        dir_name = f"{user.surname}_{user.name}_{user.patronymic}_{user.uuid}"

        file_key = f"{dir_name}.{ext}"

        user.icon = file_key

        content = await file.read()
        await self.__file_repo.upload_file(file_key,
                                           content,
                                           file.content_type)

        await self.__user_repo.update(user)
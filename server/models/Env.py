from pydantic import BaseModel


class BaseCity(BaseModel):
    name: str
    region: str


class GetCity(BaseCity):
    id: int


class PostCity(BaseCity):
    pass


class PutCity(BaseCity):
    pass


class BaseTypeArticle(BaseModel):
    name: str
    description: str


class GetTypeArticle(BaseTypeArticle):
    id: int


class PostTypeArticle(BaseTypeArticle):
    pass


class PutTypeArticle(BaseTypeArticle):
    pass


class BaseTag(BaseModel):
    name: str
    description: str


class GetTag(BaseTag):
    id: int


class PostTag(BaseTag):
    pass


class PutTag(BaseTag):
    pass


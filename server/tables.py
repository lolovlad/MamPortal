from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    Text,
    ForeignKey,
    Boolean,
    Float,
    Date,
    LargeBinary
)

from sqlalchemy.dialects.postgresql import JSONB, UUID
from uuid import uuid4
from datetime import datetime

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.mutable import MutableDict
from sqlalchemy.orm import relationship
from werkzeug.security import generate_password_hash, check_password_hash


base = declarative_base()


class TypeUser(base):
    __tablename__ = "type_user"
    id = Column(Integer, autoincrement=True, primary_key=True)
    name = Column(String(32), nullable=False, unique=True)
    description = Column(String(128), nullable=True)


class TypeArticle(base):
    __tablename__ = "type_article"
    id = Column(Integer, autoincrement=True, primary_key=True)
    name = Column(String(255), nullable=False, unique=True)
    description = Column(String(128), nullable=True)


class Tag(base):
    __tablename__ = "tag"
    id = Column(Integer, autoincrement=True, primary_key=True)
    name = Column(String(255), nullable=False, unique=True)
    description = Column(String(128), nullable=True)


class City(base):
    __tablename__ = "city"
    id = Column(Integer, autoincrement=True, primary_key=True)
    name = Column(String(255), nullable=False, unique=True)
    region = Column(String(255), nullable=False)


class StateEvent(base):
    __tablename__ = "state_event"
    id = Column(Integer, autoincrement=True, primary_key=True)
    name = Column(String(255), nullable=False, unique=True)
    description = Column(String(128), nullable=True)


class User(base):
    __tablename__ = "user"
    id = Column(Integer, autoincrement=True, primary_key=True)
    uuid = Column(UUID(as_uuid=True), unique=True, default=uuid4)

    name = Column(String, nullable=True)
    surname = Column(String, nullable=True)
    patronymic = Column(String, nullable=True)

    email = Column(String, nullable=True, unique=True)
    phone = Column(String, nullable=True, unique=True)

    password_hash = Column(String, nullable=True)
    id_type = Column(Integer, ForeignKey("type_user.id"))
    type = relationship("TypeUser", lazy="joined")
    icon = Column(String, nullable=True, default="account-icon-33.png")

    is_deleted = Column(Boolean, nullable=True, default=False)

    @property
    def password(self):
        return self.password_hash

    @password.setter
    def password(self, val: str):
        self.password_hash = generate_password_hash(val)

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)


class PregnancyCalendar(base):
    __tablename__ = "pregnancy_calendar"
    id = Column(Integer, autoincrement=True, primary_key=True)
    uuid = Column(UUID(as_uuid=True), unique=True, default=uuid4)
    id_user = Column(Integer, ForeignKey("user.id"))
    name = Column(String, nullable=True)
    calendar = Column(MutableDict.as_mutable(JSONB), nullable=True)
    date_start = Column(Date(), nullable=False)
    date_end = Column(Date(), nullable=True)


class Article(base):
    __tablename__ = "article"
    id = Column(Integer, autoincrement=True, primary_key=True)
    uuid = Column(UUID(as_uuid=True), unique=True, default=uuid4)
    id_autor = Column(Integer, ForeignKey("user.id"))
    autor = relationship("User", lazy="joined")

    date_publications = Column(DateTime(), nullable=False)

    id_type = Column(Integer, ForeignKey("type_article.id"))
    type = relationship("TypeArticle", lazy="joined")

    name = Column(String(255), nullable=False)
    description = Column(LargeBinary, nullable=True, default=b'')
    tags = relationship(Tag, secondary="tag_article", lazy="joined")


class Comment(base):
    __tablename__ = "comment"
    id = Column(Integer, autoincrement=True, primary_key=True)
    uuid = Column(UUID(as_uuid=True), unique=True, default=uuid4)
    id_user = Column(Integer, ForeignKey("user.id"))
    user = relationship("User", lazy="joined")

    id_article = Column(Integer, ForeignKey("article.id"))
    article = relationship("Article", lazy="joined")
    date_publications = Column(DateTime(), nullable=True, default=datetime.now)
    content = Column(String, nullable=False)


class Like(base):
    __tablename__ = "like"
    id_user = Column(Integer, ForeignKey("user.id"), primary_key=True)
    id_article = Column(Integer, ForeignKey("article.id"), primary_key=True)


class TagArticle(base):
    __tablename__ = "tag_article"
    id_tag = Column(Integer, ForeignKey("tag.id"), primary_key=True)
    id_article = Column(Integer, ForeignKey("article.id"), primary_key=True)


class Event(base):
    __tablename__ = "event"
    id = Column(Integer, autoincrement=True, primary_key=True)
    uuid = Column(UUID(as_uuid=True), unique=True, default=uuid4)
    date_conducting = Column(DateTime(timezone=True), nullable=False)
    date_stop = Column(DateTime(timezone=True), nullable=False)
    id_city = Column(Integer, ForeignKey("city.id"))
    city = relationship("City", lazy="joined")

    address = Column(String(255), nullable=False)
    name = Column(String(255), nullable=False)
    description = Column(LargeBinary, nullable=True, default=b'')

    id_state = Column(Integer, ForeignKey("state_event.id"))
    state = relationship("StateEvent", lazy="joined")

    tags = relationship(Tag, secondary="tag_event", lazy="joined")
    users = relationship(User, secondary="user_to_event", lazy="joined")


class UserToEvent(base):
    __tablename__ = "user_to_event"
    id_user = Column(ForeignKey("user.id"), primary_key=True)
    id_event = Column(ForeignKey("event.id"), primary_key=True)


class TagEvent(base):
    __tablename__ = "tag_event"
    id_tag = Column(Integer, ForeignKey("tag.id"), primary_key=True)
    id_event = Column(Integer, ForeignKey("event.id"), primary_key=True)

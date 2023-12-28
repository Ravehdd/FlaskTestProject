# from flsite import session, db
# from flsite import Base

import bcrypt
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from flask_jwt_extended import create_access_token
from datetime import timedelta
from passlib.hash import bcrypt


Base = declarative_base()


class Name(Base):
    __tablename__ = "names"
    id = Column(Integer, primary_key=True)
    name = Column(String)
    age = Column(Integer)
    user_id = Column(Integer, ForeignKey("user.id"))


class Video(Base):
    __tablename__ = "video"
    id = Column(Integer, primary_key=True)
    name = Column(String)
    description = Column(String)
    user_id = Column(Integer, ForeignKey("user.id"))


class User(Base):
    __tablename__ = "user"
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    email = Column(String, nullable=False, unique=True)
    password = Column(String, nullable=False)
    names = relationship("Video", backref="user", lazy=True)

    def __init__(self, **kwargs):
        self.name = kwargs.get("name")
        self.email = kwargs.get('email')
        self.password = bcrypt.hash(kwargs.get("password"))

    def get_token(self, expire_time=24):
        expire_delta = timedelta(expire_time)
        token = create_access_token(
            identity=self.id,
            expires_delta=expire_delta)
        return token

    @classmethod
    def authenticate(cls, email, password):
        user = cls.query.filter(cls.email == email).one()
        if not bcrypt.verify(password, user.password):
            raise Exception("No user with this password")
        return user











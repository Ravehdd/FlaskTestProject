# from flsite import session, db
# from flsite import Base

import bcrypt
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, ForeignKey, create_engine
from sqlalchemy.orm import relationship, scoped_session, sessionmaker
from flask_jwt_extended import create_access_token
from datetime import timedelta
from passlib.hash import bcrypt
# from flsite import session

Base = declarative_base()
engine = create_engine("sqlite:///db.sqlite")
session = scoped_session(sessionmaker(autoflush=False, autocommit=False, bind=engine))


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

    @classmethod
    def get_user_list(cls, user_id):
        try:
            videos = cls.query.filter(cls.user_id == user_id).all()
            session.commit()
        except Exception:
            session.rollback()
            raise
        return videos

    @classmethod
    def get(cls, video_id, user_id):
        try:
            video = cls.query.filter(Video.id == video_id, Video.user_id == user_id).first()
            if not video:
                raise Exception("No video")
        except Exception:
            session.rollback()
            raise
        return video

    def update(self, **kwargs):
        try:
            for key, value in kwargs.items():
                setattr(self, key, value)
                session.commit()
        except Exception:
            session.rollback()
            raise

    def delete(self):
        try:
            session.delete(self)
            session.commit()
        except Exception:
            session.rollback()
            raise


    def save(self):
        try:
            session.add(self)
            session.commit()
        except Exception:
            session.rollback()
            raise



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











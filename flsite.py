from flask import Flask, jsonify, request
from flask_restful import Api, Resource
import sqlalchemy as db
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy import create_engine, MetaData
from sqlalchemy.ext.declarative import declarative_base
from flask_jwt_extended import JWTManager, jwt_required, get_jwt_identity
from config import Config
from apispec.ext.marshmallow import MarshmallowPlugin
from apispec import APISpec
from flask_apispec.extension import FlaskApiSpec
from schemas import *
from flask_apispec import use_kwargs, marshal_with


app = Flask(__name__)
api = Api()
engine = create_engine("sqlite:///db.sqlite")
session = scoped_session(sessionmaker(autoflush=False, autocommit=False, bind=engine))
client = app.test_client()


jwt = JWTManager(app)
app.config.from_object(Config)

from models import Base, User, Video
Base.query = session.query_property()

Base.metadata.create_all(bind=engine)

docs = FlaskApiSpec()
docs.init_app(app)
app.config.update({
    "APISPEC_SPEC": APISpec(
        title="Spec",
        version="v1",
        openapi_version="2.0",
        plugins=[MarshmallowPlugin()]
    ),
    "APISPEC_SWAGGER_URL": "/swagger"
})


@app.route("/register", methods=["POST"])
@use_kwargs(UserSchema)
@marshal_with(AuthSchema)
def register(**kwargs):
    user = User(**kwargs)
    session.add(user)
    session.commit()
    token = user.get_token()
    return {"access_token": token}


@app.route("/login", methods=["POST"])
@use_kwargs(UserSchema(only=("email", "password")))
@marshal_with(AuthSchema)
def login(**kwargs):
    user = User(**kwargs)
    token = user.get_token()
    return {"access_token": token}


@app.route("/", methods=["GET"])
@jwt_required()
@marshal_with(VideoSchema(many=True))
def get_index():
    user_id = get_jwt_identity()
    videos = Video.query.filter(Video.user_id == user_id).all()
    return videos


@app.route("/post", methods=["POST"])
@jwt_required()
@use_kwargs(VideoSchema)
@marshal_with(VideoSchema)
def post_index(**kwargs):
    user_id = get_jwt_identity()
    new_one = Video(user_id=user_id, **kwargs)
    session.add(new_one)
    session.commit()
    return new_one


@app.route("/put/<int:video_id>", methods=["PUT"])
@jwt_required()
@use_kwargs(VideoSchema)
@marshal_with(VideoSchema)
def put_index(video_id, **kwargs):
    user_id = get_jwt_identity()
    item = Video.query.filter(Video.id == video_id, Video.user_id == user_id).first()
    if not item:
        return {"response": "No videos with this id"}
    for key, value in kwargs.items():
        setattr(item, key, value)
    session.commit()

    return item


@app.route("/delete/<int:video_id>", methods=["DELETE"])
@jwt_required()
@marshal_with(VideoSchema)
def delete_index(video_id):
    user_id = get_jwt_identity()
    item = Video.query.filter(Video.id == video_id, Video.user_id == user_id).first()
    if not item:
        return {"response": "No videos with this id"}
    session.delete(item)
    session.commit()
    return {"response": "Deleted successfully"}


docs.register(get_index)
docs.register(post_index)

if __name__ == "__main__":
    app.run(debug=True, port=8000)


@app.teardown_appcontext
def shutdown_session(exception=None):
    session.remove()

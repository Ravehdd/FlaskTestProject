from flask import Flask, jsonify, request
from flask_restful import Api, Resource
import sqlalchemy as db
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy import create_engine, MetaData
from sqlalchemy.ext.declarative import declarative_base
from flask_jwt_extended import JWTManager, jwt_required, get_jwt_identity
from .config import Config
from apispec.ext.marshmallow import MarshmallowPlugin
from apispec import APISpec
from flask_apispec.extension import FlaskApiSpec
from .schemas import *
from flask_apispec import use_kwargs, marshal_with
import logging

app = Flask(__name__)
api = Api()
engine = create_engine("sqlite:///db.sqlite")
session = scoped_session(sessionmaker(autoflush=False, autocommit=False, bind=engine))
client = app.test_client()


jwt = JWTManager()
app.config.from_object(Config)
from .models import *
Base.query = session.query_property()

docs = FlaskApiSpec()
app.config.update({
    "APISPEC_SPEC": APISpec(
        title="Spec",
        version="v1",
        openapi_version="2.0",
        plugins=[MarshmallowPlugin()]
    ),
    "APISPEC_SWAGGER_URL": "/swagger"
})


Base.metadata.create_all(bind=engine)


def setup_logger():
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)

    formatter = logging.Formatter("%(asctime)s:%(name)s:%(levelname)s:%(message)s")
    file_handler = logging.FileHandler("log/api.log")
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    return logger


logger = setup_logger()



# @app.route("/register", methods=["POST"])
# @use_kwargs(UserSchema)
# @marshal_with(AuthSchema)
# def register(**kwargs):
#     user = User(**kwargs)
#     session.add(user)
#     session.commit()
#     token = user.get_token()
#     return {"access_token": token}
#
#
# @app.route("/login", methods=["POST"])
# @use_kwargs(UserSchema(only=("email", "password")))
# # @marshal_with(AuthSchema)
# def login(**kwargs):
#     params = request.json
#     user = User(**params)
#     token = user.get_token()
#     return {"access_token": token}


# @app.route('/register', methods=['POST'])
# def register():
#     try:
#         params = request.json
#         user = User(**params)
#         session.add(user)
#         session.commit()
#         token = user.get_token()
#     except Exception as e:
#         logger.warning(f"Registration failed with errors: {e}")
#         return {"message": str(e)}, 400
#     return {'access_token': token}
#
#
# @app.route('/login', methods=['POST'])
# def login():
#     try:
#         params = request.json
#         user = User.authenticate(**params)
#         token = user.get_token()
#     except Exception as e:
#         logger.warning(f"Login with email {params['email']} failed with errors: {e}")
#         return {"message": str(e)}, 400
#     return {'access_token': token}
#
#
# @app.route("/", methods=["GET"])
# @jwt_required()
# @marshal_with(VideoSchema(many=True))
# def get_index():
#     try:
#         user_id = get_jwt_identity()
#         videos = Video.get_user_list(user_id=user_id)
#     except Exception as e:
#         logger.warning(f"user:{user_id} read action failed with errors: {e}")
#         return {"message": str(e)}, 400
#     return videos
#
#
# @app.route("/post", methods=["POST"])
# @jwt_required()
# @use_kwargs(VideoSchema)
# @marshal_with(VideoSchema)
# def post_index(**kwargs):
#     params = request.json
#     try:
#         user_id = get_jwt_identity()
#         new_one = Video(user_id=user_id, **kwargs)
#         new_one.save()
#     except Exception as e:
#         logger.warning(f"user:{user_id} create action failed with errors: {e}")
#         return {"message": str(e)}, 400
#     return new_one
#
#
# @app.route("/put/<int:video_id>", methods=["PUT"])
# @jwt_required()
# @use_kwargs(VideoSchema)
# @marshal_with(VideoSchema)
# def put_index(video_id, **kwargs):
#     try:
#         user_id = get_jwt_identity()
#         item = Video.get(video_id=video_id, user_id=user_id)
#         item.update(**kwargs)
#     except Exception as e:
#         logger.warning(f"user:{user_id} update action failed with errors: {e}")
#         return {"message": str(e)}, 400
#     return item
#
#
# @app.route("/delete/<int:video_id>", methods=["DELETE"])
# @jwt_required()
# @marshal_with(VideoSchema)
# def delete_index(video_id):
#     try:
#         user_id = get_jwt_identity()
#         item = Video.get(video_id=video_id, user_id=user_id)
#         item.delete()
#     except Exception as e:
#         logger.warning(f"user:{user_id} delete action failed with errors: {e}")
#         return {"message": str(e)}, 400
#     return {"response": "Deleted successfully"}

@app.teardown_appcontext
def shutdown_session(exception=None):
    session.remove()


from .main.views import videos
from .users.views import users

app.register_blueprint(videos)
app.register_blueprint(users)

docs.init_app(app)
jwt.init_app(app)

# @app.errorhandler(422)
# def error_handler(err):
#     headers = err.data.get("headers", None)
#     messages = err.data.get("messages", ["Invalid request"])
#     logger.warning(f"Invalid input params: {messages}")
#
#     if headers:
#         return jsonify({"messages": messages}), 400, headers
#     else:
#         return jsonify({"messages": messages}), 400


# docs.register(get_index)
# docs.register(post_index)
#


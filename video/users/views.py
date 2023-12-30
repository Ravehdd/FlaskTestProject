from flask import Blueprint, jsonify
from video import logger, session, request, docs
from video.schemas import *
from flask_apispec import use_kwargs, marshal_with
from video.models import User

users = Blueprint("users", __name__)


@users.route('/register', methods=['POST'])
def register():
    try:
        params = request.json
        user = User(**params)
        session.add(user)
        session.commit()
        token = user.get_token()
    except Exception as e:
        logger.warning(f"Registration failed with errors: {e}")
        return {"message": str(e)}, 400
    return {'access_token': token}


@users.route('/login', methods=['POST'])
def login():
    try:
        params = request.json
        user = User.authenticate(**params)
        token = user.get_token()
    except Exception as e:
        logger.warning(f"Login with email {params['email']} failed with errors: {e}")
        return {"message": str(e)}, 400
    return {'access_token': token}


@users.errorhandler(422)
def error_handler(err):
    headers = err.data.get("headers", None)
    messages = err.data.get("messages", ["Invalid request"])
    logger.warning(f"Invalid input params: {messages}")

    if headers:
        return jsonify({"messages": messages}), 400, headers
    else:
        return jsonify({"messages": messages}), 400


docs.register(login, blueprint="users")
docs.register(register, blueprint="users")

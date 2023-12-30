from flask import Blueprint, jsonify
from video import logger, request, docs
from video.schemas import *
from flask_apispec import use_kwargs, marshal_with
from video.models import Video
from flask_jwt_extended import jwt_required, get_jwt_identity

videos = Blueprint("videos", __name__)


@videos.route("/", methods=["GET"])
@jwt_required()
@marshal_with(VideoSchema(many=True))
def get_index():
    try:
        user_id = get_jwt_identity()
        videos = Video.get_user_list(user_id=user_id)
    except Exception as e:
        logger.warning(f"user:{user_id} read action failed with errors: {e}")
        return {"message": str(e)}, 400
    return videos


@videos.route("/post", methods=["POST"])
@jwt_required()
@use_kwargs(VideoSchema)
@marshal_with(VideoSchema)
def post_index(**kwargs):
    params = request.json
    try:
        user_id = get_jwt_identity()
        new_one = Video(user_id=user_id, **kwargs)
        new_one.save()
    except Exception as e:
        logger.warning(f"user:{user_id} create action failed with errors: {e}")
        return {"message": str(e)}, 400
    return new_one


@videos.route("/put/<int:video_id>", methods=["PUT"])
@jwt_required()
@use_kwargs(VideoSchema)
@marshal_with(VideoSchema)
def put_index(video_id, **kwargs):
    try:
        user_id = get_jwt_identity()
        item = Video.get(video_id=video_id, user_id=user_id)
        item.update(**kwargs)
    except Exception as e:
        logger.warning(f"user:{user_id} update action failed with errors: {e}")
        return {"message": str(e)}, 400
    return item


@videos.route("/delete/<int:video_id>", methods=["DELETE"])
@jwt_required()
@marshal_with(VideoSchema)
def delete_index(video_id):
    try:
        user_id = get_jwt_identity()
        item = Video.get(video_id=video_id, user_id=user_id)
        item.delete()
    except Exception as e:
        logger.warning(f"user:{user_id} delete action failed with errors: {e}")
        return {"message": str(e)}, 400
    return {"response": "Deleted successfully"}


@videos.errorhandler(422)
def error_handler(err):
    headers = err.data.get("headers", None)
    messages = err.data.get("messages", ["Invalid request"])
    logger.warning(f"Invalid input params: {messages}")

    if headers:
        return jsonify({"messages": messages}), 400, headers
    else:
        return jsonify({"messages": messages}), 400


docs.register(get_index, blueprint="videos")
docs.register(post_index, blueprint="videos")



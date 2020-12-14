from os import environ
from app.helpers.cloud import get_cloud


def is_admin(user_name: str) -> bool:
    cloud = get_cloud()
    return cloud.is_user_admin(user_name)

from os import environ

def get_admin_name() -> str:
    return environ.get("DEFAULT_USER")

def is_admin(user_name: str) -> bool:
    return user_name == get_admin_name()

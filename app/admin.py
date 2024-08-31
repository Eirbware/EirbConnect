from app.models import User
from fastapi import routing


def isAdmin(user: User) -> bool:
    return user.user == "eirbware"

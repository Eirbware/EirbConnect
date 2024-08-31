"""
This module contains helper functions
"""

import base64
from app.database.mongodb import mongodb
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# Helper password functions
def verify_password(plain_password, hashed_password):
    """
    Helper function to check if a password matches a hashed password
    """
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    """
    Helper function to generate a hashed password
    """
    return pwd_context.hash(password)


def get_origin(url: str) -> str:
    """
    Returns the origin of an url

    Ex: https://eirb.fr/association -> https://eirb.fr
    """
    return "/".join(url.split("/")[:3])


def is_origin_whitelisted(service_origin: str) -> bool:
    service = mongodb.services.find_one({"service_origin": service_origin})
    return service != None


def is_url_whitelisted(url: str) -> bool:
    return is_origin_whitelisted(get_origin(url))


def encode_base64(string: str) -> str:
    """
    Encode a string in base64
    """
    return base64.urlsafe_b64encode(string.encode("utf-8")).decode("utf-8")


def decode_base64(string: str) -> str:
    """
    Encode a string in base64
    """
    return base64.urlsafe_b64decode(string.encode("utf-8")).decode("utf-8")


def url_add_query(url: str, name: str, value: str) -> str:
    if "?" in url:
        return f"{url}&{name}={value}"

    else:
        return f"{url}?{name}={value}"

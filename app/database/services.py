from datetime import datetime
from random import randint
from app.database.mongodb import mongodb

MAX_REDIRECT_ID = 2**32


def add_service(origin: str) -> None:
    """ """
    if not mongodb.services.find_one({"service_origin": origin}):
        mongodb.services.insert_one(
            {
                "service_origin": origin,
            }
        )


def create_redirection(redirect_url: str) -> int:
    """
    Store a redirection url using a random id

    Returns the redirect id
    """

    def generate_redirect_id() -> int:
        return randint(0, MAX_REDIRECT_ID)

    def redirect_id_exists(redirect_id: int) -> bool:
        return mongodb.redirections.find_one({"redirect_id": redirect_id}) == None

    redirect_id = -1
    while redirect_id < 0 and redirect_id_exists(redirect_id):
        redirect_id = generate_redirect_id()

    mongodb.redirections.insert_one(
        {
            "redirect_id": redirect_id,
            "redirect_url": redirect_url,
            "created": datetime.now(),
        }
    )

    return redirect_id


def get_redirection_from_id(redirect_id: int) -> str:
    """
    Returns the redirection url if redirect_id exists
            otherwise, returns an empty string

            returns EirbConnect if redirect_id = -1

    """
    if redirect_id == -1:
        return "EirbConnect"

    res = mongodb.redirections.find_one({"redirect_id": redirect_id})

    if res == None:
        return ""

    return res["redirect_url"]

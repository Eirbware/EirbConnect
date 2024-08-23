from app.database.mongodb import mongodb
from app.models import CasUser, User
from app.utils import get_password_hash


def get_user_from_login(login: str) -> User | None:
    return mongodb.utilisateurs.find_one({"user": login})


def user_exists(login: str) -> bool:
    """
    Returns True if the user cas_login exists in the database
            False otherwise
    """
    return get_user_from_login(login) != None


def add_user(cas_user: CasUser, email_personnel: str, password: str) -> None:
    # Check
    if user_exists(cas_user.user):
        return

    # hash the password
    hashed_password = get_password_hash(password)

    mongodb.utilisateurs.insert_one(
        {
            "user": cas_user.user,
            "attributes": {
                "nom": cas_user.attributes.nom,
                "prenom": cas_user.attributes.prenom,
                "courriel": cas_user.attributes.courriel,
                "email_personnel": email_personnel,
                "profil": cas_user.attributes.profil,
                "nom_complet": cas_user.attributes.nom_complet,
                "ecole": cas_user.attributes.ecole,
                "diplome": cas_user.attributes.diplome,
                "supannEtuAnneeInscription": cas_user.attributes.supannEtuAnneeInscription,
            },
            "password": hashed_password,
            "roles": [],
        }
    )

"""
EirbConnect : Service d'authentification des étudiants de l'ENSEIRB-MATMECA
This is the main file of the application.
"""

from pathlib import Path

from app.database.mongodb import create_collections
from app.database.services import add_service
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.conf import APP_URL, BASE_DIR, config_disp, ADMIN_PASS, DEFAULT_ADMIN_PASS
from app.database.users import add_user
from app.models import CasUser, CasUserAttributes, User, UserAttributes
from app.utils import get_password_hash
from app.routers.api import api_router
from app.routers.front import front_router

print(config_disp())
create_collections(["utilisateurs", "services", "roles", "assos", "redirections"])

app = FastAPI()
app.mount(
    "/static", StaticFiles(directory=str(Path(BASE_DIR, "static"))), name="static"
)

origins = [APP_URL]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(front_router)
app.include_router(api_router)

# We insert the EirbConnect service
add_service("EirbConnect")
add_service("http://localhost:3000")

# Create an account for eirbware, used as an admin account for other services
# To prevent security issues, the admin password musn't be the default one
if ADMIN_PASS != DEFAULT_ADMIN_PASS:
    add_user(
        CasUser(
            user="Eirbware",
            attributes=CasUserAttributes(
                nom="",
                prenom="Eirbware",
                courriel="eirbware@enseirb-matmeca.fr",
                profil="asso",
                nom_complet="Eirbware",
                ecole="enseirb-matmeca",
                diplome="",
                supannEtuAnneeInscription="2024",
            ),
        ),
        "eirbware@enseirb-matmeca.fr",
        ADMIN_PASS,
    )

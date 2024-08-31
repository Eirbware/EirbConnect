from pathlib import Path

from fastapi import APIRouter, Request, HTTPException, Form
from fastapi.responses import RedirectResponse, FileResponse
from fastapi.templating import Jinja2Templates

from app.conf import APP_URL, CAS_SERVICE_URL, BASE_DIR
from app.database.services import get_redirection_from_id
from app.utils import encode_base64, get_origin, is_url_whitelisted
from app.auth import (
    get_user_from_token,
    get_user_data_from_token,
    create_access_token,
    get_user_with_id_and_password,
)


templates = Jinja2Templates(directory=str(Path(BASE_DIR, "templates")))
front_router = APIRouter()


@front_router.get("/")
async def root(request: Request):
    """
    Page de présentation
    """
    return templates.TemplateResponse(
        name="index.html",
        context={
            "request": request,
        },
    )


@front_router.get("/favicon.ico", include_in_schema=False)
async def favicon():
    """
    Endpoint pour le favicon
    """
    headers = {
        "Content-Security-Policy": f"default-src 'self' {APP_URL}",
    }
    return FileResponse(str(Path(BASE_DIR, "static", "favicon.ico")), headers=headers)


@front_router.get("/login")
async def login(request: Request, service_url: str = "EirbConnect"):
    """
    Page de login
    """
    if not is_url_whitelisted(service_url):
        return HTTPException(status_code=403, detail="Service not whitelisted")

    return templates.TemplateResponse(
        name="login.html",
        context={
            "request": request,
            "service_url": service_url,
        },
    )


# @front_router.post("/login/{redirection_id}")
# async def login_post(
#     request: Request,
#     redirection_id: str,
#     cas_id: str = Form(...),
#     password: str = Form(...),
# ):
#     """
#     Route qui s'exécute après l'envoi du formulaire de login et qui authentifie l'utilisateur
#     """
#     eirb_service_url = get_redirection_from_id(redirection_id)
#
#     user = get_user_with_id_and_password(cas_id, password)
#
#     if not user:
#         return templates.TemplateResponse(
#             name="login.html",
#             context={
#                 "request": request,
#                 "service_url": get_redirection_from_id(redirection_id),
#                 "error": "Identifiant ou mot de passe incorrect",
#             },
#         )
#
#     if eirb_service_url:
#         return RedirectResponse(
#             url=f"{eirb_service_url}?token={create_access_token(user.model_dump())}",
#             status_code=303,
#         )
#
#     return user


@front_router.get("/logout")
async def logout():
    """
    Page de logout
    """
    return RedirectResponse(url=f"{CAS_SERVICE_URL}/logout")


@front_router.get("/register")
async def register(request: Request, redirect_id: int = -1, token: str | None = None):
    """
    Page d'inscription
    """
    redirect_url = get_redirection_from_id(redirect_id)
    if not is_url_whitelisted(redirect_url):
        return HTTPException(status_code=403, detail="Service not whitelisted")

    # Si le token n'est pas présent, on redirige vers la page d'authentification
    if not token:
        return RedirectResponse(url=f"/api/cas_login?service_url={redirect_url}")

    # Si le token est présent, on vérifie qu'il est valide
    cas_user = get_user_from_token(token)

    return templates.TemplateResponse(
        name="register.html",
        context={
            "request": request,
            "cas_user": cas_user,
            "token": token,
            "redirect_id": redirect_id,
        },
    )


@front_router.get("/get_user_info")
def get_user_info(token: str):
    """
    Endpoint pour récupérer les informations d'un utilisateur à partir d'un token
    """
    return get_user_data_from_token(token)

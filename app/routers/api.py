from fastapi import APIRouter, Request, HTTPException, Form
from fastapi.responses import RedirectResponse, FileResponse

from app.conf import APP_URL, CAS_PROXY, CAS_SERVICE_URL
from app.database.services import create_redirection, get_redirection_from_id
from app.utils import (
    encode_base64,
    get_origin,
    is_origin_whitelisted,
    is_url_whitelisted,
    url_add_query,
)
from app.auth import (
    register_user,
    get_user,
    get_cas_user_from_ticket,
    get_user_from_token,
    get_user_data,
    get_user_data_from_token,
    update_user,
    create_access_token,
    get_user_with_id_and_password,
)

api_router = APIRouter(prefix="/api")


@api_router.post("/login")
async def login_post(
    request: Request,
    cas_id: str = Form(...),
    password: str = Form(...),
    service_url: str = Form(...),
):
    """
    Route qui s'exécute après l'envoi du formulaire de login et qui authentifie l'utilisateur
    """
    if not is_url_whitelisted(service_url):
        return HTTPException(status_code=403, detail="Service not whitelisted")

    user = get_user_with_id_and_password(cas_id, password)

    if not user:
        return HTTPException(
            status_code=404, detail="Identifiant ou mot de passe incorrect"
        )
        # return templates.TemplateResponse(
        #     name="login.html",
        #     context={
        #         "request": request,
        #         "service_url": service_url,
        #         "error": "Identifiant ou mot de passe incorrect",
        #     },
        # )

    if service_url:
        if service_url == "EirbConnect":
            return RedirectResponse(
                url=f"/get_user_info?token={create_access_token(user.model_dump())}",
                status_code=303,
            )

        return RedirectResponse(
            url=f"{service_url}?token={create_access_token(user.model_dump())}",
            status_code=303,
        )

    return user


@api_router.get("/cas_redirect/{redirect_id}")
async def cas_redirect(redirect_id: int, ticket: str):
    """
    Login avec le CAS puis redirection vers "eirb_service_url"
    """
    redirected_url = f"{APP_URL}/api/cas_redirect/{redirect_id}"
    service_url = redirected_url
    if CAS_PROXY != "":
        service_url = (
            f"{CAS_PROXY}/login?token={encode_base64(redirected_url)}@bordeaux-inp.fr"
        )

    # On récupère l'utilisateur CAS depuis le ticket
    cas_user = get_cas_user_from_ticket(ticket, service_url)

    if not cas_user:
        return HTTPException(status_code=403, detail="Invalid ticket")

    redirect_url = get_redirection_from_id(redirect_id)
    print(redirect_id, redirect_url)

    # On vérifie que l'utilisateur existe dans la base de données
    user = get_user(cas_user.user)

    if not user and redirect_url:
        # Si l'utilisateur n'existe pas, on redirige vers la page d'inscription
        return RedirectResponse(
            url=f"/register?token={create_access_token(cas_user.model_dump())}&redirect_id={redirect_id}"
        )

    elif not user:
        return RedirectResponse(
            url=f"/register?token={create_access_token(cas_user.model_dump())}"
        )

    # Si l'utilisateur existe, on met a jour ses attributs "cas"
    update_user(cas_user)

    user_data = get_user_data(cas_user.user)

    if not user_data:
        return RedirectResponse(
            url=f"/register?token={create_access_token(cas_user.model_dump())}&redirect_id={redirect_id}"
        )

    if redirect_url and redirect_url != "EirbConnect":
        return RedirectResponse(
            url_add_query(
                redirect_url,
                "token",
                create_access_token(user_data),
            )
        )

    return user_data


@api_router.get("/cas_login")
async def cas_login(service_url: str = "EirbConnect"):
    """
    Endpoint pour authentication uniquement avec le cas
    (redirection transparente pour l'utilisateur)

    Args:
        service_url (str, optional): _description_. Defaults to "EirbConnect".
    """
    # On encrypte l'url du service et on vérifie qu'il est autorisé à utiliser EirbConnect
    if not is_url_whitelisted(service_url):
        return HTTPException(status_code=403, detail="Service not whitelisted")

    redirect_id = create_redirection(service_url)

    redirect_url = f"{APP_URL}/api/cas_redirect/{redirect_id}"
    service_url = redirect_url
    if CAS_PROXY != "":
        service_url = f"{CAS_PROXY}/login?token={encode_base64(redirect_url)}@bordeaux-inp.fr&serviceUrl={redirect_url}"

    authentication_cas_url = f"{CAS_SERVICE_URL}/?service={service_url}"

    return RedirectResponse(url=authentication_cas_url)


@api_router.post("/register/{redirect_id}/{token}")
async def register_post(
    token: str,
    redirect_id: int,
    email: str = Form(...),
    password: str = Form(...),
):
    """
    Route qui s'exécute après l'envoi du formulaire de login et qui enregistre l'utilisateur
    """
    redirect_url = get_redirection_from_id(redirect_id)

    # On récupère les données de l'utilisateur depuis le token
    cas_user = get_user_from_token(token)

    if not cas_user:
        return HTTPException(status_code=403, detail="Invalid token")

    register_user(cas_user, email, password)

    user = get_user_data(cas_user.user)

    if not user:
        return HTTPException(status_code=404, detail="User not found")

    if redirect_url == "EirbConnect":
        return RedirectResponse(
            url=f"/get_user_info?token={create_access_token(user)}", status_code=302
        )

    elif redirect_url:
        return RedirectResponse(
            url=url_add_query(redirect_url, "token", create_access_token(user)),
        )

    return user

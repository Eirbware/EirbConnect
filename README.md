# EirbConnect

## Description

EirbConnect est un service d'authentification pensé pour connecter les étudiants de l'ENSEIRB-MATMECA aux services de l'école créés par les étudiants (dont Eirbware et le BDE).
Il permet également aux anciens élèves de l'école de continuer de se connecter aux services associatifs apprès suppression leur compte CAS.

## Table des matières

- Technologies
- Installation
- Docker
- Utilisation

## Technologies

Framework: FastAPI
Database: MongoDB

## Installation

### Prérequis

- MongoDB
  Les collections suivantes seront créées automatiquement :
  - services : liste des services qui sont autorisés à utiliser EirbConnect 
  - assos : liste des associations (pour assos.eirb.fr)
  - utilisateurs : liste des utilisateurs
  - roles : liste de leurs rôles dans les associations
- Python

### Installation

#### Créer un environnement virtuel

```bash
python3 -m venv venv
```

#### Activer l'environnement virtuel

```bash
source venv/bin/activate
```

#### Installer les dépendances

```bash
pip install -r requirements.txt
```

#### Configurer les variables d'environnement

Voici un exemple de fichier `.env` à créer dans app :

```bash
touch app/.env
```

```
MONGO_URI = localhost:27017

# auth

# à générer avec openssl rand -hex 32
SECRET_KEY = "<clé secrète pour les tokens JWT>"
ACCES_TOKEN_EXPIRE_MINUTES = 30
ALGORITHM = "HS256"

# Config pour docker

APP_URL = "http://0.0.0.0:8080"
```

#### Lancer le serveur

```bash
./run.sh
```

## Docker

### Créer l'image

```bash
docker build -t eirb_connect .
```

### Lancer le conteneur

```bash
ocker run -d -p 8000:80 -e MONGO_URI=localhost:27017 --name EirbConnect eirb_connect
```

## Utilisation

### Front

#### GET `/`

Page permettant de diriger vers `/register` ou `/login`.


#### GET `/login`

Paramètres:
  - service_url: URL de redirection après authentification d'un des services whitelisté (optionnel)

Sur cette page, l'utilisateur peut se connecter avec son identifiant CAS et un mot de passe ou alors se connecter avec le CAS (redirection vers /api/caslogin).

#### GET `/register`

Paramètres:
  - service_url: URL de redirection après authentification d'un des services whitelisté (optionnel)

Redirige l'utilisateur vers le CAS Bordeaux INP, récupère les informations de l'utilisateur puis le redirige vers une page de création de compte. Sur cette page l'utilisateur est alors invité à renseigner son mail personnel et un mot de passe.

#### GET `/get_user_info?token=<token>`

Paramètres:
  - token: token JWT de l'utilisateur

Permet de récupérer les informations de l'utilisateur après authentification.

### API

#### POST `/api/login` 

Body:
  - cas_id: identifiant de connexion CAS
  - password: mot de passe EirbConnect associé à cas_id
  - service_url: URL de redirection après authentification d'un des services whitelisté (optionnel)

Renvoie :
* `403` si `service_url` ne fait pas parti des services whitelistés 
* `404` si le couple `(cas_id, password)` ne correspond pas à un utilisateur
* `303` redirige vers `service_url` si l'authentification réussie

Si service_url n'est pas EirbConnect, un token JWT est créé et est passé en query comme paramètre `token`

#### GET `/api/cas_login` 

Paramètres:
  - service_url: URL de redirection après authentification d'un des services whitelisté (optionnel)

Permet d'idientifier un utilisateur avec le CAS Bordeaux INP de manière transparente pour un utilisateur qui a un compte EirbConnect.
Si l'utilisateur n'a pas de compte EirbConnect, il sera redirigé vers la page de création de compte.
Stocke associe `service_url` à un `redirect_id` unique.

Renvoie :
* `403` si `service_url` ne fait pas parti des services whitelistés 
* Redirige vers `CAS_PROXY` si la variable est définie dans le `.env`
* Redirige vers `CAS_SERVICE_URL` sinon

#### GET `/api/cas_redirect` 

Paramètres:
  - redirect_id (int): identifiant de redirection pour rediriger après l'authentification
  - ticket: ticket permettant de valider l'authentification

Point de redirection venant du CAS après authentification.

Renvoie :
* `403` si le ticket n'est pas valide
* Redirection vers `/register` si l'utilisateur n'a pas de compte EirbConnect
* Redirige vers l'url associée à redirect_id s'il en existe une
* Sinon, retourne les informations de l'utilisateur

#### POST `/register/{redirect_id}/{token}`

Paramètres:
  - redirect_id (int): identifiant de redirection pour rediriger après l'authentification
  - token: token d'authentification JWT
  - email: adresse mail de l'utilisateur
  - password: mot de passe de l'utilisateur

Créé un utilisateur dans la base de donnée d'EirbConnect

Renvoie :
* `403` si le token n'est pas valide
* Redirige vers l'url associée à redirect_id s'il en existe une
* Sinon, retourne les informations de l'utilisateur

#### GET `/api/logout`

Déconnecte l'utilisateur du service.

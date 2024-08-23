"""
This file contains the configuration for the application.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
dotenv_path = Path(os.path.dirname(os.path.abspath(__file__))) / ".env"
load_dotenv(dotenv_path=dotenv_path)

APP_URL = os.getenv("APP_URL", "http://127.0.0.1:8080")
CAS_SERVICE_URL = os.getenv("CAS_SERVICE_URL", "https://cas.bordeaux-inp.fr/")

DEFAULT_ADMIN_PASS = "admin"
ADMIN_PASS = os.getenv("ADMIN_PASS", DEFAULT_ADMIN_PASS)

CAS_PROXY = os.getenv("CAS_PROXY", "")


HOST = os.getenv("MONGO_URI", "localhost:27017")
BASE_DIR = Path(__file__).resolve().parent


# The secret key should be UNIQUE and SECRET
# You may use the following command to generate a secret key:
# openssl rand -hex 32
# Copy the output and paste it in the .env file as SECRET_KEY variable

SECRET_KEY = os.getenv("SECRET_KEY", "very_secret_key")
ACCES_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCES_TOKEN_EXPIRE_MINUTES", "30"))

# encryption algorithm
ALGORITHM = os.getenv("ALGORITHM", "HS256")


def config_disp():
    return f"""Config :
APP_URL={APP_URL}
CAS_SERVICE_URL={CAS_SERVICE_URL}
CAS_PROXY={CAS_PROXY}
HOST={HOST}
SECRET_KEY={SECRET_KEY}
ACCESS_TOKEN_EXPIRE_MINUTES={ACCES_TOKEN_EXPIRE_MINUTES}
ALGORITHM={ALGORITHM}
ADMIN_PASS={ADMIN_PASS}
"""

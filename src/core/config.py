import os
from dotenv import load_dotenv

# Carrega variáveis do .env
load_dotenv()

class Settings:
    # APP
    PROJECT_NAME: str = "Raízes do Nordeste api"

    # JWT
    SECRET_KEY: str = os.getenv("SECRET_KEY", "supersecret")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    # DATABASE
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./raizes.db")

settings = Settings()
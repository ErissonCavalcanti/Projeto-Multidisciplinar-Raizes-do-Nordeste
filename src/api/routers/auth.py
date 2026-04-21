from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime, timedelta

from src.infrastructure.database import get_db
from src.infrastructure.models import Usuario
from src.core.config import settings
from src.api.schemas.error_schema import make_error

from passlib.context import CryptContext
from jose import jwt

from pydantic import BaseModel, EmailStr

router = APIRouter()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class UserLogin(BaseModel):
    email: EmailStr
    senha: str


def verificar_senha(senha: str, senha_hash: str):
    return pwd_context.verify(senha, senha_hash)


def criar_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


@router.post("/login")
def login(user: UserLogin, db: Session = Depends(get_db)):
    usuario = db.query(Usuario).filter(Usuario.email == user.email).first()

    if not usuario or not verificar_senha(user.senha, usuario.senha_hash):
        raise HTTPException(
            status_code=401,
            detail=make_error("CREDENCIAIS_INVALIDAS", "E-mail ou senha inválidos.", "/auth/login")
        )

    token_data = {
        "sub": usuario.email,
        "id": usuario.id,
        "perfil": usuario.perfil
    }
    token = criar_token(token_data)

    return {
        "accessToken": token,
        "tokenType": "Bearer",
        "expiresIn": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        "user": {
            "id": usuario.id,
            "nome": usuario.nome,
            "email": usuario.email,
            "perfil": usuario.perfil
        }
    }
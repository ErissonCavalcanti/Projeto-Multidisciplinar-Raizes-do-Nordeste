from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime, timedelta

from src.infrastructure.database import get_db
from src.infrastructure.models import Usuario
from src.core.config import settings

from passlib.context import CryptContext
from jose import jwt

from pydantic import BaseModel, EmailStr

router = APIRouter()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# SCHEMA DE LOGIN
class UserLogin(BaseModel):
    email: EmailStr
    senha: str


# FUNÇÕES DE SEGURANÇA
def verificar_senha(senha: str, senha_hash: str):
    return pwd_context.verify(senha, senha_hash)


def criar_token(data: dict):
    to_encode = data.copy()

    expire = datetime.utcnow() + timedelta(minutes=60)

    to_encode.update({"exp": expire})

    return jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM
    )


# LOGIN
@router.post("/login")
def login(user: UserLogin, db: Session = Depends(get_db)):

    usuario = db.query(Usuario).filter(Usuario.email == user.email).first()

    if not usuario or not verificar_senha(user.senha, usuario.senha_hash):
        raise HTTPException(status_code=401, detail="Email ou senha inválidos")

    token_data = {
        "sub": usuario.email,
        "perfil": usuario.perfil
    }

    token = criar_token(token_data)

    return {
        "access_token": token,
        "token_type": "bearer",
        "perfil": usuario.perfil
    }
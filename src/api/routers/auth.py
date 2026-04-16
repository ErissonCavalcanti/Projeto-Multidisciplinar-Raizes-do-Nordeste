from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from src.infrastructure.database import get_db
from src.infrastructure.models import Usuario
from src.core.security import verificar_senha, criar_token
from src.api.schemas.user_schema import UserLogin

router = APIRouter()

@router.post("/login")
def login(dados: UserLogin, db: Session = Depends(get_db)):
    user = db.query(Usuario).filter(Usuario.email == dados.email).first()

    if not user:
        raise HTTPException(status_code=401, detail="Usuário não encontrado")

    if not verificar_senha(dados.senha, user.senha_hash):
        raise HTTPException(status_code=401, detail="Senha inválida")

    token = criar_token({"sub": user.email})

    return {"accessToken": token}
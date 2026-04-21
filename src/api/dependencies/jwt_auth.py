from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt

from src.core.config import settings

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise HTTPException(status_code=401, detail={"error": "TOKEN_INVALIDO", "message": "Token inválido ou expirado.", "details": [], "path": ""})
        return {
            "email": email,
            "id": payload.get("id"),
            "perfil": payload.get("perfil")
        }
    except JWTError:
        raise HTTPException(status_code=401, detail={"error": "TOKEN_INVALIDO", "message": "Token inválido ou expirado.", "details": [], "path": ""})
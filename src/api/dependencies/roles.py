from fastapi import Depends, HTTPException
from src.api.dependencies.jwt_auth import get_current_user

def require_role(role: str):
    def role_checker(user = Depends(get_current_user)):
        if user.get("perfil") != role:
            raise HTTPException(status_code=403, detail="Acesso negado")
        return user
    return role_checker
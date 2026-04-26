"""
Guards de autorização por perfil/role.
Uso: adicionar Depends(requer_perfil(["ADMIN","GERENTE"])) nos endpoints.
"""
from fastapi import Depends, HTTPException
from src.api.dependencies.jwt_auth import get_current_user


def requer_perfil(perfis_permitidos: list):
    """
    Retorna uma dependência que verifica se o utilizador tem um dos perfis permitidos.
    Retorna 403 se não tiver permissão.

    Exemplo de uso:
        @router.post("/produtos", dependencies=[Depends(requer_perfil(["ADMIN","GERENTE"]))])
    """
    def verificar(user=Depends(get_current_user)):
        perfil = user.get("perfil", "")
        if perfil not in perfis_permitidos:
            raise HTTPException(
                status_code=403,
                detail={
                    "error": "PERMISSAO_NEGADA",
                    "message": f"Perfil '{perfil}' não tem permissão para esta operação. Requerido: {perfis_permitidos}",
                    "details": [{"field": "perfil", "issue": f"Requerido: {perfis_permitidos}"}],
                    "path": ""
                }
            )
        return user
    return verificar


# Atalhos prontos para usar
SomenteAdmin          = requer_perfil(["ADMIN"])
AdminOuGerente        = requer_perfil(["ADMIN", "GERENTE"])
AdminGerAtendente     = requer_perfil(["ADMIN", "GERENTE", "ATENDENTE"])
ClienteOuAtendente    = requer_perfil(["CLIENTE", "ATENDENTE"])
CozinhaOuSuperior     = requer_perfil(["COZINHA", "GERENTE", "ADMIN"])
Todos                 = requer_perfil(["ADMIN", "GERENTE", "COZINHA", "ATENDENTE", "CLIENTE"])

# Alias para compatibilidade com código existente
require_role = requer_perfil
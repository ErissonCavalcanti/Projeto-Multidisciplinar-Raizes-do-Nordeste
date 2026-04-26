from typing import List, Optional
from pydantic import BaseModel, validator
from enum import Enum


# ENUMs
class CanalPedido(str, Enum):
    APP = "APP"
    TOTEM = "TOTEM"
    BALCAO = "BALCAO"
    PICKUP = "PICKUP"
    WEB = "WEB"


class StatusPedido(str, Enum):
    AGUARDANDO_PAGAMENTO = "AGUARDANDO_PAGAMENTO"
    RECEBIDO = "RECEBIDO"
    EM_PREPARO = "EM_PREPARO"
    PRONTO = "PRONTO"
    ENTREGUE = "ENTREGUE"
    CANCELADO = "CANCELADO"


# REQUEST SCHEMAS
class ItemPedidoCreate(BaseModel):
    # Aceita tanto camelCase (produtoId) quanto snake_case (produto_id)
    # Pydantic v2 usa model_config; para v1 usa Field com alias
    produto_id: int
    quantidade: int

    class Config:
        populate_by_name = True


class PedidoCreate(BaseModel):
    unidade_id: int
    canalPedido: CanalPedido
    itens: List[ItemPedidoCreate]
    forma_pagamento: str = "MOCK"

    @validator("itens")
    def itens_nao_vazios(cls, v):
        # RN01 — ao menos 1 item obrigatório
        if not v or len(v) == 0:
            raise ValueError("O pedido deve conter ao menos um item.")
        return v

    class Config:
        populate_by_name = True


class AtualizarStatusRequest(BaseModel):
    novoStatus: StatusPedido
    motivo: Optional[str] = None
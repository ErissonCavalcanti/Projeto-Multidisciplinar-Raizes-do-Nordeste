from typing import List
from pydantic import BaseModel
from enum import Enum


# ─── ENUMs ────────────────────────────────────────────────────────────────────
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


# ─── REQUEST SCHEMAS ──────────────────────────────────────────────────────────
class ItemPedidoCreate(BaseModel):
    produto_id: int
    quantidade: int


class PedidoCreate(BaseModel):
    unidade_id: int
    canalPedido: CanalPedido       # ENUM obrigatório — retorna 422 se inválido
    itens: List[ItemPedidoCreate]
    forma_pagamento: str = "MOCK"


class AtualizarStatusRequest(BaseModel):
    novoStatus: StatusPedido
    motivo: str = None
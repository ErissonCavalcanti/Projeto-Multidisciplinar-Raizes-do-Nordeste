from typing import List
from pydantic import BaseModel


class Item(BaseModel):
    produto_id: int
    quantidade: int

class PedidoCreate(BaseModel):
    canalPedido: str
    itens: List[Item]
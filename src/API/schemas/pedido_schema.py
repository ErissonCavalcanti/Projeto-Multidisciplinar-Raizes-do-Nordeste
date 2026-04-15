from pydantic import BaseModel

class PedidoCreate(BaseModel):
    canalPedido: str
    total: float
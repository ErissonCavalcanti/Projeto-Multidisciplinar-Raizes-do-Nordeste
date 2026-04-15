from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from src.infrastructure.database import get_db
from src.infrastructure.models import Pedido
from src.api.schemas.pedido_schema import PedidoCreate

router = APIRouter()

@router.post("/")
def criar_pedido(pedido: PedidoCreate, db: Session = Depends(get_db)):

    novo = Pedido(
        status="AGUARDANDO_PAGAMENTO",
        total=pedido.total,
        canal=pedido.canalPedido
    )

    db.add(novo)
    db.commit()
    db.refresh(novo)

    return novo


@router.get("/{pedido_id}")
def buscar_pedido(pedido_id: int, db: Session = Depends(get_db)):
    return db.query(Pedido).filter(Pedido.id == pedido_id).first()
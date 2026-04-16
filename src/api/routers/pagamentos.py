from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from src.infrastructure.database import get_db
from src.infrastructure.models import Pedido

router = APIRouter()

@router.post("/solicitar")
def pagamento_mock(pedidoId: int, resultado: str, db: Session = Depends(get_db)):

    pedido = db.query(Pedido).filter(Pedido.id == pedidoId).first()

    if not pedido:
        raise HTTPException(status_code=404, detail="Pedido não encontrado")

    if resultado == "APROVADO":
        pedido.status = "RECEBIDO"
    else:
        pedido.status = "AGUARDANDO_PAGAMENTO"

    db.commit()

    return {
        "pedidoId": pedidoId,
        "status": resultado,
        "novoStatusPedido": pedido.status
    }
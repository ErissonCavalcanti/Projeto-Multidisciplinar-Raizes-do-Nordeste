from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from src.infrastructure.models import Estoque

from src.infrastructure.database import get_db
from src.infrastructure.models import Pedido, Produto, ItemPedido
from src.api.schemas.pedido_schema import PedidoCreate
from src.api.dependencies.jwt_auth import get_current_user

router = APIRouter()


@router.post("/")
def criar_pedido(
    pedido: PedidoCreate,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    novo_pedido = Pedido(
        status="AGUARDANDO_PAGAMENTO",
        canal=pedido.canalPedido,
        total=0
    )

    db.add(novo_pedido)
    db.commit()
    db.refresh(novo_pedido)

    total = 0

    for item in pedido.itens:
        produto = db.query(Produto).filter(Produto.id == item.produto_id).first()

        if not produto:
            raise HTTPException(status_code=404, detail=f"Produto {item.produto_id} não encontrado")

        estoque = db.query(Estoque).filter(Estoque.produto_id == item.produto_id).first()

        if not estoque or estoque.quantidade < item.quantidade:
            raise HTTPException(status_code=400, detail="Estoque insuficiente")

        estoque.quantidade -= item.quantidade

        subtotal = produto.preco * item.quantidade
        total += subtotal

        item_db = ItemPedido(
            pedido_id=novo_pedido.id,
            produto_id=produto.id,
            quantidade=item.quantidade,
            preco_unitario=produto.preco
        )

        db.add(item_db)

    novo_pedido.total = total
    db.commit()

    print(f"[LOG] Pedido {novo_pedido.id} criado por {user['email']}")

    return {
        "pedidoId": novo_pedido.id,
        "status": novo_pedido.status,
        "total": total
    }


@router.get("/")
def listar_pedidos(
    status: str = None,
    canal: str = None,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    query = db.query(Pedido)

    if status:
        query = query.filter(Pedido.status == status)

    if canal:
        query = query.filter(Pedido.canal == canal)

    return query.all()


@router.get("/{pedido_id}")
def buscar_pedido(
    pedido_id: int,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    pedido = db.query(Pedido).filter(Pedido.id == pedido_id).first()

    if not pedido:
        raise HTTPException(status_code=404, detail="Pedido não encontrado")

    return pedido


@router.patch("/{pedido_id}/status")
def atualizar_status(
    pedido_id: int,
    novo_status: str,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    pedido = db.query(Pedido).filter(Pedido.id == pedido_id).first()

    if not pedido:
        raise HTTPException(status_code=404, detail="Pedido não encontrado")

    fluxo = [
        "AGUARDANDO_PAGAMENTO",
        "RECEBIDO",
        "EM_PREPARO",
        "PRONTO",
        "ENTREGUE"
    ]

    if novo_status not in fluxo:
        raise HTTPException(status_code=400, detail="Status inválido")

    status_atual_index = fluxo.index(pedido.status)
    novo_index = fluxo.index(novo_status)

    if novo_index < status_atual_index:
        raise HTTPException(status_code=400, detail="Não pode voltar status")

    pedido.status = novo_status
    db.commit()

    print(f"[LOG] Pedido {pedido.id} atualizado para {novo_status}")

    return {
        "pedidoId": pedido.id,
        "novoStatus": pedido.status
    }
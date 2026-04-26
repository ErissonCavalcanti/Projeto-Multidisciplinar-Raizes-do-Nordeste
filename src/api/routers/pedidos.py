from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from datetime import datetime, timedelta

from src.infrastructure.database import get_db
from src.infrastructure.models import (
    Pedido, Produto, ItemPedido, Estoque, Unidade,
    LogAuditoria, Fidelidade, TransacaoFidelidade, Consentimento
)
from src.api.schemas.pedido_schema import PedidoCreate, AtualizarStatusRequest, StatusPedido
from src.api.schemas.error_schema import make_error
from src.api.dependencies.jwt_auth import get_current_user

router = APIRouter()

FLUXO_STATUS = [
    "AGUARDANDO_PAGAMENTO",
    "RECEBIDO",
    "EM_PREPARO",
    "PRONTO",
    "ENTREGUE"
]

PONTOS_POR_REAL = 1   # 1 ponto por R$ gasto


def registrar_log(db: Session, usuario_id, entidade: str, entidade_id: int, acao: str, descricao: str):
    log = LogAuditoria(
        usuario_id=usuario_id,
        entidade=entidade,
        entidade_id=entidade_id,
        acao=acao,
        descricao=descricao,
        criado_em=datetime.utcnow()
    )
    db.add(log)
    db.commit()


def creditar_pontos_fidelidade(db: Session, usuario_id: int, pedido_id: int, total: float):
    """Credita pontos de fidelidade se o usuário tiver consentimento registrado (LGPD)."""
    consentimento = db.query(Consentimento).filter(
        Consentimento.usuario_id == usuario_id,
        Consentimento.tipo == "FIDELIDADE",
        Consentimento.aceito == True
    ).first()
    if not consentimento:
        return   # sem consentimento → sem pontos (RG-LGPD)

    pontos = int(total * PONTOS_POR_REAL)
    if pontos <= 0:
        return

    fidelidade = db.query(Fidelidade).filter(Fidelidade.usuario_id == usuario_id).first()
    if not fidelidade:
        fidelidade = Fidelidade(usuario_id=usuario_id, pontos_acumulados=0, pontos_resgatados=0)
        db.add(fidelidade)
        db.commit()
        db.refresh(fidelidade)

    fidelidade.pontos_acumulados += pontos
    transacao = TransacaoFidelidade(
        fidelidade_id=fidelidade.id,
        pedido_id=pedido_id,
        tipo="CREDITO",
        pontos=pontos,
        descricao=f"Pedido #{pedido_id} — R$ {total:.2f}",
        criado_em=datetime.utcnow()
    )
    db.add(transacao)
    db.commit()


# POST /pedidos
@router.post("/", status_code=201)
def criar_pedido(
    pedido: PedidoCreate,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    # RN01 — ao menos 1 item
    if not pedido.itens or len(pedido.itens) == 0:
        raise HTTPException(
            status_code=422,
            detail=make_error("PEDIDO_SEM_ITENS", "O pedido deve conter ao menos um item.", "/pedidos",
                              [{"field": "itens", "issue": "Lista não pode ser vazia"}])
        )

    # RN04 — idempotência: pedido duplicado nos últimos 60 segundos
    janela = datetime.utcnow() - timedelta(seconds=60)
    pedido_recente = db.query(Pedido).filter(
        Pedido.usuario_id == user.get("id"),
        Pedido.unidade_id == pedido.unidade_id,
        Pedido.criado_em >= janela
    ).first()
    if pedido_recente:
        raise HTTPException(
            status_code=409,
            detail=make_error("PEDIDO_DUPLICADO",
                              "Pedido idêntico já realizado nos últimos 60 segundos.",
                              "/pedidos",
                              [{"field": "pedidoId", "issue": f"Pedido existente: #{pedido_recente.id}"}])
        )

    # Valida unidade
    unidade = db.query(Unidade).filter(Unidade.id == pedido.unidade_id, Unidade.ativo == True).first()
    if not unidade:
        raise HTTPException(
            status_code=404,
            detail=make_error("UNIDADE_NAO_ENCONTRADA", "Unidade não encontrada ou inativa.", "/pedidos")
        )

    # Valida produtos e estoque (não desconta ainda — RN UC-03 fluxo 6 ocorre após pagamento aprovado)
    erros_estoque = []
    itens_validados = []
    for item in pedido.itens:
        produto = db.query(Produto).filter(Produto.id == item.produto_id, Produto.ativo == True).first()
        if not produto:
            raise HTTPException(
                status_code=404,
                detail=make_error("PRODUTO_NAO_ENCONTRADO",
                                  f"Produto {item.produto_id} não encontrado.",
                                  "/pedidos",
                                  [{"field": "itens[].produto_id", "issue": f"ID {item.produto_id} inexistente"}])
            )
        estoque = db.query(Estoque).filter(
            Estoque.produto_id == item.produto_id,
            Estoque.unidade_id == pedido.unidade_id
        ).first()
        if not estoque or estoque.quantidade < item.quantidade:
            disponivel = estoque.quantidade if estoque else 0
            erros_estoque.append({"field": f"itens[{item.produto_id}].quantidade", "issue": f"Disponível: {disponivel}"})
        else:
            itens_validados.append((item, produto, estoque))

    if erros_estoque:
        raise HTTPException(
            status_code=409,
            detail=make_error("ESTOQUE_INSUFICIENTE", "Quantidade insuficiente para um ou mais itens.", "/pedidos", erros_estoque)
        )

    # Calcula total
    total = round(sum(p.preco_base * i.quantidade for i, p, _ in itens_validados), 2)

    # Cria pedido — estoque ainda NÃO descontado (será descontado após pagamento aprovado)
    novo_pedido = Pedido(
        unidade_id=pedido.unidade_id,
        usuario_id=user.get("id"),
        canal_pedido=pedido.canalPedido.value,
        status="AGUARDANDO_PAGAMENTO",
        total=total,
        criado_em=datetime.utcnow()
    )
    db.add(novo_pedido)
    db.commit()
    db.refresh(novo_pedido)

    # Cria itens do pedido
    itens_response = []
    for item, produto, _ in itens_validados:
        item_db = ItemPedido(
            pedido_id=novo_pedido.id,
            produto_id=produto.id,
            quantidade=item.quantidade,
            preco_unitario=produto.preco_base
        )
        db.add(item_db)
        itens_response.append({
            "produtoId": produto.id,
            "quantidade": item.quantidade,
            "precoUnitario": produto.preco_base
        })

    db.commit()

    registrar_log(db, user.get("id"), "pedido", novo_pedido.id, "CRIACAO",
                  f"Pedido criado via {pedido.canalPedido.value} — total R$ {total}")

    return {
        "pedidoId": novo_pedido.id,
        "status": novo_pedido.status,
        "canalPedido": novo_pedido.canal_pedido,
        "total": novo_pedido.total,
        "itens": itens_response,
        "createdAt": novo_pedido.criado_em.isoformat() + "Z"
    }


# GET /pedidos
@router.get("/")
def listar_pedidos(
    status: str = Query(None),
    canalPedido: str = Query(None),
    unidade_id: int = Query(None),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    query = db.query(Pedido)
    if status:       query = query.filter(Pedido.status == status)
    if canalPedido:  query = query.filter(Pedido.canal_pedido == canalPedido)
    if unidade_id:   query = query.filter(Pedido.unidade_id == unidade_id)

    total_registros = query.count()
    pedidos = query.offset((page - 1) * limit).limit(limit).all()

    return {
        "data": [{
            "pedidoId": p.id,
            "status": p.status,
            "canalPedido": p.canal_pedido,
            "total": p.total,
            "unidade_id": p.unidade_id,
            "criadoEm": p.criado_em.isoformat() + "Z" if p.criado_em else None
        } for p in pedidos],
        "pagination": {
            "page": page, "limit": limit,
            "total": total_registros,
            "pages": (total_registros + limit - 1) // limit
        }
    }


#  GET /pedidos/{id}
@router.get("/{pedido_id}")
def buscar_pedido(pedido_id: int, db: Session = Depends(get_db), user=Depends(get_current_user)):
    pedido = db.query(Pedido).filter(Pedido.id == pedido_id).first()
    if not pedido:
        raise HTTPException(status_code=404,
            detail=make_error("PEDIDO_NAO_ENCONTRADO", "Pedido não encontrado.", f"/pedidos/{pedido_id}"))
    itens = db.query(ItemPedido).filter(ItemPedido.pedido_id == pedido_id).all()
    return {
        "pedidoId": pedido.id,
        "status": pedido.status,
        "canalPedido": pedido.canal_pedido,
        "total": pedido.total,
        "unidade_id": pedido.unidade_id,
        "itens": [{"produtoId": i.produto_id, "quantidade": i.quantidade, "precoUnitario": i.preco_unitario} for i in itens],
        "criadoEm": pedido.criado_em.isoformat() + "Z" if pedido.criado_em else None
    }


# PATCH /pedidos/{id}/status
@router.patch("/{pedido_id}/status")
def atualizar_status(
    pedido_id: int,
    body: AtualizarStatusRequest,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    pedido = db.query(Pedido).filter(Pedido.id == pedido_id).first()
    if not pedido:
        raise HTTPException(status_code=404,
            detail=make_error("PEDIDO_NAO_ENCONTRADO", "Pedido não encontrado.", f"/pedidos/{pedido_id}/status"))

    novo_status = body.novoStatus.value
    status_anterior = pedido.status

    if novo_status == "CANCELADO":
        if pedido.status == "ENTREGUE":
            raise HTTPException(status_code=409,
                detail=make_error("STATUS_INVALIDO", "Pedido já entregue não pode ser cancelado.", f"/pedidos/{pedido_id}/status"))
    else:
        idx_atual = FLUXO_STATUS.index(pedido.status) if pedido.status in FLUXO_STATUS else -1
        idx_novo  = FLUXO_STATUS.index(novo_status) if novo_status in FLUXO_STATUS else -1
        if idx_novo < 0:
            raise HTTPException(status_code=400,
                detail=make_error("STATUS_INVALIDO", "Status inválido.", f"/pedidos/{pedido_id}/status"))
        if idx_novo <= idx_atual:
            raise HTTPException(status_code=409,
                detail=make_error("STATUS_INVALIDO",
                    f"Não é possível retroceder o status de '{pedido.status}' para '{novo_status}'.",
                    f"/pedidos/{pedido_id}/status"))

    pedido.status = novo_status
    pedido.atualizado_em = datetime.utcnow()
    db.commit()

    registrar_log(db, user.get("id"), "pedido", pedido.id, "STATUS_ATUALIZADO",
                  f"Status alterado de {status_anterior} para {novo_status}. Motivo: {body.motivo or 'não informado'}")

    return {
        "pedidoId": pedido.id,
        "statusAnterior": status_anterior,
        "novoStatus": pedido.status,
        "atualizadoEm": pedido.atualizado_em.isoformat() + "Z"
    }
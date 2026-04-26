from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from datetime import datetime
import json

from src.infrastructure.database import get_db
from src.infrastructure.models import Pedido, Pagamento, LogAuditoria, ItemPedido, Estoque
from src.api.schemas.error_schema import make_error
from src.api.dependencies.jwt_auth import get_current_user
from src.api.services.fidelidade_service import creditar_pontos

router = APIRouter()


class PagamentoMockRequest(BaseModel):
    pedidoId: int
    formaPagamento: str = "MOCK"
    simularResultado: str = "APROVADO"


@router.post("/solicitar")
def pagamento_mock(
    body: PagamentoMockRequest,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    pedido = db.query(Pedido).filter(Pedido.id == body.pedidoId).first()

    if not pedido:
        raise HTTPException(
            status_code=404,
            detail=make_error(
                "PEDIDO_NAO_ENCONTRADO",
                "Pedido não encontrado.",
                "/pagamentos/solicitar"
            )
        )

    if pedido.status != "AGUARDANDO_PAGAMENTO":
        raise HTTPException(
            status_code=409,
            detail=make_error(
                "PAGAMENTO_JA_PROCESSADO",
                f"Pedido está com status '{pedido.status}', não aceita pagamento.",
                "/pagamentos/solicitar"
            )
        )

    resultado = body.simularResultado.upper()

    if resultado not in ("APROVADO", "RECUSADO"):
        raise HTTPException(
            status_code=422,
            detail=make_error(
                "RESULTADO_INVALIDO",
                "simularResultado deve ser APROVADO ou RECUSADO.",
                "/pagamentos/solicitar",
                [
                    {
                        "field": "simularResultado",
                        "issue": "Valor inválido"
                    }
                ]
            )
        )

    payload_req = json.dumps({
        "pedidoId": body.pedidoId,
        "valor": pedido.total,
        "formaPagamento": body.formaPagamento
    })

    payload_resp = json.dumps({
        "status": resultado,
        "transacaoId": f"MOCK-{pedido.id}-{datetime.utcnow().timestamp()}"
    })

    pagamento = Pagamento(
        pedido_id=pedido.id,
        forma_pagamento=body.formaPagamento,
        status_pagamento=resultado,
        payload_request=payload_req,
        payload_response=payload_resp,
        criado_em=datetime.utcnow()
    )

    db.add(pagamento)

    if resultado == "APROVADO":

        itens = db.query(ItemPedido).filter(
            ItemPedido.pedido_id == pedido.id
        ).all()

        erros_estoque = []

        for item in itens:
            est = db.query(Estoque).filter(
                Estoque.produto_id == item.produto_id,
                Estoque.unidade_id == pedido.unidade_id
            ).first()

            if not est or est.quantidade < item.quantidade:
                disponivel = est.quantidade if est else 0

                erros_estoque.append({
                    "field": f"produto_id:{item.produto_id}",
                    "issue": f"Disponível: {disponivel}"
                })

        if erros_estoque:
            raise HTTPException(
                status_code=409,
                detail=make_error(
                    "ESTOQUE_INSUFICIENTE",
                    "Estoque insuficiente no momento da confirmação do pagamento.",
                    "/pagamentos/solicitar",
                    erros_estoque
                )
            )

        for item in itens:
            est = db.query(Estoque).filter(
                Estoque.produto_id == item.produto_id,
                Estoque.unidade_id == pedido.unidade_id
            ).first()

            est.quantidade -= item.quantidade

        pedido.status = "RECEBIDO"

        if pedido.usuario_id:
            creditar_pontos(
                db,
                pedido.usuario_id,
                pedido.id,
                pedido.total
            )

    else:
        pedido.status = "AGUARDANDO_PAGAMENTO"

    pedido.atualizado_em = datetime.utcnow()

    log = LogAuditoria(
        usuario_id=user.get("id"),
        entidade="pagamento",
        entidade_id=pedido.id,
        acao="PAGAMENTO_MOCK",
        descricao=f"Resultado: {resultado} — novo status: {pedido.status}",
        criado_em=datetime.utcnow()
    )

    db.add(log)

    db.commit()
    db.refresh(pagamento)

    return {
        "pagamentoId": pagamento.id,
        "pedidoId": body.pedidoId,
        "status": resultado,
        "novoStatusPedido": pedido.status,
        "mensagem": (
            "Pagamento processado com sucesso."
            if resultado == "APROVADO"
            else "Pagamento recusado pelo gateway."
        ),
        "processadoEm": pagamento.criado_em.isoformat() + "Z"
    }


@router.get("/{pedido_id}")
def consultar_pagamento(
    pedido_id: int,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    pagamento = db.query(Pagamento).filter(
        Pagamento.pedido_id == pedido_id
    ).first()

    if not pagamento:
        raise HTTPException(
            status_code=404,
            detail=make_error(
                "PAGAMENTO_NAO_ENCONTRADO",
                "Nenhum pagamento encontrado para este pedido.",
                f"/pagamentos/{pedido_id}"
            )
        )

    return {
        "pagamentoId": pagamento.id,
        "pedidoId": pagamento.pedido_id,
        "formaPagamento": pagamento.forma_pagamento,
        "statusPagamento": pagamento.status_pagamento,
        "criadoEm": pagamento.criado_em.isoformat() + "Z"
    }
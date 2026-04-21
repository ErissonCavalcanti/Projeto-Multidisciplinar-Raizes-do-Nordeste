from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from datetime import datetime
import json

from src.infrastructure.database import get_db
from src.infrastructure.models import Pedido, Pagamento, LogAuditoria
from src.api.schemas.error_schema import make_error
from src.api.dependencies.jwt_auth import get_current_user

router = APIRouter()


class PagamentoMockRequest(BaseModel):
    pedidoId: int
    formaPagamento: str = "MOCK"
    simularResultado: str = "APROVADO"   # APROVADO | RECUSADO


@router.post("/solicitar")
def pagamento_mock(
    body: PagamentoMockRequest,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)      # JWT obrigatório
):
    pedido = db.query(Pedido).filter(Pedido.id == body.pedidoId).first()
    if not pedido:
        raise HTTPException(
            status_code=404,
            detail=make_error("PEDIDO_NAO_ENCONTRADO", "Pedido não encontrado.", "/pagamentos/solicitar")
        )

    if pedido.status != "AGUARDANDO_PAGAMENTO":
        raise HTTPException(
            status_code=409,
            detail=make_error("PAGAMENTO_JA_PROCESSADO", f"Pedido está com status '{pedido.status}', não aceita pagamento.", "/pagamentos/solicitar")
        )

    resultado = body.simularResultado.upper()
    if resultado not in ("APROVADO", "RECUSADO"):
        raise HTTPException(
            status_code=422,
            detail=make_error("RESULTADO_INVALIDO", "simularResultado deve ser APROVADO ou RECUSADO.", "/pagamentos/solicitar",
                              [{"field": "simularResultado", "issue": "Valor inválido"}])
        )

    # Payload simulado da requisição ao gateway externo
    payload_req = json.dumps({"pedidoId": body.pedidoId, "valor": pedido.total, "formaPagamento": body.formaPagamento})
    payload_resp = json.dumps({"status": resultado, "transacaoId": f"MOCK-{pedido.id}-{datetime.utcnow().timestamp()}"})

    # Persiste registo de pagamento
    pagamento = Pagamento(
        pedido_id=pedido.id,
        forma_pagamento=body.formaPagamento,
        status_pagamento=resultado,
        payload_request=payload_req,
        payload_response=payload_resp,
        criado_em=datetime.utcnow()
    )
    db.add(pagamento)

    # Actualiza status do pedido conforme resultado
    novo_status_pedido = "RECEBIDO" if resultado == "APROVADO" else "AGUARDANDO_PAGAMENTO"
    pedido.status = novo_status_pedido
    pedido.atualizado_em = datetime.utcnow()

    # Log de auditoria
    log = LogAuditoria(
        usuario_id=user.get("id"),
        entidade="pagamento",
        entidade_id=pedido.id,
        acao="PAGAMENTO_MOCK",
        descricao=f"Resultado: {resultado} — status do pedido: {novo_status_pedido}",
        criado_em=datetime.utcnow()
    )
    db.add(log)
    db.commit()
    db.refresh(pagamento)

    return {
        "pagamentoId": pagamento.id,
        "pedidoId": body.pedidoId,
        "status": resultado,
        "novoStatusPedido": novo_status_pedido,
        "mensagem": "Pagamento aprovado com sucesso." if resultado == "APROVADO" else "Pagamento recusado pelo gateway.",
        "processadoEm": pagamento.criado_em.isoformat() + "Z"
    }


@router.get("/{pedido_id}")
def consultar_pagamento(
    pedido_id: int,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    pagamento = db.query(Pagamento).filter(Pagamento.pedido_id == pedido_id).first()
    if not pagamento:
        raise HTTPException(
            status_code=404,
            detail=make_error("PAGAMENTO_NAO_ENCONTRADO", "Nenhum pagamento encontrado para este pedido.", f"/pagamentos/{pedido_id}")
        )
    return {
        "pagamentoId": pagamento.id,
        "pedidoId": pagamento.pedido_id,
        "formaPagamento": pagamento.forma_pagamento,
        "statusPagamento": pagamento.status_pagamento,
        "criadoEm": pagamento.criado_em.isoformat() + "Z"
    }
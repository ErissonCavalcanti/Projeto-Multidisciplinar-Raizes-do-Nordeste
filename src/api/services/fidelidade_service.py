"""
Serviço de fidelização — desacoplado dos routers para evitar import circular.
Chamado tanto por pedidos.py (criação) quanto por pagamentos.py (após aprovação).
"""
from sqlalchemy.orm import Session
from datetime import datetime

from src.infrastructure.models import Consentimento, Fidelidade, TransacaoFidelidade

PONTOS_POR_REAL = 1   # 1 ponto para cada R$ 1,00 gasto


def creditar_pontos(db: Session, usuario_id: int, pedido_id: int, total: float):
    """
    Credita pontos de fidelidade somente se o usuário tiver consentimento
    LGPD do tipo FIDELIDADE registrado e aceito (RN-LGPD).
    """
    consentimento = db.query(Consentimento).filter(
        Consentimento.usuario_id == usuario_id,
        Consentimento.tipo == "FIDELIDADE",
        Consentimento.aceito == True
    ).first()

    if not consentimento:
        return  # sem consentimento → sem pontos

    pontos = int(total * PONTOS_POR_REAL)
    if pontos <= 0:
        return

    fidelidade = db.query(Fidelidade).filter(
        Fidelidade.usuario_id == usuario_id
    ).first()

    if not fidelidade:
        fidelidade = Fidelidade(
            usuario_id=usuario_id,
            pontos_acumulados=0,
            pontos_resgatados=0
        )
        db.add(fidelidade)
        db.flush()  # garante id sem fechar a transação

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

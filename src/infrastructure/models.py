from sqlalchemy import Column, Integer, String, Float, ForeignKey, Boolean, DateTime, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from src.infrastructure.database import Base

# USUÁRIO

class Usuario(Base):
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    senha_hash = Column(String, nullable=False)
    perfil = Column(String, nullable=False)          # ADMIN | GERENTE | COZINHA | ATENDENTE | CLIENTE
    ativo = Column(Boolean, default=True)
    criado_em = Column(DateTime, default=datetime.utcnow)


# UNIDADE

class Unidade(Base):
    __tablename__ = "unidades"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String, nullable=False)
    cidade = Column(String, nullable=False)
    estado = Column(String, nullable=False)
    ativo = Column(Boolean, default=True)
    criado_em = Column(DateTime, default=datetime.utcnow)


# PRODUTO

class Produto(Base):
    __tablename__ = "produtos"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String, nullable=False)
    preco = Column(Float, nullable=False)
    categoria = Column(String, default="Geral")
    ativo = Column(Boolean, default=True)

# ESTOQUE  (por unidade)

class Estoque(Base):
    __tablename__ = "estoque"

    id = Column(Integer, primary_key=True, index=True)
    unidade_id = Column(Integer, ForeignKey("unidades.id"), nullable=False)
    produto_id = Column(Integer, ForeignKey("produtos.id"), nullable=False)
    quantidade = Column(Integer, default=0)
    atualizado_em = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


# PEDIDO

class Pedido(Base):
    __tablename__ = "pedidos"

    id = Column(Integer, primary_key=True, index=True)
    unidade_id = Column(Integer, ForeignKey("unidades.id"), nullable=False)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"), nullable=True)
    canal_pedido = Column(String, nullable=False)    # APP | TOTEM | BALCAO | PICKUP | WEB
    status = Column(String, default="AGUARDANDO_PAGAMENTO")
    total = Column(Float, default=0.0)
    criado_em = Column(DateTime, default=datetime.utcnow)
    atualizado_em = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    itens = relationship("ItemPedido", back_populates="pedido")
    pagamento = relationship("Pagamento", back_populates="pedido", uselist=False)



# ITEM DO PEDIDO

class ItemPedido(Base):
    __tablename__ = "itens_pedido"

    id = Column(Integer, primary_key=True, index=True)
    pedido_id = Column(Integer, ForeignKey("pedidos.id"), nullable=False)
    produto_id = Column(Integer, ForeignKey("produtos.id"), nullable=False)
    quantidade = Column(Integer, nullable=False)
    preco_unitario = Column(Float, nullable=False)

    pedido = relationship("Pedido", back_populates="itens")


# PAGAMENTO  (desacoplado do pedido)

class Pagamento(Base):
    __tablename__ = "pagamentos"

    id = Column(Integer, primary_key=True, index=True)
    pedido_id = Column(Integer, ForeignKey("pedidos.id"), unique=True, nullable=False)
    forma_pagamento = Column(String, default="MOCK")
    status_pagamento = Column(String, nullable=False)   # APROVADO | RECUSADO | PENDENTE
    payload_request = Column(Text, nullable=True)
    payload_response = Column(Text, nullable=True)
    criado_em = Column(DateTime, default=datetime.utcnow)

    pedido = relationship("Pedido", back_populates="pagamento")


# FIDELIDADE

class Fidelidade(Base):
    __tablename__ = "fidelidade"

    id = Column(Integer, primary_key=True, index=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"), unique=True, nullable=False)
    pontos_acumulados = Column(Integer, default=0)
    pontos_resgatados = Column(Integer, default=0)
    atualizado_em = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


# LOG DE AUDITORIA

class LogAuditoria(Base):
    __tablename__ = "logs_auditoria"

    id = Column(Integer, primary_key=True, index=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"), nullable=True)
    entidade = Column(String, nullable=False)    # ex: "pedido", "estoque"
    entidade_id = Column(Integer, nullable=True)
    acao = Column(String, nullable=False)        # ex: "CRIACAO", "STATUS_ATUALIZADO"
    descricao = Column(Text, nullable=True)
    criado_em = Column(DateTime, default=datetime.utcnow)
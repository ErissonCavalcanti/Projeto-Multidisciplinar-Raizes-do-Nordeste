from sqlalchemy import Column, Integer, String, Float, ForeignKey, Boolean, DateTime, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from src.infrastructure.database import Base


# USUARIO
class Usuario(Base):
    __tablename__ = "usuarios"

    id            = Column(Integer, primary_key=True, index=True)
    nome          = Column(String, nullable=False)
    email         = Column(String, unique=True, nullable=False)
    senha_hash    = Column(String, nullable=False)
    perfil        = Column(String, nullable=False)   # ADMIN | GERENTE | COZINHA | ATENDENTE | CLIENTE
    ativo         = Column(Boolean, default=True)
    criado_em     = Column(DateTime, default=datetime.utcnow)
    atualizado_em = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


# CONSENTIMENTO LGPD
class Consentimento(Base):
    __tablename__ = "consentimentos"

    id                 = Column(Integer, primary_key=True, index=True)
    usuario_id         = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    tipo               = Column(String, nullable=False)   # ex: FIDELIDADE, MARKETING
    aceito             = Column(Boolean, nullable=False)
    data_consentimento = Column(DateTime, default=datetime.utcnow)


# UNIDADE
class Unidade(Base):
    __tablename__ = "unidades"

    id        = Column(Integer, primary_key=True, index=True)
    nome      = Column(String, nullable=False)
    cnpj      = Column(String, nullable=True)
    endereco  = Column(String, nullable=True)
    cidade    = Column(String, nullable=False)
    estado    = Column(String, nullable=False)
    ativo     = Column(Boolean, default=True)
    criado_em = Column(DateTime, default=datetime.utcnow)


# CATEGORIA
class Categoria(Base):
    __tablename__ = "categorias"

    id        = Column(Integer, primary_key=True, index=True)
    nome      = Column(String, nullable=False)
    descricao = Column(Text, nullable=True)


# PRODUTO
class Produto(Base):
    __tablename__ = "produtos"

    id           = Column(Integer, primary_key=True, index=True)
    nome         = Column(String, nullable=False)
    descricao    = Column(Text, nullable=True)
    preco_base   = Column(Float, nullable=False)
    categoria_id = Column(Integer, ForeignKey("categorias.id"), nullable=True)
    ativo        = Column(Boolean, default=True)

    @property
    def preco(self):
        return self.preco_base


# CARDAPIO POR UNIDADE
class CardapioUnidade(Base):
    __tablename__ = "cardapio_unidade"

    id          = Column(Integer, primary_key=True, index=True)
    unidade_id  = Column(Integer, ForeignKey("unidades.id"), nullable=False)
    produto_id  = Column(Integer, ForeignKey("produtos.id"), nullable=False)
    preco_local = Column(Float, nullable=True)   # sobrescreve preco_base se informado
    disponivel  = Column(Boolean, default=True)


# ESTOQUE (por unidade)
class Estoque(Base):
    __tablename__ = "estoque"

    id            = Column(Integer, primary_key=True, index=True)
    unidade_id    = Column(Integer, ForeignKey("unidades.id"), nullable=False)
    produto_id    = Column(Integer, ForeignKey("produtos.id"), nullable=False)
    quantidade    = Column(Integer, default=0)
    atualizado_em = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


# MOVIMENTACOES DE ESTOQUE
class MovimentacaoEstoque(Base):
    __tablename__ = "movimentacoes_estoque"

    id         = Column(Integer, primary_key=True, index=True)
    estoque_id = Column(Integer, ForeignKey("estoque.id"), nullable=False)
    tipo       = Column(String, nullable=False)   # ENTRADA | SAIDA
    quantidade = Column(Integer, nullable=False)
    motivo     = Column(String, nullable=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"), nullable=True)
    criado_em  = Column(DateTime, default=datetime.utcnow)


# PEDIDO
class Pedido(Base):
    __tablename__ = "pedidos"

    id            = Column(Integer, primary_key=True, index=True)
    unidade_id    = Column(Integer, ForeignKey("unidades.id"), nullable=False)
    usuario_id    = Column(Integer, ForeignKey("usuarios.id"), nullable=True)
    canal_pedido  = Column(String, nullable=False)   # APP | TOTEM | BALCAO | PICKUP | WEB
    status        = Column(String, default="AGUARDANDO_PAGAMENTO")
    total         = Column(Float, default=0.0)
    criado_em     = Column(DateTime, default=datetime.utcnow)
    atualizado_em = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    itens     = relationship("ItemPedido", back_populates="pedido")
    pagamento = relationship("Pagamento", back_populates="pedido", uselist=False)


# ITEM DO PEDIDO
class ItemPedido(Base):
    __tablename__ = "itens_pedido"

    id             = Column(Integer, primary_key=True, index=True)
    pedido_id      = Column(Integer, ForeignKey("pedidos.id"), nullable=False)
    produto_id     = Column(Integer, ForeignKey("produtos.id"), nullable=False)
    quantidade     = Column(Integer, nullable=False)
    preco_unitario = Column(Float, nullable=False)

    pedido = relationship("Pedido", back_populates="itens")


# PAGAMENTO (desacoplado do pedido)
class Pagamento(Base):
    __tablename__ = "pagamentos"

    id               = Column(Integer, primary_key=True, index=True)
    pedido_id        = Column(Integer, ForeignKey("pedidos.id"), unique=True, nullable=False)
    forma_pagamento  = Column(String, default="MOCK")
    status_pagamento = Column(String, nullable=False)   # APROVADO | RECUSADO | PENDENTE
    payload_request  = Column(Text, nullable=True)
    payload_response = Column(Text, nullable=True)
    criado_em        = Column(DateTime, default=datetime.utcnow)

    pedido = relationship("Pedido", back_populates="pagamento")


# FIDELIDADE
class Fidelidade(Base):
    __tablename__ = "fidelidade"

    id                = Column(Integer, primary_key=True, index=True)
    usuario_id        = Column(Integer, ForeignKey("usuarios.id"), unique=True, nullable=False)
    pontos_acumulados = Column(Integer, default=0)
    pontos_resgatados = Column(Integer, default=0)
    atualizado_em     = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    transacoes = relationship("TransacaoFidelidade", back_populates="fidelidade")


# TRANSACOES DE FIDELIDADE
class TransacaoFidelidade(Base):
    __tablename__ = "transacoes_fidelidade"

    id            = Column(Integer, primary_key=True, index=True)
    fidelidade_id = Column(Integer, ForeignKey("fidelidade.id"), nullable=False)
    pedido_id     = Column(Integer, ForeignKey("pedidos.id"), nullable=True)
    tipo          = Column(String, nullable=False)   # CREDITO | DEBITO
    pontos        = Column(Integer, nullable=False)
    descricao     = Column(String, nullable=True)
    criado_em     = Column(DateTime, default=datetime.utcnow)

    fidelidade = relationship("Fidelidade", back_populates="transacoes")


# CAMPANHAS E PROMOCOES
class Campanha(Base):
    __tablename__ = "campanhas"

    id             = Column(Integer, primary_key=True, index=True)
    nome           = Column(String, nullable=False)
    tipo_desconto  = Column(String, nullable=False)   # PERCENTUAL | VALOR_FIXO
    valor_desconto = Column(Float, nullable=False)
    produto_id     = Column(Integer, ForeignKey("produtos.id"), nullable=True)
    categoria_id   = Column(Integer, ForeignKey("categorias.id"), nullable=True)
    unidade_id     = Column(Integer, ForeignKey("unidades.id"), nullable=True)
    inicio         = Column(DateTime, nullable=False)
    fim            = Column(DateTime, nullable=False)
    ativo          = Column(Boolean, default=True)


# LOG DE AUDITORIA
class LogAuditoria(Base):
    __tablename__ = "logs_auditoria"

    id          = Column(Integer, primary_key=True, index=True)
    usuario_id  = Column(Integer, ForeignKey("usuarios.id"), nullable=True)
    entidade    = Column(String, nullable=False)   # ex: pedido, estoque, pagamento
    entidade_id = Column(Integer, nullable=True)
    acao        = Column(String, nullable=False)   # ex: CRIACAO, STATUS_ATUALIZADO
    descricao   = Column(Text, nullable=True)
    criado_em   = Column(DateTime, default=datetime.utcnow)


# TOKENS REVOGADOS (blacklist JWT para logout)
class TokenRevogado(Base):
    __tablename__ = "tokens_revogados"

    id          = Column(Integer, primary_key=True, index=True)
    jti         = Column(String, unique=True, nullable=False)   # JWT ID claim
    usuario_id  = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    revogado_em = Column(DateTime, default=datetime.utcnow)
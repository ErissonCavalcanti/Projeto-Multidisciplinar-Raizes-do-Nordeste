from sqlalchemy import Column, Integer, String, Float
from .database import Base

class Usuario(Base):
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True)
    senha_hash = Column(String)
    perfil = Column(String)


class Pedido(Base):
    __tablename__ = "pedidos"

    id = Column(Integer, primary_key=True, index=True)
    status = Column(String)
    total = Column(Float)
    canal = Column(String)
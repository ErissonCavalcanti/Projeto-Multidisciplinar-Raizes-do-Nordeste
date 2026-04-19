from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel

from src.infrastructure.database import get_db
from src.infrastructure.models import Produto
from src.api.dependencies.roles import require_role

router = APIRouter()


# SCHEMAS
class ProdutoCreate(BaseModel):
    nome: str
    preco: float


class ProdutoResponse(BaseModel):
    id: int
    nome: str
    preco: float

    class Config:
        from_attributes = True


# CRIAR PRODUTO (SÓ ADMIN)
@router.post("/", response_model=ProdutoResponse)
def criar_produto(
    produto: ProdutoCreate,
    db: Session = Depends(get_db),
    user=Depends(require_role("ADMIN"))
):
    novo = Produto(nome=produto.nome, preco=produto.preco)

    db.add(novo)
    db.commit()
    db.refresh(novo)

    return novo


# LISTAR PRODUTOS
@router.get("/", response_model=list[ProdutoResponse])
def listar_produtos(db: Session = Depends(get_db)):
    return db.query(Produto).all()


# BUSCAR PRODUTO
@router.get("/{produto_id}", response_model=ProdutoResponse)
def buscar_produto(produto_id: int, db: Session = Depends(get_db)):
    produto = db.query(Produto).filter(Produto.id == produto_id).first()

    if not produto:
        raise HTTPException(status_code=404, detail="Produto não encontrado")

    return produto


# ATUALIZAR PRODUTO (SÓ ADMIN)
@router.put("/{produto_id}", response_model=ProdutoResponse)
def atualizar_produto(
    produto_id: int,
    dados: ProdutoCreate,
    db: Session = Depends(get_db),
    user=Depends(require_role("ADMIN"))
):
    produto = db.query(Produto).filter(Produto.id == produto_id).first()

    if not produto:
        raise HTTPException(status_code=404, detail="Produto não encontrado")

    produto.nome = dados.nome
    produto.preco = dados.preco

    db.commit()
    db.refresh(produto)

    return produto


# DELETAR PRODUTO (SÓ ADMIN)
@router.delete("/{produto_id}")
def deletar_produto(
    produto_id: int,
    db: Session = Depends(get_db),
    user=Depends(require_role("ADMIN"))
):
    produto = db.query(Produto).filter(Produto.id == produto_id).first()

    if not produto:
        raise HTTPException(status_code=404, detail="Produto não encontrado")

    db.delete(produto)
    db.commit()

    return {"message": "Produto deletado com sucesso"}
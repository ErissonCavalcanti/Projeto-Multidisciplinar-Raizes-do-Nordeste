"""
Seed de dados para demonstração do fluxo completo.
Execute: python -m src.api.seed
"""
from src.infrastructure.database import SessionLocal, Base, engine
from src.infrastructure.models import (
    Usuario, Produto, Estoque, Unidade,
    Pagamento, Pedido, ItemPedido, LogAuditoria
)
from passlib.context import CryptContext

# Cria todas as tabelas antes de inserir dados
Base.metadata.create_all(bind=engine)

pwd_context = CryptContext(schemes=["bcrypt"])
db = SessionLocal()

# Unidade
unidade = db.query(Unidade).filter(Unidade.nome == "Unidade Centro").first()
if not unidade:
    unidade = Unidade(nome="Unidade Centro", cidade="Fortaleza", estado="CE", ativo=True)
    db.add(unidade)
    db.commit()
    db.refresh(unidade)
    print(f"[SEED] Unidade criada: id={unidade.id}")
else:
    print(f"[SEED] Unidade já existe: id={unidade.id}")

unidade_id = unidade.id   # guardar antes de fechar sessão

# Usuários
usuarios_seed = [
    {"nome": "Admin Raízes",    "email": "admin@email.com",    "senha": "Admin@123",   "perfil": "ADMIN"},
    {"nome": "Maria Cliente",   "email": "cliente@teste.com",  "senha": "Teste@123",   "perfil": "CLIENTE"},
    {"nome": "João Cozinha",    "email": "cozinha@teste.com",  "senha": "Cozinha@123", "perfil": "COZINHA"},
    {"nome": "Ana Atendente",   "email": "atendente@teste.com","senha": "Atend@123",   "perfil": "ATENDENTE"},
]

for u in usuarios_seed:
    if not db.query(Usuario).filter(Usuario.email == u["email"]).first():
        novo = Usuario(
            nome=u["nome"],
            email=u["email"],
            senha_hash=pwd_context.hash(u["senha"]),
            perfil=u["perfil"],
            ativo=True
        )
        db.add(novo)
        print(f"[SEED] Usuário criado: {u['email']} ({u['perfil']})")
    else:
        print(f"[SEED] Usuário já existe: {u['email']}")

db.commit()

# Produtos
produtos_seed = [
    {"nome": "Açaí 500ml",         "preco": 12.0,  "categoria": "Açaí"},
    {"nome": "Açaí 1L",            "preco": 20.0,  "categoria": "Açaí"},
    {"nome": "Tapioca Nordestina",  "preco": 8.50,  "categoria": "Salgado"},
    {"nome": "Suco de Cajá 300ml", "preco": 6.0,   "categoria": "Bebida"},
]

for p in produtos_seed:
    if not db.query(Produto).filter(Produto.nome == p["nome"]).first():
        novo = Produto(nome=p["nome"], preco=p["preco"], categoria=p["categoria"], ativo=True)
        db.add(novo)
        print(f"[SEED] Produto criado: {p['nome']}")
    else:
        print(f"[SEED] Produto já existe: {p['nome']}")

db.commit()

# Estoque por unidade
prod_zero_id = None
produtos = db.query(Produto).all()
for prod in produtos:
    existe = db.query(Estoque).filter(
        Estoque.produto_id == prod.id,
        Estoque.unidade_id == unidade_id
    ).first()
    if not existe:
        db.add(Estoque(unidade_id=unidade_id, produto_id=prod.id, quantidade=50))
        print(f"[SEED] Estoque criado: {prod.nome} | qtd=50")
    elif existe.quantidade < 10:
        existe.quantidade = 50

    # Guarda o id do produto sem estoque para T10
    if prod.nome == "Suco de Cajá 300ml":
        prod_zero_id = prod.id

db.commit()

# Zera estoque do Suco de Cajá para o cenário T10
if prod_zero_id:
    est_zero = db.query(Estoque).filter(
        Estoque.produto_id == prod_zero_id,
        Estoque.unidade_id == unidade_id
    ).first()
    if est_zero:
        est_zero.quantidade = 0
        db.commit()
        print(f"[SEED] Estoque zerado para T10: Suco de Cajá 300ml (id={prod_zero_id})")

db.close()

print("\n" + "="*55)
print("  SEED concluído! Dados para usar nos testes:")
print("="*55)
print(f"  Unidade ID   : {unidade_id}")
print("  Admin        : admin@email.com        / Admin@123")
print("  Cliente      : cliente@teste.com      / Teste@123")
print("  Cozinha      : cozinha@teste.com      / Cozinha@123")
print("  Atendente    : atendente@teste.com    / Atend@123")
print("  Produto c/ estoque  : ID 1 (Açaí 500ml)")
print(f"  Produto sem estoque : ID {prod_zero_id} (Suco de Cajá) → usar em T10")
print("="*55)
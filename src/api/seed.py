from src.infrastructure.database import SessionLocal
from src.infrastructure.models import Usuario, Produto, Estoque
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"])

db = SessionLocal()

# cria usuário admin
if not db.query(Usuario).filter(Usuario.email == "admin@email.com").first():
    admin = Usuario(
        email="admin@email.com",
        senha_hash=pwd_context.hash("123456"),
        perfil="ADMIN"
    )
    db.add(admin)

# cria produtos
if not db.query(Produto).first():
    p1 = Produto(nome="Açaí 500ml", preco=12.0)
    p2 = Produto(nome="Açaí 1L", preco=20.0)

    db.add_all([p1, p2])
    db.commit()

    # estoque
    db.add_all([
        Estoque(produto_id=1, quantidade=50),
        Estoque(produto_id=2, quantidade=30)
    ])

db.commit()
db.close()
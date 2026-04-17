from fastapi import FastAPI
from src.infrastructure.database import Base, engine
from src.api.routers import auth, pedidos, pagamentos, produtos

# cria banco
Base.metadata.create_all(bind=engine)

# cria app
app = FastAPI(title=" API Raízes do Nordeste ")

# rotas
app.include_router(auth.router, prefix="/auth", tags=["Auth"])
app.include_router(pedidos.router, prefix="/pedidos", tags=["Pedidos"])
app.include_router(pagamentos.router, prefix="/pagamentos", tags=["Pagamentos"])
app.include_router(produtos.router, prefix="/produtos", tags=["Produtos"])


# rota raiz (opcional)
@app.get("/")
def home():
    return {"message": "API funcionando 🚀"}
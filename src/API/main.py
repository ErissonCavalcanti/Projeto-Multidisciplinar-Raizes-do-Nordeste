from fastapi import FastAPI
from src.infrastructure.database import Base, engine

from src.api.routers import auth, pedidos, pagamentos

Base.metadata.create_all(bind=engine)

app = FastAPI(title="API Raízes do Nordeste")

app.include_router(auth.router, prefix="/auth", tags=["Auth"])
app.include_router(pedidos.router, prefix="/pedidos", tags=["Pedidos"])
app.include_router(pagamentos.router, prefix="/pagamentos", tags=["Pagamentos"])
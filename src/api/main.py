from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.infrastructure.database import Base, engine
from src.api.routers import auth, pedidos, pagamentos, produtos

# Cria todas as tabelas no banco ao iniciar
Base.metadata.create_all(bind=engine)

# Aplicação FastAPI
# Swagger em /api-docs  |  ReDoc em /redoc
app = FastAPI(
    title="API Raízes do Nordeste",
    description=(
        "Backend para gestão de pedidos da Rede de Lanchonetes Raízes do Nordeste. "
        "Projeto Multidisciplinar — Trilha Back-End | UNINTER 2026."
    ),
    version="1.0.0",
    docs_url="/api-docs",
    redoc_url="/redoc",
    contact={
        "name": "Erisson José Cavalcanti da Silva",
        "url": "https://github.com/ErissonCavalcanti/Projeto-Multidisciplinar-Raizes-do-Nordeste",
    },
)

# CORS — permite requisições de qualquer origem em desenvolvimento
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Rotas
app.include_router(auth.router,       prefix="/auth",       tags=["Auth"])
app.include_router(pedidos.router,    prefix="/pedidos",    tags=["Pedidos"])
app.include_router(pagamentos.router, prefix="/pagamentos", tags=["Pagamentos"])
app.include_router(produtos.router,   prefix="/produtos",   tags=["Produtos"])


@app.get("/", tags=["Root"])
def home():
    return {
        "message": "API Raízes do Nordeste funcionando",
        "swagger": "/api-docs",
        "redoc": "/redoc",
        "repositorio": "https://github.com/ErissonCavalcanti/Projeto-Multidisciplinar-Raizes-do-Nordeste"
    }
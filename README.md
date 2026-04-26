# 🍽️ API Raízes do Nordeste

Backend para gestão de pedidos da Rede de Lanchonetes **Raízes do Nordeste**.  
Projeto Multidisciplinar — Trilha Back-End | UNINTER 2026  
**Aluno:** Erisson José Cavalcanti da Silva | **RU:** 4628196

---

## 🚀 Tecnologias

- **FastAPI** — framework web assíncrono
- **SQLAlchemy** — ORM e mapeamento relacional
- **SQLite** — banco de dados local (dev/testes)
- **JWT (python-jose)** — autenticação por token
- **bcrypt (passlib)** — hash seguro de senhas
- **Pydantic** — validação de schemas e ENUMs

---

## 📋 Pré-requisitos

- Python **3.11+**
- pip

---

## ⚙️ Configuração

### 1. Clonar o repositório
```bash
git clone https://github.com/ErissonCavalcanti/Projeto-Multidisciplinar-Raizes-do-Nordeste
cd Projeto-Multidisciplinar-Raizes-do-Nordeste
```

### 2. Criar e activar ambiente virtual
```bash
python -m venv .venv

# Windows
.venv\Scripts\activate

# Linux / Mac
source .venv/bin/activate
```

### 3. Instalar dependências
```bash
pip install -r requirements.txt
```

### 4. Configurar variáveis de ambiente
```bash
# Copiar o ficheiro de exemplo
cp .env.example src/.env

# Editar src/.env e definir uma SECRET_KEY segura:
# SECRET_KEY=coloque_aqui_uma_chave_longa_e_aleatoria
```

> **Gerar chave segura:**
> ```bash
> python -c "import secrets; print(secrets.token_hex(32))"
> ```

### 5. Aplicar seed de dados
```bash
python -m src.api.seed
```
Cria unidade, produtos, estoque e os seguintes utilizadores:

| Perfil | Email | Senha |
|--------|-------|-------|
| ADMIN | admin@email.com | Admin@123 |
| CLIENTE | cliente@teste.com | Teste@123 |
| COZINHA | cozinha@teste.com | Cozinha@123 |
| ATENDENTE | atendente@teste.com | Atend@123 |

### 6. Iniciar a API
```bash
uvicorn src.api.main:app --reload
```

---

## 📄 Documentação (Swagger / OpenAPI)

Após iniciar o servidor:

- **Swagger UI:** http://127.0.0.1:8000/api-docs
- **ReDoc:** http://127.0.0.1:8000/redoc
- Postman: https://documenter.getpostman.com/view/45608718/2sBXqGrMrq
  
---

## 🧪 Testes com Postman

1. Importe o ficheiro `docs/raizes_api_collection.json` no Postman
2. Execute o seed antes de correr os testes
3. Corra as requisições na ordem sugerida (T01 → T12)
4. Os tokens são guardados automaticamente nas variáveis da colecção

**Ordem sugerida:**
```
Auth/T01 (Login CLIENTE) → Auth/Login ADMIN → Auth/Login COZINHA
→ Pedidos/T04 (Criar pedido) → Pagamento/T05 (Mock aprovado)
→ Pedidos/T06 (EM_PREPARO) → Pedidos/T07 (Filtrar por canal)
→ Erros/T02, T03, T09, T10, T11, T12
```

---

## 📁 Estrutura do Projeto

```
raizes-do-nordeste/
├── src/
│   ├── api/
│   │   ├── dependencies/        # JWT auth, roles guard
│   │   ├── routers/             # auth, pedidos, pagamentos, produtos
│   │   ├── schemas/             # Pydantic schemas + ENUMs
│   │   ├── main.py              # FastAPI app
│   │   └── seed.py              # Dados iniciais
│   ├── core/
│   │   ├── config.py            # Settings (.env)
│   │   └── security.py          # Hash / JWT helpers
│   └── infrastructure/
│       ├── database.py          # SQLAlchemy engine
│       └── models.py            # Todos os modelos ORM
├── docs/
│   └── raizes_api_collection.json   # Coleção Postman
├── .env.example
├── requirements.txt
└── README.md
```

---

## 🔗 Endpoints principais

| Método | Rota | Auth | Descrição |
|--------|------|------|-----------|
| POST | /auth/login | público | Login e token JWT |
| GET | /produtos | público | Listar produtos |
| POST | /produtos | ADMIN | Criar produto |
| POST | /pedidos | JWT | Criar pedido (valida estoque + canalPedido) |
| GET | /pedidos?canalPedido=APP | JWT | Listar com filtros |
| GET | /pedidos/{id} | JWT | Detalhe do pedido |
| PATCH | /pedidos/{id}/status | JWT | Actualizar status |
| POST | /pagamentos/solicitar | JWT | Pagamento mock |
| GET | /pagamentos/{pedido_id} | JWT | Consultar pagamento |

---

